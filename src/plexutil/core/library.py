from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from plexutil.exception.library_poll_timeout_error import (
    LibraryPollTimeoutError,
)
from plexutil.plex_util_logger import PlexUtilLogger
from plexutil.util.path_ops import PathOps
from plexutil.util.plex_ops import PlexOps

if TYPE_CHECKING:
    from pathlib import Path

    from plexapi.audio import Audio
    from plexapi.library import LibrarySection
    from plexapi.server import PlexServer
    from plexapi.video import Video

    from plexutil.dto.library_preferences_dto import LibraryPreferencesDTO
    from plexutil.enums.agent import Agent
    from plexutil.enums.language import Language
    from plexutil.enums.scanner import Scanner

from alive_progress import alive_bar
from plexapi.exceptions import NotFound

from plexutil.enums.library_type import LibraryType
from plexutil.exception.library_op_error import LibraryOpError
from plexutil.exception.library_unsupported_error import (
    LibraryUnsupportedError,
)


class Library(ABC):
    def __init__(
        self,
        plex_server: PlexServer,
        name: str,
        library_type: LibraryType,
        agent: Agent,
        scanner: Scanner,
        locations: list[Path],
        language: Language,
        preferences: LibraryPreferencesDTO,
    ) -> None:
        self.plex_server = plex_server
        self.name = name
        self.library_type = library_type
        self.agent = agent
        self.scanner = scanner
        self.locations = locations
        self.language = language
        self.preferences = preferences
        self.library = None

        sections = self.plex_server.library.sections()
        filtered_sections = [
            section
            for section in sections
            if LibraryType.is_eq(self.library_type, section)
        ]

        for filtered_section in filtered_sections:
            if filtered_section.title == self.name:
                self.library = filtered_section
                self.name = self.library.title
                self.library_type = LibraryType.get_from_section(self.library)
                self.locations = self.library.locations

    @abstractmethod
    def create(self) -> None:
        self.__log_library(operation="CREATE", is_info=True, is_debug=True)

        if self.exists():
            description = (
                f"Library {self.name} "
                f"({self.library.key if self.library else ''}) of "
                f"type {self.library_type} already exists"
            )
            raise LibraryOpError(
                op_type="CREATE",
                description=description,
                library_type=self.library_type,
            )

    @abstractmethod
    def delete(self) -> None:
        self.__log_library(operation="DELETE", is_info=True, is_debug=True)

        if self.library:
            self.library.delete()
        else:
            description = "Nothing found"
            raise LibraryOpError(
                op_type="DELETE",
                description=description,
                library_type=self.library_type,
            )

    @abstractmethod
    def exists(self) -> bool:
        self.__log_library(
            operation="Check Exists", is_info=True, is_debug=True
        )
        return bool(self.library)

    def poll(
        self,
        requested_attempts: int = 0,
        expected_count: int = 0,
        interval_seconds: int = 0,
        tvdb_ids: list[int] | None = None,
    ) -> None:
        current_count = len(self.query(tvdb_ids))
        init_offset = abs(expected_count - current_count)

        debug = (
            f"Requested attempts: {requested_attempts!s}\n"
            f"Interval seconds: {interval_seconds!s}\n"
            f"Current count: {current_count!s}\n"
            f"Expected count: {expected_count!s}\n"
            f"Net change: {init_offset!s}\n"
        )

        PlexUtilLogger.get_logger().debug(debug)

        with alive_bar(init_offset) as bar:
            attempts = 0
            display_count = 0
            offset = init_offset

            while attempts < requested_attempts:
                updated_current_count = len(self.query(tvdb_ids))
                offset = abs(updated_current_count - current_count)
                current_count = updated_current_count

                if current_count == expected_count:
                    for _ in range(abs(current_count - display_count)):
                        bar()

                    break

                for _ in range(offset):
                    display_count = display_count + 1
                    bar()

                time.sleep(interval_seconds)
                attempts = attempts + 1
                if attempts >= requested_attempts:
                    raise LibraryPollTimeoutError

    def query(
        self,
        tvdb_ids: list[int] | None = None,
    ) -> list[Audio] | list[Video]:
        op_type = "QUERY"

        if tvdb_ids is None:
            tvdb_ids = []

        try:
            library = self.get_library_or_error("QUERY")
            if self.library_type is LibraryType.MUSIC:
                return library.searchTracks()

            elif self.library_type is LibraryType.TV:
                shows = library.all()
                shows_filtered = []

                if tvdb_ids:
                    for show in shows:
                        guids = show.guids
                        tvdb_prefix = "tvdb://"
                        for guid in guids:
                            if tvdb_prefix in guid.id:
                                tvdb = guid.id.replace(tvdb_prefix, "")
                                if int(tvdb) in tvdb_ids:
                                    shows_filtered.append(show)
                            else:
                                description = (
                                    "Expected ("
                                    + tvdb_prefix
                                    + ") but show does not have any: "
                                    + guid.id
                                )
                                LibraryOpError(
                                    op_type=op_type,
                                    library_type=self.library_type,
                                    description=description,
                                )

                return shows_filtered

            else:
                raise LibraryUnsupportedError(
                    op_type=op_type,
                    library_type=self.library_type,
                )

        except NotFound:
            debug = "Received Not Found on a Query operation"
            PlexUtilLogger.get_logger().debug(debug)
            return []

    def __log_library(
        self,
        operation: str,
        is_info: bool = True,
        is_debug: bool = False,
        is_console: bool = False,
    ) -> None:
        info = (
            f"{operation} {self.library_type} library: \n"
            f"ID: {self.library.key if self.library else ''}\n"
            f"Name: {self.name}\n"
            f"Type: {self.library_type.value}\n"
            f"Agent: {self.agent.value}\n"
            f"Scanner: {self.scanner.value}\n"
            f"Locations: {self.locations!s}\n"
            f"Language: {self.language.value}\n"
            f"Preferences: {self.preferences.movie}\n"
            f"{self.preferences.music}\n"
            f"{self.preferences.tv}\n"
        )
        if not is_console:
            if is_info:
                PlexUtilLogger.get_logger().info(info)
            if is_debug:
                PlexUtilLogger.get_logger().debug(info)
        else:
            PlexUtilLogger.get_console_logger().info(info)

    def get_library_or_error(self, op_type: str) -> LibrarySection:
        sections = self.plex_server.library.sections()
        filtered_sections = [
            section
            for section in sections
            if LibraryType.is_eq(self.library_type, section)
        ]

        for filtered_section in filtered_sections:
            if filtered_section.title == self.name:
                self.library = filtered_section
                return filtered_section

        description = f"Library {self.name} does not exist"

        raise LibraryOpError(op_type, self.library_type, description)

    def verify_and_get_library(self, op_type: str) -> LibrarySection:
        library = self.get_library_or_error(op_type)

        if LibraryType.is_eq(LibraryType.MOVIE, library) or LibraryType.is_eq(
            LibraryType.TV, library
        ):
            raise NotImplementedError

        library.update()
        if LibraryType.is_eq(LibraryType.MUSIC, library) | LibraryType.is_eq(
            LibraryType.MUSIC_PLAYLIST, library
        ):
            local_files = PathOps.get_local_files(self.locations)
            self.poll(100, len(local_files), 10)
            tracks = library.searchTracks()
            PlexOps.validate_local_files(tracks, self.locations)

        return library
