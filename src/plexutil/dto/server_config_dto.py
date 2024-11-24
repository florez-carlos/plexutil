from dataclasses import dataclass


@dataclass(frozen=True)
class ServerConfigDTO:
    host: str = "localhost"
    port: int = 32000
    token: str = ""

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ServerConfigDTO):
            return False

        return (
            self.host == other.host
            and self.port == other.port
            and self.token == other.token
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.host,
                self.port,
                self.token,
            ),
        )
