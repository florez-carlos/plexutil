from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from plexutil.enums.language import Language


@dataclass(frozen=True)
class TVLanguageManifestDTO:
    language: Language
    ids: list[int]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TVLanguageManifestDTO):
            return False

        return self.language == other.language and self.ids == other.ids

    def __hash__(self) -> int:
        return hash((self.language, self.ids))
