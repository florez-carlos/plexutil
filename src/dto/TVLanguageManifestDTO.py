from dataclasses import dataclass
from typing import List

from src.enum.Language import Language


@dataclass(frozen=True)
class TVLanguageManifestDTO():

    language: Language
    ids: List[int]

def __eq__(self, other):

    if not isinstance(other, TVLanguageManifestDTO):
        return NotImplemented

    return self.language == other.language\
    and self.ids == other.ids\

def __hash__(self):
    return hash((self.language, self.ids))
