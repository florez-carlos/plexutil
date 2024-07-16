from src.dto.tv_language_manifest_dto import TVLanguageManifestDTO
from src.dto.tv_language_manifest_file_dto import TVLanguageManifestFileDTO
from src.enum.language import Language
from src.serializer.serializer import Serializer


class TVLanguageManifestSerializer(Serializer):
    def to_json(self, serializable: TVLanguageManifestDTO) -> dict:
        raise NotImplementedError()

    def to_dto(self, json_dict: dict) -> TVLanguageManifestFileDTO:
        tv_language_manifests_dto = []
        languages = json_dict["languages"]

        for language_dict in languages:
            language_name = language_dict["name"]
            regions = language_dict["regions"]
            for region in regions:
                region_name = region["name"]
                ids = region["tvdbIds"]
                language = Language.get_language_from_str(
                    language_name + "-" + region_name,
                )
                tv_language_manifests_dto.append(
                    TVLanguageManifestDTO(language, ids),
                )

        return TVLanguageManifestFileDTO(tv_language_manifests_dto)
