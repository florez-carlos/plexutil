from __future__ import annotations

from typing import TYPE_CHECKING

from plexutil.core.prompt import Prompt
from plexutil.dto.dropdown_item_dto import DropdownItemDTO
from plexutil.exception.library_unsupported_error import (
    LibraryUnsupportedError,
)

if TYPE_CHECKING:
    from plexapi.server import PlexServer

    from plexutil.core.library import Library
    from plexutil.dto.bootstrap_paths_dto import BootstrapPathsDTO
    from plexutil.enums.user_request import UserRequest

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
        user_request: UserRequest,
        bootstrap_paths_dto: BootstrapPathsDTO,
    ) -> Library:
        library_types = LibraryType.get_all()
        dropdown = [
            DropdownItemDTO(
                display_name=x.get_display_name(), value=x.get_value()
            )
            for x in library_types
        ]
        response = Prompt.draw_dropdown(
            "Choose the Library Type", "Available Library Types", dropdown
        )
        library_type = response.value

        match library_type:
            case LibraryType.MOVIE:
                library = MovieLibrary(
                    plex_server=plex_server,
                    user_request=user_request,
                    bootstrap_paths_dto=bootstrap_paths_dto,
                )
            case LibraryType.MUSIC:
                library = MusicLibrary(
                    plex_server=plex_server,
                    user_request=user_request,
                    bootstrap_paths_dto=bootstrap_paths_dto,
                )
            case LibraryType.MUSIC_PLAYLIST:
                library = Playlist(
                    plex_server=plex_server,
                    user_request=user_request,
                    bootstrap_paths_dto=bootstrap_paths_dto,
                    playlist_name="",
                )
            case LibraryType.TV:
                library = TVLibrary(
                    plex_server=plex_server,
                    user_request=user_request,
                    bootstrap_paths_dto=bootstrap_paths_dto,
                )
            case _:
                op_type = "Library Factory"
                raise LibraryUnsupportedError(op_type, library_type)
        return library
