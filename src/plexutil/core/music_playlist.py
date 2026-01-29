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
    from plexapi.server import PlexServer

    from plexutil.dto.bootstrap_paths_dto import BootstrapPathsDTO
from plexutil.core.library import Library
from plexutil.dto.music_playlist_dto import MusicPlaylistDTO
from plexutil.enums.agent import Agent
from plexutil.enums.language import Language
from plexutil.enums.library_type import LibraryType
from plexutil.enums.scanner import Scanner
from plexutil.enums.user_request import UserRequest
from plexutil.exception.library_op_error import LibraryOpError
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
        is_strict: bool = False,
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
            is_strict=is_strict,
        )
        self.playlist_name = ""

    def create(self) -> None:
        raise NotImplementedError

    def update(self) -> None:
        raise NotImplementedError

    def modify(self) -> None:
        raise NotImplementedError

    def display(self, expect_input: bool = False) -> None:
        super().display(expect_input=True)
        if (
            self.user_request is UserRequest.DOWNLOAD
            or self.user_request is UserRequest.UPLOAD
        ):
            return
        dropdown = []
        playlists = self.get_section().playlists()
        for playlist in playlists:
            media_count = len(playlist.items())
            display_name = f"{playlist.title} ({media_count!s} items)"
            dropdown.append(
                DropdownItemDTO(display_name=display_name, value=playlist)
            )

        selected_playlist = Prompt.confirm_playlist(
            playlists=playlists,
            library_type=self.library_type,
            expect_input=expect_input,
        )

        if expect_input:
            self.playlist_name = selected_playlist.title

    def query(self) -> list[Track]:
        op_type = "QUERY"
        self.log_library(operation=op_type, is_info=False, is_debug=True)

        return cast("MusicSection", self.get_section()).searchTracks()

    def delete(self) -> None:
        plex_playlists = self.get_section().playlists()

        op_type = "DELETE"
        self.log_library(operation=op_type, is_info=False, is_debug=True)

        for plex_playlist in plex_playlists:
            if plex_playlist.title == self.playlist_name:
                plex_playlist.delete()
                return

        description = f"Playlist not found: {self.playlist_name}"
        raise LibraryOpError(op_type, self.library_type, description)

    def exists(self) -> bool:
        return super().exists()

    def exists_playlist(self) -> bool:
        plex_playlists = self.get_section().playlists()

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

        music_playlist_dtos = self.__get_all_playlists()

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
        )

        section = self.get_section()
        for dto in music_playlist_dtos:
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
            tracks = self.query()
            songs = dto.songs
            known = [
                track
                for track in tracks
                if PlexOps.get_song_dto(track) in songs
            ]
            unknown = [
                PlexOps.get_song_dto(track=track)
                for track in tracks
                if PlexOps.get_song_dto(track) not in songs
            ]
            if unknown:
                description = (
                    f"WARNING: These songs were not found "
                    f"in the plex server library: {self.name}\n"
                )
                for u in unknown:
                    description = description + f"->{u!s}\n"

                PlexUtilLogger.get_logger().warning(description)

            section.createPlaylist(
                title=self.playlist_name,
                items=known,
            )

            description = f"Created Playlist: {self.playlist_name}"
            PlexUtilLogger.get_logger().info(description)

    def __get_all_playlists(self) -> list[MusicPlaylistDTO]:
        """
        Gets ALL Playlists in a Library as a list of MusicPlaylistDTO

        Returns:
            list[MusicPlaylistDTO]: All the playlists in the current Library
        """
        section = self.get_section()
        plex_playlists = section.playlists()

        playlists = []
        for plex_playlist in plex_playlists:
            music_playlist_dto = MusicPlaylistDTO(name=plex_playlist.title)

            for track in plex_playlist.items():
                song_dto = PlexOps.get_song_dto(track)
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
