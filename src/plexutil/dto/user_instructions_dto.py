from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from plexutil.dto.plex_config_dto import PlexConfigDTO
    from plexutil.enums.user_request import UserRequest


@dataclass(frozen=True)
class UserInstructionsDTO:
    request: UserRequest
    items: list[str]
    plex_config_dto: PlexConfigDTO
    is_all_items: bool = False

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UserInstructionsDTO):
            return False

        return (
            self.request == other.request
            and self.items == other.items
            and self.plex_config_dto == other.plex_config_dto
            and self.is_all_items == other.is_all_items
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.request,
                self.items,
                self.plex_config_dto,
                self.is_all_items,
            ),
        )
