from __future__ import annotations

import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, cast

from plexapi.exceptions import NotFound

from plexutil.core.prompt import Prompt
from plexutil.dto.dropdown_item_dto import DropdownItemDTO
from plexutil.dto.library_setting_dto import LibrarySettingDTO
from plexutil.enums.agent import Agent
from plexutil.enums.language import Language
from plexutil.enums.library_setting import LibrarySetting
from plexutil.enums.scanner import Scanner
from plexutil.enums.user_request import UserRequest
from plexutil.exception.library_illegal_state_error import (
    LibraryIllegalStateError,
)
from plexutil.exception.library_poll_timeout_error import (
    LibraryPollTimeoutError,
)
from plexutil.exception.library_section_missing_error import (
    LibrarySectionMissingError,
)
from plexutil.plex_util_logger import PlexUtilLogger
from plexutil.util.icons import Icons
from plexutil.util.path_ops import PathOps
from plexutil.util.plex_ops import PlexOps

if TYPE_CHECKING:
    from plexapi.audio import Track
    from plexapi.library import (
        LibrarySection,
        MovieSection,
        MusicSection,
        ShowSection,
    )
    from plexapi.server import Playlist, PlexServer
    from plexapi.video import Movie, Show

    from plexutil.dto.bootstrap_paths_dto import BootstrapPathsDTO
    from plexutil.dto.movie_dto import MovieDTO
    from plexutil.dto.song_dto import SongDTO
    from plexutil.dto.tv_series_dto import TVSeriesDTO

from alive_progress import alive_bar

from plexutil.enums.library_type import LibraryType
from plexutil.exception.library_op_error import LibraryOpError
from plexutil.exception.library_unsupported_error import (
    LibraryUnsupportedError,
)


