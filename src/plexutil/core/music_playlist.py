from __future__ import annotations

from dataclasses import field
from typing import TYPE_CHECKING, cast

from plexutil.core.prompt import Prompt
from plexutil.dto.dropdown_item_dto import DropdownItemDTO
from plexutil.service.music_playlist_service import MusicPlaylistService
from plexutil.service.song_music_playlist_composite_service import (
    SongMusicPlaylistCompositeService,
)
from plexutil.util.icons import Icons

if TYPE_CHECKING:
    from pathlib import Path

    from plexapi.audio import Track
    from plexapi.library import MusicSection
    from plexapi.server import Playlist, PlexServer

    from plexutil.dto.bootstrap_paths_dto import BootstrapPathsDTO
    from plexutil.dto.music_playlist_dto import MusicPlaylistDTO
    from plexutil.dto.song_dto import SongDTO
from plexutil.core.library import Library
from plexutil.enums.agent import Agent
from plexutil.enums.language import Language
from plexutil.enums.library_type import LibraryType
from plexutil.enums.scanner import Scanner
from plexutil.enums.user_request import UserRequest
from plexutil.exception.library_op_error import LibraryOpError
from plexutil.mapper.music_playlist_mapper import MusicPlaylistMapper
from plexutil.plex_util_logger import PlexUtilLogger
from plexutil.util.plex_ops import PlexOps


