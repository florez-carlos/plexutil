from dataclasses import dataclass


@dataclass(frozen=True)
class ServerConfigDTO:
    host: str | None = None
    port: int | None = None
    token: str | None = None

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
