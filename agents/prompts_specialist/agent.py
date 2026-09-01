from agent_kernel.runtime import Agent, HappyPathNodes


class PromptsSpecialist(Agent):
    """Agent type for authoring agent packages. spawn() once per execution."""

    def __init__(self, **ports: object) -> None:
        super().__init__(name="prompts_specialist", nodes=HappyPathNodes(), ports=ports)
