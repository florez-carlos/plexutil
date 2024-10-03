class InvalidSchemaError(Exception):
    def __init__(
        self,
        description: str = "",
    ) -> None:
        self.description = description

        super().__init__(description)
