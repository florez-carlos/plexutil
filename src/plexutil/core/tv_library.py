from __future__ import annotations

from typing import TYPE_CHECKING, cast

from plexutil.dto.dropdown_item_dto import DropdownItemDTO
from plexutil.dto.library_setting_dto import LibrarySettingDTO
from plexutil.enums.library_setting import LibrarySetting
from plexutil.exception.library_op_error import LibraryOpError

if TYPE_CHECKING:
    from pathlib import Path

    from plexapi.server import PlexServer
    from plexapi.video import Show

    from plexutil.dto.bootstrap_paths_dto import BootstrapPathsDTO
    from plexutil.enums.user_request import UserRequest


from plexutil.core.library import Library
from plexutil.core.prompt import Prompt
from plexutil.enums.agent import Agent
from plexutil.enums.language import Language
from plexutil.enums.library_name import LibraryName
from plexutil.enums.library_type import LibraryType
from plexutil.enums.scanner import Scanner
from plexutil.plex_util_logger import PlexUtilLogger


class TVLibrary(Library):
    def __init__(
        self,
        plex_server: PlexServer,
        locations: list[Path],
        user_request: UserRequest,
        bootstrap_paths_dto: BootstrapPathsDTO,
        agent: Agent = Agent.get_default(LibraryType.TV),
        scanner: Scanner = Scanner.get_default(LibraryType.TV),
        name: str = LibraryName.TV.value,
        language: Language = Language.get_default(),
    ) -> None:
        super().__init__(
            plex_server,
            name,
            LibraryType.TV,
            agent,
            scanner,
            locations,
            language,
            user_request,
            bootstrap_paths_dto,
        )

    def add_item(self) -> None:
        raise NotImplementedError

    def delete_item(self) -> None:
        raise NotImplementedError

    def download(self) -> None:
        raise NotImplementedError

    def upload(self) -> None:
        raise NotImplementedError

    def create(self) -> None:
        """
        Creates a TV Library
        Logs a warning if a specific tv preference is rejected by the server
        Logs a warning if no TV Preferences available
        This operation is expensive as it waits for all the tv files
        to be recognized by the server

        Returns:
            None: This method does not return a value

        Raises:
            LibraryOpError: If Library already exists
        """
        op_type = "CREATE"

        self.log_library(operation=op_type, is_info=False, is_debug=True)

        if self.exists():
            description = f"TV Library '{self.name}' already exists"
            raise LibraryOpError(
                op_type=op_type,
                library_type=LibraryType.TV,
                description=description,
            )

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

        settings = LibrarySetting.get_all(LibraryType.TV)

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

    def modify_show_language(self) -> None:
        self.probe_library()
        shows = cast("list[Show]", self.get_section().searchShows())
        dropdown = [
            DropdownItemDTO(display_name=show.originalTitle, value=show)
            for show in shows
        ]
        user_response = Prompt.draw_dropdown(
            title="TV Show Selection",
            description="Pick the Show to modify language",
            dropdown=dropdown,
        )

        show = user_response.value

        languages = Language.get_all()
        dropdown = [
            DropdownItemDTO(
                display_name=language.get_display_name(),
                value=language.get_value(),
            )
            for language in languages
        ]
        user_response = Prompt.draw_dropdown(
            title="TV Show Language Selection",
            description=f"Pick the language to set for {show.originalTitle}",
            dropdown=dropdown,
        )

        language = user_response.value

        show.value.editAdvanced(languageOverride=language.get_value())
        show.refresh()
        description = (
            f"TV Show Language override ({language.value}): "
            f"{show.originalTitle}"
        )
        PlexUtilLogger.get_logger().debug(description)

    def query(self) -> list[Show]:
        op_type = "QUERY"
        if not self.exists():
            description = f"TV Library '{self.name}' does not exist"
            raise LibraryOpError(
                op_type=op_type,
                library_type=LibraryType.TV,
                description=description,
            )
        return cast("list[Show]", self.get_section().searchShows())

    def delete(self) -> None:
        return super().delete()

    def exists(self) -> bool:
        return super().exists()
