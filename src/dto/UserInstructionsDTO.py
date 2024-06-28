from dataclasses import dataclass
from typing import List

from src.dto.PlexConfigDTO import PlexConfigDTO
from src.enum.FileType import FileType
from src.enum.UserRequest import UserRequest

@dataclass(frozen=True)
class UserInstructionsDTO():

    request: UserRequest
    items: List[str]
    plex_config_dto: PlexConfigDTO


def __eq__(self, other):

    if not isinstance(other, UserInstructionsDTO):
        return NotImplemented

    return self.request == other.request and self.items == other.items and self.plex_config_dto == other.plex_config_dto

def __hash__(self):
    return hash((self.request, self.items, self.plex_config_dto))
