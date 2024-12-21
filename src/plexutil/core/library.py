from __future__ import annotations

import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

from plexutil.enums.agent import Agent
from plexutil.enums.language import Language
from plexutil.enums.scanner import Scanner
from plexutil.exception.library_illegal_state_error import (
    LibraryIllegalStateError,
)
from plexutil.exception.library_poll_timeout_error import (
    LibraryPollTimeoutError,
)
from plexutil.plex_util_logger import PlexUtilLogger
from plexutil.util.path_ops import PathOps
from plexutil.util.plex_ops import PlexOps

if TYPE_CHECKING:
    from plexapi.audio import Audio, Track
    from plexapi.library import LibrarySection
    from plexapi.server import PlexServer
    from plexapi.video import Movie, Show, Video

    from plexutil.dto.library_preferences_dto import LibraryPreferencesDTO
    from plexutil.dto.local_file_dto import LocalFileDTO
    from plexutil.dto.movie_dto import MovieDTO
    from plexutil.dto.tv_episode_dto import TVEpisodeDTO

from alive_progress import alive_bar

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

        library = None
        try:
            library = self.get_section()
        except LibraryOpError:
            return

        if library:
            self.locations = library.locations
            self.agent = Agent.get_from_str(library.agent)
            self.scanner = Scanner.get_from_str(library.scanner)
            self.locations = [
                PathOps.get_path_from_str(location)
                for location in library.locations
            ]
            self.language = Language.get_from_str(library.language)

    @abstractmethod
    def create(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete(self) -> None:
        """
        Generic Library Delete

        Returns:
            None: This method does not return a value.

        Raises:
            LibraryOpError: If Library isn't found

        """
        op_type = "DELETE"
        self.__log_library(operation=op_type, is_info=True, is_debug=True)

        library = self.get_section()

        if library:
            library.delete()
        else:
            description = "Nothing found"
            raise LibraryOpError(
                op_type=op_type,
                description=description,
                library_type=self.library_type,
            )

    @abstractmethod
    def exists(self) -> bool:
        """
        Generic Library Exists

        Returns:
            bool: If Library exists

        """
        self.__log_library(
            operation="Check Exists", is_info=True, is_debug=True
        )
        return bool(self.get_section())

    def poll(
        self,
        requested_attempts: int = 0,
        expected_count: int = 0,
        interval_seconds: int = 0,
    ) -> None:
        current_count = len(self.query())
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
                updated_current_count = len(self.query())
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

    @abstractmethod
    def query(self) -> list[Video] | list[Audio]:
        raise NotImplementedError

    def __log_library(
        self,
        operation: str,
        is_info: bool = True,
        is_debug: bool = False,
        is_console: bool = False,
    ) -> None:
        """
        Private logging template to be used by methods of this class

        Args:
            opration (str): The type of operation i.e. CREATE DELETE
            is_info (bool): Should it be logged as INFO
            is_debug (bool): Should it be logged as DEBUG
            is_console (bool): Should it be logged with console handler

        Returns:
            None: This method does not return a value.
        """
        info = (
            f"{operation} {self.library_type} library: \n"
            f"ID: {self.library.key if self.library else ''}\n"
            f"Name: {self.name}\n"
            f"Type: {self.library_type.value}\n"
            f"Agent: {self.agent.value}\n"
            f"Scanner: {self.scanner.value}\n"
            f"Locations: {self.locations!s}\n"
            f"Language: {self.language.value}\n"
            f"Movie Preferences: {self.preferences.movie}\n"
            f"Music Preferences: {self.preferences.music}\n"
            f"TV Preferences: {self.preferences.tv}\n"
        )
        if not is_console:
            if is_info:
                PlexUtilLogger.get_logger().info(info)
            if is_debug:
                PlexUtilLogger.get_logger().debug(info)
        else:
            PlexUtilLogger.get_console_logger().info(info)

    def get_section(self) -> LibrarySection:
        """
        Gets an up-to-date Plex Server Library Section

        Returns:
            LibrarySection: A current LibrarySection

        Raises:
            LibraryOpError: If no library of the same type and name exist
        """

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

        description = f"Library: {self.name} does not exist"

        op_type = "GET_LIBRARY"
        raise LibraryOpError(op_type, self.library_type, description)

    def __get_local_files(
        self,
    ) -> list[LocalFileDTO] | list[MovieDTO] | list[TVEpisodeDTO]:
        library = self.get_section()

        if LibraryType.is_eq(LibraryType.MUSIC, library) | LibraryType.is_eq(
            LibraryType.MUSIC_PLAYLIST, library
        ):
            local_files = PathOps.get_local_files(self.locations)
        elif LibraryType.is_eq(LibraryType.TV, library):
            local_files = PathOps.get_local_tv(self.locations)
        elif LibraryType.is_eq(LibraryType.MOVIE, library):
            local_files = PathOps.get_local_movie(self.locations)
        else:
            op_type = "GET_LOCAL_FILES"
            raise LibraryUnsupportedError(
                op_type,
                LibraryType.get_from_section(library),
            )

        return local_files

    def __get_plex_files(self) -> list[Show] | list[Track] | list[Movie]:
        library = self.get_section()

        if LibraryType.is_eq(LibraryType.MUSIC, library) | LibraryType.is_eq(
            LibraryType.MUSIC_PLAYLIST, library
        ):
            plex_files = library.searchTracks()
        elif LibraryType.is_eq(LibraryType.TV, library):
            plex_files = library.searchShows()
        elif LibraryType.is_eq(LibraryType.MOVIE, library):
            plex_files = library.searchMovies()
        else:
            op_type = "GET_PLEX_FILES"
            raise LibraryUnsupportedError(
                op_type,
                LibraryType.get_from_section(library),
            )

        return plex_files

    def probe_library(self) -> None:
        """
        Verifies local files match server files, if not then it issues a
        library update, polls for 1000s or until server matches local files

        Returns:
            None: This method does not return a value.

        Raises:
            LibraryIllegalStateError: If local files do not match server
            LibraryUnsupportedError: If Library Type isn't supported
        """
        library = self.get_section()
        local_files = self.__get_local_files()
        plex_files = self.__get_plex_files()
        try:
            PlexOps.validate_local_files(plex_files, self.locations)
        except LibraryIllegalStateError:
            description = (
                "Plex Server does not match local files\n"
                "A server update is necessary\n"
                "This process may take several minutes\n"
            )
            PlexUtilLogger.get_logger().info(description)
            library.update()

        if LibraryType.is_eq(LibraryType.TV, library):
            episodes = []
            for show in plex_files:
                episodes.extend(show.searchEpisodes())
            expected_count = len(episodes)
        else:
            expected_count = len(local_files)

        self.poll(100, expected_count, 10)
        plex_files = self.__get_plex_files()
        PlexOps.validate_local_files(plex_files, self.locations)
