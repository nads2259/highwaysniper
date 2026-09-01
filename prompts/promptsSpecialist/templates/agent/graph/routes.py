"""Map lifecycle states to graph nodes. Illegal edges are kernel-enforced."""

from agent_kernel.lifecycle import Lifecycle

STATE_TO_NODE = {
    Lifecycle.RECEIVED: "intake",
    Lifecycle.CONTRACTED: "goal_builder",
    Lifecycle.PLANNING: "planner",
    Lifecycle.PLAN_VALIDATION: "plan_validator",
    Lifecycle.EXECUTING: "executor",
    Lifecycle.STEP_VALIDATION: "step_validator",
    Lifecycle.REPLANNING: "replanner",
    Lifecycle.GOAL_VALIDATION: "goal_validator",
    Lifecycle.COMPLETED: "finalizer",
}
