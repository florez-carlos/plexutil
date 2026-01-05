from __future__ import annotations

from dataclasses import field
from typing import TYPE_CHECKING, cast

from plexutil.dto.dropdown_item_dto import DropdownItemDTO

if TYPE_CHECKING:
    from pathlib import Path

    from plexapi.library import ShowSection
    from plexapi.server import PlexServer
    from plexapi.video import Show

    from plexutil.dto.bootstrap_paths_dto import BootstrapPathsDTO
from plexutil.core.library import Library
from plexutil.core.prompt import Prompt
from plexutil.enums.agent import Agent
from plexutil.enums.language import Language
from plexutil.enums.library_type import LibraryType
from plexutil.enums.scanner import Scanner
from plexutil.enums.user_request import UserRequest
from plexutil.plex_util_logger import PlexUtilLogger


class TVLibrary(Library):
    def __init__(
        self,
        plex_server: PlexServer,
        user_request: UserRequest,
        bootstrap_paths_dto: BootstrapPathsDTO,
        locations: list[Path] = field(default_factory=list),
        agent: Agent = Agent.get_default(LibraryType.TV),
        scanner: Scanner = Scanner.get_default(LibraryType.TV),
        name: str = LibraryType.TV.get_display_name(),
        language: Language = Language.get_default(),
    ) -> None:
        super().__init__(
            supported_requests=[
                UserRequest.CREATE,
                UserRequest.UPDATE,
                UserRequest.DELETE,
                UserRequest.DISPLAY,
            ],
            plex_server=plex_server,
            name=name,
            library_type=LibraryType.TV,
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

    def create(self) -> None:
        super().create()

    def modify_show_language(self) -> None:
        self.probe_library()
        shows = self.query()

        dropdown = [
            DropdownItemDTO(display_name=show.title, value=show)
            for show in shows
        ]

        user_response = Prompt.draw_dropdown(
            title="TV Show Selection",
            description="Pick the Show to modify language",
            dropdown=dropdown,
        )

        show = user_response.value

        language = Prompt.confirm_language()
        show.value.editAdvanced(languageOverride=language.get_value())
        show.refresh()
        description = (
            f"TV Show Language override ({language.value}): {show.title}"
        )
        PlexUtilLogger.get_logger().debug(description)

    def query(self) -> list[Show]:
        op_type = "QUERY"
        self.log_library(operation=op_type, is_info=False, is_debug=True)
        return cast("ShowSection", self.get_section()).searchShows()

    def delete(self) -> None:
        return super().delete()

    def exists(self) -> bool:
        return super().exists()
