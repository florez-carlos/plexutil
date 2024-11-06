from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from plexutil.dto.song_dto import SongDTO
from plexutil.enums.file_type import FileType
from plexutil.static import Static

if TYPE_CHECKING:
    from plexapi.server import PlexServer

    from plexutil.dto.library_preferences_dto import LibraryPreferencesDTO


class PlexOps(Static):
    @staticmethod
    def set_server_settings(
        plex_server: PlexServer,
        library_preferences_dto: LibraryPreferencesDTO,
    ) -> None:
        server_settings = library_preferences_dto.plex_server_settings
        for setting_id, setting_value in server_settings.items():
            plex_server.settings.get(setting_id).set(setting_value)
        plex_server.settings.save()

    @staticmethod
    def get_local_songs(music_folder_path: Path) -> list[SongDTO]:
        songs = []

        for item in Path(music_folder_path).iterdir():
            if item.is_file():
                file_name = item.stem
                file_extension = item.suffix
                songs.append(
                    SongDTO(
                        name=file_name,
                        extension=FileType.get_file_type_from_str(
                            file_extension
                        ),
                    )
                )

        return songs
