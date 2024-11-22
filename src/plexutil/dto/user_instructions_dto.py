from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from plexutil.enums.library_type import LibraryType

if TYPE_CHECKING:
    from plexutil.dto.plex_config_dto import PlexConfigDTO
    from plexutil.enums.user_request import UserRequest


@dataclass(frozen=True)
class UserInstructionsDTO:
    request: UserRequest
    library_type: LibraryType
    items: list[str]
    plex_config_dto: PlexConfigDTO
    is_all_items: bool = False

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UserInstructionsDTO):
            return False

        return (
            self.request == other.request
            and self.library_type == other.library_type
            and self.items == other.items
            and self.plex_config_dto == other.plex_config_dto
            and self.is_all_items == other.is_all_items
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.request,
                self.library_type,
                self.items,
                self.plex_config_dto,
                self.is_all_items,
            ),
        )
