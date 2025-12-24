from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from plexapi.server import PlexServer

    from plexutil.core.library import Library
    from plexutil.dto.bootstrap_paths_dto import BootstrapPathsDTO
    from plexutil.dto.user_instructions_dto import UserInstructionsDTO

from plexutil.core.movie_library import MovieLibrary
from plexutil.core.music_library import MusicLibrary
from plexutil.core.playlist import Playlist
from plexutil.core.tv_library import TVLibrary
from plexutil.enums.library_type import LibraryType
from plexutil.static import Static


class LibraryFactory(Static):
    @staticmethod
    def get(
        plex_server: PlexServer,
        user_instructions_dto: UserInstructionsDTO,
        bootstrap_paths_dto: BootstrapPathsDTO,
    ) -> Library:
        library = None

        request = user_instructions_dto.request
        playlist_name = user_instructions_dto.playlist_name
        language = user_instructions_dto.language
        library_name = user_instructions_dto.library_name
        locations = user_instructions_dto.locations
        library_type = user_instructions_dto.library_type

        match library_type:
            case LibraryType.MUSIC:
                library = MusicLibrary(
                    plex_server=plex_server,
                    language=language,
                    name=library_name,
                    locations=locations,
                    user_request=request,
                    bootstrap_paths_dto=bootstrap_paths_dto,
                )
            case LibraryType.MUSIC_PLAYLIST:
                library = Playlist(
                    plex_server=plex_server,
                    language=language,
                    library_type=LibraryType.MUSIC,
                    name=library_name,
                    playlist_name=playlist_name,
                    locations=locations,
                    user_request=request,
                    bootstrap_paths_dto=bootstrap_paths_dto,
                )
            case LibraryType.MOVIE:
                library = MovieLibrary(
                    plex_server=plex_server,
                    language=language,
                    name=library_name,
                    locations=locations,
                    user_request=request,
                    bootstrap_paths_dto=bootstrap_paths_dto,
                )
            case LibraryType.TV:
                library = TVLibrary(
                    plex_server=plex_server,
                    language=language,
                    name=library_name,
                    locations=locations,
                    user_request=request,
                    bootstrap_paths_dto=bootstrap_paths_dto,
                )
        return library
