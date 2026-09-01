from agent_kernel.runtime import Agent


class PromptsSpecialist(Agent):
    """Agent type for authoring agent packages. spawn() once per execution."""

    def __init__(self, **ports: object) -> None:
        super().__init__(name="prompts_specialist", ports=ports)
