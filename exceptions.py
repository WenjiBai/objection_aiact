"""
Backend exceptions.

Frontend (B) catches BackendValidationError to roll back to the previous
snapshot and show an error toast.
"""


class BackendValidationError(Exception):
    """Raised when an agent's LLM output fails Pydantic validation twice."""

    def __init__(self, agent: str, errors: list[dict], raw_output: str = ""):
        self.agent = agent
        self.errors = errors
        # Cap raw output to avoid blowing up logs / error toasts.
        self.raw_output = raw_output[:500]
        super().__init__(f"{agent} output failed validation: {errors}")
