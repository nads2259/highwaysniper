from agent_kernel.runtime import Agent

__AGENT_ID__ = "__AGENT_ID__"


class __AGENT_CLASS__(Agent):
    """Agent type. spawn() once per execution; 100 runs = 100 instances."""

    def __init__(self, **ports: object) -> None:
        super().__init__(name=__AGENT_ID__, ports=ports)
