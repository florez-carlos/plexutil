from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from plexutil.exception.library_poll_timeout_error import LibraryPollTimeoutError
from plexutil.plex_util_logger import PlexUtilLogger

if TYPE_CHECKING:
    from pathlib import Path

    from plexapi.audio import Audio
    from plexapi.server import PlexServer
    from plexapi.video import Video

    from plexutil.dto.library_preferences_dto import LibraryPreferencesDTO
    from plexutil.enums.agent import Agent
    from plexutil.enums.language import Language
    from plexutil.enums.library_name import LibraryName
    from plexutil.enums.scanner import Scanner

from alive_progress import alive_bar
from plexapi.exceptions import NotFound

from plexutil.enums.library_type import LibraryType
from plexutil.exception.library_op_error import LibraryOpError
from plexutil.exception.library_unsupported_error import LibraryUnsupportedError


class Library(ABC):
    def __init__(
        self,
        plex_server: PlexServer,
        name: LibraryName,
        library_type: LibraryType,
        agent: Agent,
        scanner: Scanner,
        location: Path,
        language: Language,
        preferences: LibraryPreferencesDTO,
    ) -> None:
        self.plex_server = plex_server
        self.name = name
        self.library_type = library_type
        self.agent = agent
        self.scanner = scanner
        self.location = location
        self.language = language
        self.preferences = preferences

    @abstractmethod
    def create(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete(self) -> None:
        op_type = "DELETE"

        info = (
            "Deleting library: \n"
            f"Name: {self.name.value}\n"
            f"Type: {self.library_type.value}\n"
            f"Agent: {self.agent.value}\n"
            f"Scanner: {self.scanner.value}\n"
            f"Location: {self.location!s}\n"
            f"Language: {self.language.value}\n"
            f"Preferences: {self.preferences.music}\n"
        )
        PlexUtilLogger.get_logger().info(info)

        try:
            result = self.plex_server.library.section(self.name.value)

            if result:
                result.delete()
            else:
                description = "Nothing found"
                raise LibraryOpError(
                    op_type=op_type,
                    description=description,
                    library_type=self.library_type,
                )

        except NotFound:
            raise LibraryOpError(
                op_type=op_type,
                library_type=self.library_type,
            ) from NotFound

    @abstractmethod
    def exists(self) -> bool:
        debug = (
            "Checking library exists: \n"
            f"Name: {self.name.value}\n"
            f"Type: {self.library_type.value}\n"
            f"Agent: {self.agent.value}\n"
            f"Scanner: {self.scanner.value}\n"
            f"Location: {self.location!s}\n"
            f"Language: {self.language.value}\n"
            f"Preferences: {self.preferences.movie}\n"
        )
        try:
            result = self.plex_server.library.section(self.name.value)

            if not result:
                debug = debug + "-Not found-"
                PlexUtilLogger.get_logger().debug(debug)
                return False

        except NotFound:
            debug = debug + "-Not found-"
            PlexUtilLogger.get_logger().debug(debug)
            return False

        PlexUtilLogger.get_logger().debug(debug)
        return True

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

        debug = (
            "Performing query:\n"
            f"Name: {self.name.value}\n"
            f"Library Type: {self.library_type.value}\n"
            f"TVDB Ids: {tvdb_ids}\n"
        )
        PlexUtilLogger.get_logger().debug(debug)

        try:
            if self.library_type is LibraryType.MUSIC:
                return self.plex_server.library.section(
                    self.name.value,
                ).searchTracks()

            elif self.library_type is LibraryType.TV:
                shows = self.plex_server.library.section(self.name.value).all()
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