class MusicPlaylist(Library):
    def __init__(
        self,
        plex_server: PlexServer,
        user_request: UserRequest,
        bootstrap_paths_dto: BootstrapPathsDTO,
        locations: list[Path] = field(default_factory=list),
        name: str = LibraryType.MUSIC_PLAYLIST.get_display_name(),
        library_type: LibraryType = LibraryType.MUSIC_PLAYLIST,
        language: Language = Language.get_default(),
        agent: Agent = Agent.get_default(LibraryType.MUSIC_PLAYLIST),
        scanner: Scanner = Scanner.get_default(LibraryType.MUSIC_PLAYLIST),
    ) -> None:
        super().__init__(
            supported_requests=[
                UserRequest.DELETE,
                UserRequest.DISPLAY,
                UserRequest.UPLOAD,
                UserRequest.DOWNLOAD,
            ],
            plex_server=plex_server,
            name=name,
            library_type=library_type,
            agent=agent,
            scanner=scanner,
            locations=locations,
            language=language,
            user_request=user_request,
            bootstrap_paths_dto=bootstrap_paths_dto,
        )
        self.playlist_name = ""

    def update(self) -> None:
        raise NotImplementedError

    def display(self) -> None:
        op_type = "DISPLAY"
        self.log_library(operation=op_type, is_info=False, is_debug=True)
        self.draw_items(expect_input=False)

    def create(self) -> None:
        raise NotImplementedError

    def query(self) -> list[Track]:
        op_type = "QUERY"
        self.log_library(operation=op_type, is_info=False, is_debug=True)

        return cast("MusicSection", self.get_section()).searchTracks()

    def query_playlists(self) -> list[Playlist]:
        op_type = "QUERY PLAYLISTS"
        self.log_library(operation=op_type, is_info=False, is_debug=True)

        return cast("MusicSection", self.get_section()).playlists()

    def delete(self) -> None:
        op_type = "DELETE"
        plex_playlists = self.get_section().playlists()

        debug = (
            "Received request to delete music playlist: \n"
            f"Playlist: {self.playlist_name}\n"
            f"Location: {self.locations!s}\n"
            f"Playlists available in server: {plex_playlists!s}"
        )
        PlexUtilLogger.get_logger().debug(debug)

        for plex_playlist in plex_playlists:
            if plex_playlist.title == self.playlist_name:
                debug = "Found playlist to delete"
                PlexUtilLogger.get_logger().debug(debug)
                plex_playlist.delete()
                return

        description = (
            f"Playlist not found in server library: {self.playlist_name}"
        )
        raise LibraryOpError(op_type, self.library_type, description)

    def exists(self) -> bool:
        return super().exists()

    def exists_playlist(self) -> bool:
        plex_playlists = self.query_playlists()

        debug = (
            f"Checking playlist exist\n"
            f"Requested: {self.playlist_name}\n"
            f"In server: {plex_playlists!s}\n"
        )
        PlexUtilLogger.get_logger().debug(debug)

        if not plex_playlists or not self.playlist_name:
            return False

        playlist_names = [x.title for x in plex_playlists]
        exists = self.playlist_name in playlist_names

        debug = f"Playlist exists: {exists!s}"
        PlexUtilLogger.get_logger().debug(debug)

        return exists

    def download(self) -> None:
        # Remove existing playlist.db file
        self.bootstrap_paths_dto.plexutil_playlists_db_dir.unlink(
            missing_ok=True
        )

        music_playlist_dtos = self.get_all_playlists()

        service = SongMusicPlaylistCompositeService(
            self.bootstrap_paths_dto.plexutil_playlists_db_dir
        )
        service.add_many(music_playlist_dtos)

    def upload(self) -> None:
        composite_service = SongMusicPlaylistCompositeService(
            self.bootstrap_paths_dto.plexutil_playlists_db_dir
        )
        playlist_service = MusicPlaylistService(
            self.bootstrap_paths_dto.plexutil_playlists_db_dir
        )
        music_playlist_dtos = composite_service.get(
            entities=playlist_service.get_all(),
            tracks=cast("list[Track]", self.query()),
        )

        self.probe_library()
        section = self.get_section()
        for dto in music_playlist_dtos:
            self.songs = dto.songs
            self.playlist_name = dto.name
            self.name = section.title

            if self.exists_playlist():
                info = (
                    f"{Icons.WARNING} Music Playlist: {self.playlist_name} for"
                    f" Library '{self.name}' already exists"
                    f"Skipping create..."
                )
                PlexUtilLogger.get_logger().warning(info)
                continue

            section.createPlaylist(
                title=self.playlist_name,
                items=self.__get_filtered_tracks(),
            )

            description = f"Created Playlist: {self.playlist_name}"
            PlexUtilLogger.get_logger().info(description)

    def get_all_playlists(self) -> list[MusicPlaylistDTO]:
        """
        Gets ALL Playlists in a Library as a list of MusicPlaylistDTO

        Returns:
            list[MusicPlaylistDTO]: All the playlists in the current Library
        """
        music_playlist_mapper = MusicPlaylistMapper()

        section = self.get_section()
        plex_playlists = section.playlists()

        playlists = []
        for plex_playlist in plex_playlists:
            music_playlist_dto = music_playlist_mapper.get_dto(
                PlexOps.get_music_playlist_entity(plex_playlist)
            )

            for track in plex_playlist.items():
                song_dto = cast(
                    "SongDTO", PlexOps.get_dto_from_plex_media(track)
                )
                music_playlist_dto.songs.append(song_dto)

            playlists.append(music_playlist_dto)

        description = f"All Playlists found in {self.name}:\n"
        for playlist in playlists:
            description = (
                description
                + f"->{playlist.name} ({len(playlist.songs)} tracks)\n"
            )
        PlexUtilLogger.get_logger().debug(description)
        return playlists

    def delete_item(self) -> None:
        """
        Matches provided Songs to Plex Tracks in the playlist and deletes
        the tracks from the playlist

        Returns:
            None: This method does not return a value
        """
        filtered_tracks = self.__get_filtered_tracks(is_playlist_tracks=False)
        playlist = self.get_section().playlist(self.playlist_name)
        playlist.removeItems(filtered_tracks)
        description = (
            f"Removed from playlist ({self.playlist_name}): {filtered_tracks}"
        )
        PlexUtilLogger.get_logger().debug(description)

    def add_item(self) -> None:
        """
        Matches provided Songs to Plex Tracks in the library and adds
        the tracks to the plex playlist

        Returns:
            None: This method does not return a value
        """
        self.probe_library()
        filtered_tracks = self.__get_filtered_tracks()
        playlist = self.get_section().playlist(self.playlist_name)
        playlist.addItems(filtered_tracks)
        description = (
            f"Added to playlist ({self.playlist_name}): {filtered_tracks}"
        )
        PlexUtilLogger.get_logger().debug(description)

    def __get_filtered_tracks(
        self, is_playlist_tracks: bool = False
    ) -> list[Track]:
        """
        Filters self.songs of this object against Tracks in the Server

        Args:
            is_playlist_tracks (bool):
                True -> Compare self.songs against this Playlist in the Server
                False -> Compare self.songs against ALL songs in the Library

        Returns:
            list[Track]: Plex Server Tracks that match the SongDTOs
                         in this object's self.songs
        """
        if is_playlist_tracks:
            all_tracks = cast(
                "list[Track]",
                self.get_section().playlist(self.playlist_name).items(),
            )
            if all_tracks is None:
                all_tracks = []

            description = (
                f"Filtering against Playlist: {self.playlist_name}\n"
                f"Songs Supplied: {len(self.songs)!s}\n"
                f"Tracks in Server: {len(all_tracks)!s}\n"
            )
            PlexUtilLogger.get_logger().debug(description)
        else:
            all_tracks = cast("list[Track]", self.get_section().searchTracks())
            if all_tracks is None:
                all_tracks = []
            description = (
                f"Filtering against All tracks in: {self.name}\n"
                f"Songs Supplied: {len(self.songs)!s}\n"
                f"Tracks in Server: {len(all_tracks)!s}\n"
            )
            PlexUtilLogger.get_logger().debug(description)

        known, unknown = PlexOps.filter_plex_media(all_tracks, self.songs)
        if unknown:
            description = (
                f"WARNING: These songs were not found "
                f"in the plex server library: {self.name}\n"
            )
            for u in unknown:
                description = description + f"->{u!s}\n"

            PlexUtilLogger.get_logger().warning(description)

        filtered_tracks = []
        for track in all_tracks:
            dto = PlexOps.get_dto_from_plex_media(track)
            if dto in known:
                filtered_tracks.append(track)

        description = f"Filtered Tracks: {filtered_tracks!s}"
        PlexUtilLogger.get_logger().debug(description)
        return filtered_tracks

    def draw_items(self, expect_input: bool = False) -> None:
        super().draw_libraries(expect_input=True)
        dropdown = []
        playlists = self.query_playlists()
        for playlist in playlists:
            media_count = len(playlist.items())
            display_name = f"{playlist.title} ({media_count!s} items)"
            dropdown.append(
                DropdownItemDTO(display_name=display_name, value=playlist)
            )

        library_type_name = self.library_type.get_display_name()
        user_response = Prompt.draw_dropdown(
            f"{library_type_name}",
            f"Displaying Available {library_type_name}",
            dropdown=dropdown,
            expect_input=expect_input,
        )
        if expect_input:
            self.playlist_name = user_response.value.title
