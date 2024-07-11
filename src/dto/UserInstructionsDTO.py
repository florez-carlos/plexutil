from dataclasses import dataclass
from typing import List

from src.dto.PlexConfigDTO import PlexConfigDTO
from src.enum.UserRequest import UserRequest

@dataclass(frozen=True)
class UserInstructionsDTO():

    request: UserRequest
    items: List[str]
    plex_config_dto: PlexConfigDTO
    is_all_items: bool = False


def __eq__(self, other):

    if not isinstance(other, UserInstructionsDTO):
        return NotImplemented

    return self.request == other.request and self.items == other.items and self.plex_config_dto == other.plex_config_dto and self.is_all_items == other.is_all_items

def __hash__(self):
    return hash((self.request, self.items, self.plex_config_dto, self.is_all_items))
