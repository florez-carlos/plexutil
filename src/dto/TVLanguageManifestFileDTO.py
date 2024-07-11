from dataclasses import dataclass
from typing import List

from src.dto.TVLanguageManifestDTO import TVLanguageManifestDTO
from src.serializer.Serializable import Serializable


@dataclass(frozen=True)
class TVLanguageManifestFileDTO(Serializable):
    manifests_dto: List[TVLanguageManifestDTO]

    def __eq__(self, other):
        if not isinstance(other, TVLanguageManifestFileDTO):
            return NotImplemented

        return self.manifests_dto == other.manifests_dto

    def __hash__(self):
        return hash(self.manifests_dto)
