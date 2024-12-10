from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from plexutil.dto.server_config_dto import ServerConfigDTO
from plexutil.enums.language import Language

if TYPE_CHECKING:
    from pathlib import Path

    from plexutil.enums.library_type import LibraryType
    from plexutil.enums.user_request import UserRequest


def create_server_config() -> ServerConfigDTO:
    return ServerConfigDTO()


@dataclass(frozen=True)
class UserInstructionsDTO:
    request: UserRequest
    library_type: LibraryType
    library_name: str
    playlist_name: str
    server_config_dto: ServerConfigDTO = field(
        default_factory=create_server_config
    )
    is_show_configuration: bool = False
    is_show_configuration_token: bool = False
    language: Language = Language.ENGLISH_US
    locations: list[Path] = field(default_factory=list)
    songs: list[str] = field(default_factory=list)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UserInstructionsDTO):
            return False

        return (
            self.request == other.request
            and self.library_type == other.library_type
            and self.library_name == other.library_name
            and self.playlist_name == other.playlist_name
            and self.is_show_configuration == other.is_show_configuration
            and self.is_show_configuration_token
            == other.is_show_configuration_token
            and self.language is other.language
            and self.locations == other.locations
            and self.songs == other.songs
            and self.server_config_dto == other.server_config_dto
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.request,
                self.library_type,
                self.library_name,
                self.playlist_name,
                self.server_config_dto,
                self.is_show_configuration,
                self.is_show_configuration_token,
                self.language,
                self.locations,
                self.songs,
            ),
        )
