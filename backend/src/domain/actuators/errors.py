class ActuatorPolicyViolationError(
    RuntimeError
):
    def __init__(
        self,
        message: str,
        policy_name: str,
    ) -> None:
        super().__init__(message)

        self.policy_name = policy_name