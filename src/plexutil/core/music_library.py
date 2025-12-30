from __future__ import annotations

from dataclasses import field
from typing import TYPE_CHECKING, cast

from plexapi.library import MusicSection

from plexutil.core.prompt import Prompt
from plexutil.dto.dropdown_item_dto import DropdownItemDTO

if TYPE_CHECKING:
    from pathlib import Path

    from plexapi.audio import Track
    from plexapi.server import PlexServer

    from plexutil.dto.bootstrap_paths_dto import BootstrapPathsDTO
from plexutil.core.library import Library
from plexutil.enums.agent import Agent
from plexutil.enums.language import Language
from plexutil.enums.library_name import LibraryName
from plexutil.enums.library_type import LibraryType
from plexutil.enums.scanner import Scanner
from plexutil.enums.user_request import UserRequest
from plexutil.exception.library_op_error import LibraryOpError


class MusicLibrary(Library):
    def __init__(
        self,
        plex_server: PlexServer,
        user_request: UserRequest,
        bootstrap_paths_dto: BootstrapPathsDTO,
        locations: list[Path] = field(default_factory=list),
        agent: Agent = Agent.get_default(LibraryType.MOVIE),
        scanner: Scanner = Scanner.get_default(LibraryType.MOVIE),
        name: str = LibraryName.MUSIC.value,
        language: Language = Language.ENGLISH_US,
    ) -> None:
        super().__init__(
            supported_requests=[
                UserRequest.CREATE,
                UserRequest.DELETE,
                UserRequest.DISPLAY,
            ],
            plex_server=plex_server,
            name=name,
            library_type=LibraryType.MUSIC,
            agent=agent,
            scanner=scanner,
            locations=locations,
            language=language,
            user_request=user_request,
            bootstrap_paths_dto=bootstrap_paths_dto,
        )

    def add_item(self) -> None:
        raise NotImplementedError

    def delete_item(self) -> None:
        raise NotImplementedError

    def download(self) -> None:
        raise NotImplementedError

    def upload(self) -> None:
        raise NotImplementedError

    def update(self) -> None:
        user_response = self.__draw_items(expect_input=True)
        user_response.value.update()
        user_response.value.refresh()

    def display(self) -> None:
        self.__draw_items(expect_input=False)

    def create(self) -> None:
        """
        Creates a Music Library
        This operation is expensive as it waits for all the music files
        to be recognized by the server

        Returns:
            None: This method does not return a value

        Raises:
            LibraryOpError: If Library already exists
            or when failure to create a Query
        """
        super().create()
        # op_type = "CREATE"
        #
        # self.log_library(operation=op_type, is_info=False, is_debug=True)
        #
        # super().assign_name()
        # super().error_if_exists()
        # super().assign_scanner()
        # super().assign_agent()
        #
        # part = ""
        # query_builder = QueryBuilder(
        #     "/library/sections",
        #     name=self.name,
        #     the_type="music",
        #     agent=self.agent.get_value(),
        #     scanner=self.scanner.get_value(),
        #     language=self.language.get_value(),
        #     location=self.locations,
        #     # prefs=self.preferences.music,
        # )
        # part = query_builder.build()
        #
        # description = f"Query: {part}\n"
        # PlexUtilLogger.get_logger().debug(description)
        #
        # # This posts a music library
        # if part:
        #     self.plex_server.query(
        #         part,
        #         method=self.plex_server._session.post,
        #     )
        #     description = f"Successfully created: {self.name}"
        #     PlexUtilLogger.get_logger().debug(description)
        #
        #     settings = LibrarySetting.get_all(LibraryType.MUSIC)
        #     library_settings = []
        #
        #     for setting in settings:
        #         library_settings.append(
        #             LibrarySettingDTO(
        #                 name=setting.get_name(),
        #                 display_name=setting.get_display_name(),
        #                 description=setting.get_description(),
        #                 user_response=setting.get_default_selection(),
        #                 is_toggle=setting.is_toggle(),
        #                 is_value=setting.is_value(),
        #                 is_dropdown=setting.is_dropdown(),
        #                 dropdown=setting.get_dropdown(),
        #                 is_from_server=False,
        #             )
        #         )
        #
        #     super().set_settings(settings=library_settings)
        #     self.get_section().refresh()
        # else:
        #     description = "Malformed Music Query"
        #     raise LibraryOpError(
        #         op_type="CREATE",
        #         library_type=self.library_type,
        #         description=description,
        #     )
        #
        # self.probe_library()

    def query(self) -> list[Track]:
        """
        Returns all tracks for the current LibrarySection

        Returns:
            list[plexapi.audio.Track]: Tracks from the current Section
        """
        op_type = "QUERY"
        if not self.exists():
            description = f"Music Library '{self.name}' does not exist"
            raise LibraryOpError(
                op_type=op_type,
                library_type=LibraryType.MUSIC,
                description=description,
            )

        return cast("list[Track]", self.get_section().searchTracks())

    def delete(self) -> None:
        return super().delete()

    def exists(self) -> bool:
        return super().exists()

    def __draw_items(self, expect_input: bool = False) -> DropdownItemDTO:
        sections = super().get_sections()
        dropdown = []
        for section in sections:
            media_count = len(cast("list[MusicSection]", section.searchTracks()))
            display_name = f"{section.title} ({media_count!s} Tracks)"
            dropdown.append(
                DropdownItemDTO(display_name=display_name, value=section)
            )

        library_type_name = self.library_type.get_display_name()
        return Prompt.draw_dropdown(
            f"{library_type_name}",
            f"Displaying Available {library_type_name} Libraries",
            dropdown=dropdown,
            expect_input=expect_input,
        )
