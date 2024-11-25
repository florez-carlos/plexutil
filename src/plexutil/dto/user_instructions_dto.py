from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from plexutil.dto.server_config_dto import ServerConfigDTO
from plexutil.enums.language import Language
from plexutil.enums.library_type import LibraryType

if TYPE_CHECKING:
    from plexutil.enums.user_request import UserRequest


@dataclass(frozen=True)
class UserInstructionsDTO:
    request: UserRequest
    library_type: LibraryType
    library_name: str
    server_config_dto: ServerConfigDTO
    language: Language = Language.ENGLISH_US
    locations: list[Path] = field(default_factory=list)
    items: list[str] = field(default_factory=list)
    is_all_items: bool = False

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UserInstructionsDTO):
            return False

        return (
            self.request == other.request
            and self.library_type == other.library_type
            and self.library_name == other.library_name
            and self.items == other.items
            and self.locations == other.locations
            and self.is_all_items == other.is_all_items
            and self.server_config_dto == other.server_config_dto
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.request,
                self.library_type,
                self.library_name,
                self.items,
                self.locations,
                self.is_all_items,
                self.server_config_dto,
            ),
        )
