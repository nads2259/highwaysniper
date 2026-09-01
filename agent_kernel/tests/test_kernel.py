from agent_kernel.contracts.plan import Plan, PlanStep
from agent_kernel.lifecycle import Lifecycle, assert_transition


def test_plan_detects_cycle() -> None:
    plan = Plan(
        plan_id="p1",
        version=1,
        steps=[
            PlanStep(id="a", objective="a", dependencies=["b"], capability="x", validator="v"),
            PlanStep(id="b", objective="b", dependencies=["a"], capability="x", validator="v"),
        ],
    )
    assert plan.is_acyclic() is False


def test_plan_accepts_dag() -> None:
    plan = Plan(
        plan_id="p1",
        version=1,
        steps=[
            PlanStep(id="a", objective="a", dependencies=[], capability="x", validator="v"),
            PlanStep(id="b", objective="b", dependencies=["a"], capability="x", validator="v"),
        ],
    )
    assert plan.is_acyclic() is True


def test_illegal_transition_is_rejected() -> None:
    try:
        assert_transition(Lifecycle.RECEIVED, Lifecycle.EXECUTING)
    except Exception as exc:
        assert "not allowed" in str(exc)
    else:
        raise AssertionError("expected IllegalTransition")
