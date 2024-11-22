from plexutil.dto.song_dto import SongDTO
from plexutil.enums.file_type import FileType
from plexutil.model.song_entity import SongEntity


class SongMapper:

    def get_dto(self, song_entity: SongEntity) -> SongDTO:
        return SongDTO(
            name=str(song_entity.name),
            extension=FileType.get_file_type_from_str(
                    str(song_entity.extension)
            )
        )

    def get_entity(self, song_dto: SongDTO) -> SongEntity:
        return SongEntity(
            name=song_dto.name,
            extension=song_dto.extension.value,
        )
