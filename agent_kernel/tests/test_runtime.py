import asyncio

from agent_kernel.contracts.failure import FailureCategory
from agent_kernel.contracts.failure_envelope import FailureEnvelope
from agent_kernel.contracts.task import (
    AgentRef,
    AgentTaskContract,
    ExecutionContract,
    GoalContract,
)
from agent_kernel.errors import InvalidInputError, LeaseLostError
from agent_kernel.lifecycle import TerminalStatus
from agent_kernel.recovery import RecoveryAction, decide_recovery
from agent_kernel.runtime import Agent
from agents.prompts_specialist.agent import PromptsSpecialist


def _task(task_id: str) -> AgentTaskContract:
    return AgentTaskContract(
        task_id=task_id,
        mission_id="mission-1",
        agent=AgentRef(capability="agent_package_authoring"),
        goal=GoalContract(
            statement="Author a package",
            success_criteria=["tree exists", "kernel imported"],
        ),
        execution=ExecutionContract(idempotency_key=task_id),
        output_schema="AgentPackageAuthoringResultV1",
    )


def test_one_instance_completes() -> None:
    agent = PromptsSpecialist()
    run = agent.spawn()
    result = asyncio.run(run.execute(_task("t-1")))
    assert result.status is TerminalStatus.SUCCEEDED
    assert result.goal_satisfied
    assert run.state.task is not None
    assert run.run_id != agent.spawn().run_id


def test_hundred_isolated_instances() -> None:
    agent = PromptsSpecialist()
    tasks = [_task(f"t-{i}") for i in range(100)]
    runs = [agent.spawn() for _ in tasks]

    async def _all():
        return await asyncio.gather(
            *[run.execute(task) for run, task in zip(runs, tasks, strict=True)]
        )

    results = asyncio.run(_all())
    assert len(results) == 100
    assert all(r.goal_satisfied for r in results)
    assert len({run.run_id for run in runs}) == 100
    assert len({run.state.task.task_id for run in runs if run.state.task}) == 100


def test_agent_execute_spawns_fresh_state() -> None:
    agent = Agent(name="kernel-default")

    async def _both():
        return await asyncio.gather(agent.execute(_task("a")), agent.execute(_task("b")))

    a, b = asyncio.run(_both())
    assert a.goal_satisfied and b.goal_satisfied


def test_recovery_matrix() -> None:
    lease = FailureEnvelope(
        code="lease_lost",
        category=FailureCategory.LEASE_LOSS,
        message="lost",
        retryable=False,
        safe_to_repeat=False,
        compensation_required=False,
    )
    assert decide_recovery(lease) is RecoveryAction.STOP_STALE_WORKER
    policy = FailureEnvelope(
        code="policy",
        category=FailureCategory.POLICY_DENIAL,
        message="denied",
        retryable=False,
        safe_to_repeat=False,
        compensation_required=False,
    )
    assert decide_recovery(policy) is RecoveryAction.STOP
    assert LeaseLostError().to_envelope().category is FailureCategory.LEASE_LOSS
    assert InvalidInputError("x").to_envelope().retryable is False


def test_error_envelope_is_frozen() -> None:
    env = InvalidInputError("bad").to_envelope()
    assert env.model_dump()["code"] == "invalid_input"
