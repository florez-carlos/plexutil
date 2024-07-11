from plexapi.server import PlexServer

from src.Static import Static
from src.dto.LibraryPreferencesDTO import LibraryPreferencesDTO


class PlexOps(Static):
    @staticmethod
    def set_server_settings(
        plex_server: PlexServer, library_preferences_dto: LibraryPreferencesDTO
    ) -> None:
        server_settings = library_preferences_dto.plex_server_settings
        for id, value in server_settings.items():
            plex_server.settings.get(id).set(value)
        plex_server.settings.save()
