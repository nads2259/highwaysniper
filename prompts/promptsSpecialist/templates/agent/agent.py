from agent_kernel.runtime import Agent, AgentRun, HappyPathNodes

__AGENT_ID__ = "__AGENT_ID__"


class __AGENT_CLASS__(Agent):
    """Agent *type*. Call spawn() for each execution; 100 runs = 100 instances."""

    def __init__(self, **ports: object) -> None:
        super().__init__(name=__AGENT_ID__, nodes=HappyPathNodes(), ports=ports)


def build_agent(**ports: object) -> Agent:
    return __AGENT_CLASS__(**ports)
