from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from plexutil.dto.tv_language_manifest_dto import TVLanguageManifestDTO

from serializer.serializable import Serializable


@dataclass(frozen=True)
class TVLanguageManifestFileDTO(Serializable):
    manifests_dto: list[TVLanguageManifestDTO]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TVLanguageManifestFileDTO):
            return False

        return self.manifests_dto == other.manifests_dto

    def __hash__(self) -> int:
        return hash(self.manifests_dto)
