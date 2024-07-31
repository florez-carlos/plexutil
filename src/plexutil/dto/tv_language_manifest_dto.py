from __future__ import annotations

from dataclasses import dataclass, field

from plexutil.enums.language import Language


@dataclass(frozen=True)
class TVLanguageManifestDTO:
    language: Language = Language.ENGLISH_US
    ids: list[int] = field(default_factory=list)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TVLanguageManifestDTO):
            return False

        return self.language == other.language and self.ids == other.ids

    def __hash__(self) -> int:
        return hash((self.language, self.ids))