class Library(ABC):
    def __init__(
        self,
        supported_requests: list[UserRequest],
        plex_server: PlexServer,
        name: str,
        library_type: LibraryType,
        agent: Agent,
        scanner: Scanner,
        locations: list[Path],
        language: Language,
        user_request: UserRequest,
        bootstrap_paths_dto: BootstrapPathsDTO,
    ) -> None:
        self.supported_requests = supported_requests
        self.plex_server = plex_server
        self.name = name
        self.library_type = library_type
        self.agent = agent
        self.scanner = scanner
        self.locations = locations
        self.language = language
        self.user_request = user_request
        self.bootstrap_paths_dto = bootstrap_paths_dto

    def do(self) -> None:
        match self.user_request:
            case UserRequest.CREATE:
                self.create()
            case UserRequest.DELETE:
                self.draw_libraries(expect_input=True)
                self.delete()
            case UserRequest.DOWNLOAD:
                self.draw_libraries(expect_input=True)
                self.download()
            case UserRequest.UPLOAD:
                self.draw_libraries(expect_input=True)
                self.upload()
            case UserRequest.DISPLAY:
                self.draw_libraries(expect_input=False)
            case UserRequest.UPDATE:
                self.draw_libraries(expect_input=True)
                section = self.get_section()
                section.update()
                section.refresh()

    @abstractmethod
    def add_item(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete_item(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def download(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def upload(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def create(self) -> None:
        """
        Creates a Library
        Logs a warning if a specific Library Setting is rejected by the server

        Returns:
            None: This method does not return a value

        Raises:
            LibraryOpError: If Library already exists
        """
        op_type = "CREATE"

        self.log_library(operation=op_type, is_info=False, is_debug=True)

        self.assign_name()
        self.error_if_exists()
        self.assign_locations()
        self.assign_scanner()
        self.assign_agent()
        self.assign_language()

        self.plex_server.library.add(
            name=self.name,
            type=self.library_type.get_value(),
            agent=self.agent.get_value(),
            scanner=self.scanner.get_value(),
            location=[str(x) for x in self.locations],  # pyright: ignore [reportArgumentType]
            language=self.language.get_value(),
        )

        description = f"Successfully created: {self.name}"
        PlexUtilLogger.get_logger().debug(description)

        settings = LibrarySetting.get_all(self.library_type)

        library_settings = []

        for setting in settings:
            library_settings.append(  # noqa: PERF401
                LibrarySettingDTO(
                    name=setting.get_name(),
                    display_name=setting.get_display_name(),
                    description=setting.get_description(),
                    user_response=setting.get_default_selection(),
                    is_toggle=setting.is_toggle(),
                    is_value=setting.is_value(),
                    is_dropdown=setting.is_dropdown(),
                    dropdown=setting.get_dropdown(),
                    is_from_server=False,
                )
            )

        self.set_settings(settings=library_settings)
        self.get_section().refresh()

    def assign_language(self) -> None:
        """
        Ask user for Library Language, or use Default in none provided

        Returns:
            None: This method does not return a value.
        """
        self.language = Prompt.confirm_language() or Language.get_default()

    def assign_locations(self) -> None:
        """
        Ask user for Library Locations, or use CWD in none provided

        Returns:
            None: This method does not return a value.
        """
        locations = Prompt.confirm_text(
            "Locations",
            "Type Locations for this Library, separated by comma",
            "Locations",
        )
        if locations:
            self.locations = [Path(location) for location in locations]
        else:
            self.locations = [Path.cwd()]

    def assign_name(self) -> None:
        """
        Ask user for a Library Name or set a Default Name
        if none provided

        Returns:
            None: This method does not return a value.
        """
        text = Prompt.confirm_text(
            "Library Name", "Type a name for the Library", "Library Name"
        )
        self.name = text[0] if text else self.library_type.get_display_name()

    def assign_scanner(self) -> None:
        """
        Ask user for a Scanner

        Returns:
            None: This method does not return a value.
        """
        scanners = Scanner.get_all()
        filtered_scanners = [
            scanner
            for scanner in scanners
            if scanner.is_compatible(self.library_type)
        ]
        dropdown = [
            DropdownItemDTO(
                display_name=filtered_scanner.get_label(),
                value=filtered_scanner,
            )
            for filtered_scanner in filtered_scanners
        ]
        user_response = Prompt.draw_dropdown(
            "Scanner Selection", "Choose a Scanner", dropdown=dropdown
        )

        self.scanner = user_response.value

    def assign_agent(self) -> None:
        """
        Ask user for an Agent

        Returns:
            None: This method does not return a value.
        """
        agents = Agent.get_all()
        filtered_agents = [
            agent for agent in agents if agent.is_compatible(self.library_type)
        ]
        dropdown = [
            DropdownItemDTO(
                display_name=filtered_agent.get_label(self.library_type),
                value=filtered_agent,
            )
            for filtered_agent in filtered_agents
        ]
        user_response = Prompt.draw_dropdown(
            "Agent Selection", "Choose an Agent", dropdown=dropdown
        )
        self.agent = user_response.value

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
        self.log_library(operation=op_type, is_info=False, is_debug=True)

        section = self.get_section()
        try:
            section.delete()
        except LibrarySectionMissingError as e:
            description = f"Does not exist: {section.title}"
            raise LibraryOpError(
                op_type=op_type,
                description=description,
                library_type=self.library_type,
            ) from e

    @abstractmethod
    def exists(self) -> bool:
        """
        Generic LibrarySection Exists

        Returns:
            bool: If LibrarySection exists

        """
        self.log_library(
            operation="CHECK EXISTS", is_info=False, is_debug=True
        )

        library = f"{self.name} | {self.library_type.get_value()}"

        try:
            self.get_section()
        except LibrarySectionMissingError:
            description = f"Does not exist: {library}"
            PlexUtilLogger.get_logger().debug(description)
            return False

        description = f"Exists: {library}"
        PlexUtilLogger.get_logger().debug(description)
        return True

    def error_if_exists(self) -> None:
        op_type = "ERROR IF EXISTS"

        if self.exists():
            description = (
                f"{self.library_type.get_display_name()} with name "
                f"{self.name} already exists"
            )
            raise LibraryOpError(
                op_type=op_type,
                library_type=self.library_type,
                description=description,
            )

    def poll(
        self,
        requested_attempts: int = 0,
        expected_count: int = 0,
        interval_seconds: int = 0,
    ) -> None:
        """
        Performs a query based on the supplied parameters

        Args:
            requested_attempts (int): Amount of times to poll
            expected_count (int): Polling terminates when reaching this amount
            interval_seconds (int): timeout before making a new attempt

        Returns:
            None: This method does not return a value

        Raises:
            LibraryPollTimeoutError: If expected_count not reached
        """
        current_count = len(self.query())
        init_offset = abs(expected_count - current_count)
        time_start = time.time()

        debug = (
            f"\n===== POLL BEGIN =====\n"
            f"Attempts: {requested_attempts!s}\n"
            f"Interval: {interval_seconds!s}\n"
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

                for _ in range(offset):
                    display_count = display_count + 1
                    bar()

                if current_count == expected_count:
                    break

                if current_count > expected_count:
                    time_end = time.time()
                    time_complete = time_end - time_start
                    description = (
                        f"Expected {expected_count!s} items in the library "
                        f"but Plex Server has {current_count!s}\n"
                        f"Failed in {time_complete:.2f}s\n"
                        f"===== POLL END =====\n"
                    )
                    raise LibraryIllegalStateError(description)

                time.sleep(interval_seconds)
                attempts = attempts + 1
                if attempts >= requested_attempts:
                    time_end = time.time()
                    time_complete = time_end - time_start
                    description = (
                        "Did not reach the expected"
                        f"library count: {expected_count!s}\n"
                        f"Failed in {time_complete:.2f}s\n"
                        f"===== POLL END =====\n"
                    )
                    raise LibraryPollTimeoutError(description)

        time_end = time.time()
        time_complete = time_end - time_start
        debug = (
            f"Reached expected: {expected_count!s} in {time_complete:.2f}s\n"
            f"===== POLL END =====\n"
        )

        PlexUtilLogger.get_logger().debug(debug)

    @abstractmethod
    def query(self) -> list[Track] | list[Show] | list[Movie] | list[Playlist]:
        raise NotImplementedError

    def log_library(
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
        library = self.plex_server.library
        library_id = library.key if library else "UNKNOWN"
        info = (
            f"\n===== {self.library_type} | {operation} | BEGIN =====\n"
            f"ID: {library_id}\n"
            f"Name: {self.name}\n"
            f"Type: {self.library_type.get_value()}\n"
            f"Agent: {self.agent.get_value()}\n"
            f"Scanner: {self.scanner.get_value()}\n"
            f"Locations: {self.locations!s}\n"
            f"Language: {self.language.get_value()}\n"
            f"\n===== {self.library_type} | {operation} | END =====\n"
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
        Gets the first occuring Section, does not have conflict resolution

        Returns:
            LibrarySection: A current LibrarySection

        Raises:
            LibrarySectionMissingError: If no library of the same
            type and name exist
        """
        filtered_sections = self.get_sections()

        for filtered_section in filtered_sections:
            if filtered_section.title == self.name:
                return filtered_section

        if self.name:
            description = f"Library not found: {self.name}"
        else:
            description = "Library Name (-libn) not specified, see -h"
        raise LibrarySectionMissingError(description)

    def get_sections(self) -> list[LibrarySection]:
        """
        Gets an up-to-date list of all Sections for this LibraryType

        Returns:
            list[LibrarySection]: A current list of all Sections
            for this LibraryType

        """
        time.sleep(1)  # Slow devices need more time
        sections = self.plex_server.library.sections()

        description = (
            f"Section to find: {self.name} {self.library_type.get_value()}"
        )

        description = f"All Sections: {sections!s}"
        PlexUtilLogger.get_logger().debug(description)

        filtered_sections = [
            section
            for section in sections
            if LibraryType.is_eq(self.library_type, section)
        ]

        description = f"Filtered Sections: {filtered_sections!s}"
        PlexUtilLogger.get_logger().debug(description)
        return filtered_sections

    def __get_local_files(
        self,
    ) -> list[SongDTO] | list[MovieDTO] | list[TVSeriesDTO]:
        """
        Private method to get local files

        Returns:
            [SongDTO | MovieDTO | TVEpisodeDTO]: Local files

        Raises:
            LibraryUnsupportedError: If Library Type not of MUSIC,
            MUSIC_PLAYLIST, TV or MOVIE
        """
        library = self.get_section()

        if LibraryType.is_eq(LibraryType.MUSIC, library) | LibraryType.is_eq(
            LibraryType.MUSIC_PLAYLIST, library
        ):
            local_files = PathOps.get_local_songs(self.locations)
        elif LibraryType.is_eq(LibraryType.TV, library):
            local_files = PathOps.get_local_tv(self.locations)
        elif LibraryType.is_eq(LibraryType.MOVIE, library):
            local_files = PathOps.get_local_movies(self.locations)
        else:
            op_type = "Get Local Files"
            raise LibraryUnsupportedError(
                op_type,
                LibraryType.get_from_section(library),
            )

        return local_files

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
        local_files = self.__get_local_files()
        plex_files = self.query()
        try:
            PlexOps.validate_local_files(plex_files, self.locations)
            description = "Local Files Successfully validated"
            PlexUtilLogger.get_logger().debug(description)
            return
        except LibraryIllegalStateError:
            description = (
                "Plex Server does not match local files\n"
                "A server update is necessary\n"
                "This process may take several minutes\n"
            )
            PlexUtilLogger.get_logger().info(description)

        expected_count = len(local_files)
        self.get_section().update()

        self.poll(100, expected_count, 10)
        plex_files = self.query()
        PlexOps.validate_local_files(plex_files, self.locations)

    def set_settings(self, settings: list[LibrarySettingDTO]) -> None:
        """
        Sets Library Settings
        Logs a warning if setting doesn't exist

        Args:
            settings (LibrarySettingDTO): The Setting to apply to this Library

        Returns:
            None: This method does not return a value
        """
        section = self.get_section()
        for setting in settings:
            response = Prompt.confirm_library_setting(setting)
            try:
                section.editAdvanced(**{response.name: response.user_response})
            except NotFound:
                description = (
                    f"{Icons.WARNING} Library Setting not accepted "
                    f"by the server: {response.name}\n"
                    f"Skipping -> {response.name}:{response.user_response}"
                )
                PlexUtilLogger.get_logger().warning(description)
                continue

    def draw_libraries(self, expect_input: bool = False) -> None:
        sections = self.get_sections()
        dropdown = []
        for section in sections:
            if self.library_type is LibraryType.MOVIE:
                media_count = len(
                    cast("list[MovieSection]", section.searchMovies())
                )
                display_name = f"{section.title} ({media_count!s} Movies)"
            elif self.library_type is LibraryType.TV:
                media_count = len(
                    cast("list[ShowSection]", section.searchShows())
                )
                display_name = f"{section.title} ({media_count!s} Shows)"
            elif (
                self.library_type is LibraryType.MUSIC
                or self.library_type is LibraryType.MUSIC_PLAYLIST
            ):
                media_count = len(
                    cast("list[MusicSection]", section.searchTracks())
                )
                display_name = f"{section.title} ({media_count!s} Tracks)"
            else:
                display_name = ""
            dropdown.append(
                DropdownItemDTO(display_name=display_name, value=section)
            )

        library_type_name = self.library_type.get_display_name()

        user_response = Prompt.draw_dropdown(
            f"{library_type_name}",
            f"Displaying Available {library_type_name} Libraries",
            dropdown=dropdown,
            expect_input=expect_input,
        )

        if expect_input:
            section = user_response.value
            self.name = section.title
            self.agent = Agent.get_from_str(
                candidate=section.agent, library_type=self.library_type
            )
            self.scanner = Scanner.get_from_str(
                candidate=section.scanner, library_type=self.library_type
            )
            self.locations = [
                PathOps.get_path_from_str(location)
                for location in section.locations
            ]
            self.language = Language.get_from_str(section.language)
