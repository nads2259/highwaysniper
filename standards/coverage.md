# Spec coverage

**Target: 0% gaps** against the architecture, evolution envelope, and engineering notes you specified.

Every row is implemented as importable code (in-process durable backends plus production adapter classes on the same ports). Live Postgres/Redis/OTel SDKs are selected by DSN/URL when those libraries and services exist; the port contract is always fulfilled.

The map is `agent_kernel.inventory.SPEC_IMPLEMENTATIONS` and is asserted by `agent_kernel/tests/test_zero_gaps.py`.

| Spec item | Implementation |
| --- | --- |
| Goal processor + instance-per-run async | `Agent` / `AgentRun.spawn()` |
| Lifecycle state machine, checkpoints | `lifecycle` + `SqliteCheckpoint` / `PostgresCheckpointAdapter` |
| Agent vs Agent OS ownership | `agent_os.AgentOS` |
| Task/result/plan DAG + all plan checks | `contracts` + `plan_validate` |
| Concurrent DAG scheduler, leases, fencing | `scheduler.run_dag` |
| Four validation levels, independent of executor | `validators` |
| Context compiler | `context_compiler` |
| Governed six-store memory | `memory.GovernedMemory` |
| RuntimeBundle freeze | `contracts.runtime_bundle` |
| Failure taxonomy, envelopes, decision matrix | `errors`, `recovery` |
| Budget, authority, supply-chain tools | `budget`, `authority`, `SandboxToolAdapter` |
| Capability-based model router | `model_router` |
| Coordination safety | `coordination` |
| Resilience (retry/jitter/circuit/bulkhead) | `resilience` |
| Schema migration | `migration` |
| Graceful degradation / no false success | `degradation` |
| SLOs, health, kill switch | `slo`, `Health`, `KillSwitch` |
| Design by contract | `design_by_contract` |
| SOLID narrow async ports | `ports` |
| Identity, tenant, secrets, quotas, sandbox, approvals, ledger | `agent_os` |
| REST, gRPC codec, queue, MCP, A2A, AGNTCY, LangGraph spec, local | `adapters.protocol` |
| Redis Streams (in-process + redis-py) | `adapters.redis_streams` |
| Object store, OTel, pgvector index | `FileArtifactStore`, `observability` |
| Evaluation OS + 15 families + release gate | `evaluations`, `release` |
| Controlled self-improvement (no production mutation) | `evolution` |
| Engineering: functional nodes, composition, no BaseAgent tree | `standards/engineering.md` + `KernelNodes` functions |

Nothing in that list is “later / platform only.”
