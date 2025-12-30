from __future__ import annotations

from dataclasses import field
from typing import TYPE_CHECKING, cast

from plexapi.library import MovieSection

from plexutil.core.prompt import Prompt
from plexutil.dto.dropdown_item_dto import DropdownItemDTO
from plexutil.exception.library_op_error import LibraryOpError

if TYPE_CHECKING:
    from pathlib import Path

    from plexapi.server import PlexServer
    from plexapi.video import Movie

    from plexutil.dto.bootstrap_paths_dto import BootstrapPathsDTO
from plexutil.core.library import Library
from plexutil.enums.agent import Agent
from plexutil.enums.language import Language
from plexutil.enums.library_name import LibraryName
from plexutil.enums.library_type import LibraryType
from plexutil.enums.scanner import Scanner
from plexutil.enums.user_request import UserRequest


class MovieLibrary(Library):
    def __init__(
        self,
        plex_server: PlexServer,
        user_request: UserRequest,
        bootstrap_paths_dto: BootstrapPathsDTO,
        locations: list[Path] = field(default_factory=list),
        language: Language = Language.get_default(),
        agent: Agent = Agent.get_default(LibraryType.MOVIE),
        scanner: Scanner = Scanner.get_default(LibraryType.MOVIE),
        name: str = LibraryName.get_default(LibraryType.MOVIE).value,
    ) -> None:
        super().__init__(
            supported_requests=[
                UserRequest.CREATE,
                UserRequest.DELETE,
                UserRequest.DISPLAY,
                UserRequest.UPDATE,
            ],
            plex_server=plex_server,
            name=name,
            library_type=LibraryType.MOVIE,
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

    def update(self) -> None:
        user_response = self.__draw_items(expect_input=True)
        user_response.value.update()
        user_response.value.refresh()

    def display(self) -> None:
        self.__draw_items(expect_input=False)

    def query(self) -> list[Movie]:
        """
        Returns all movies for the current LibrarySection

        Returns:
            list[plexapi.video.Movie]: Movies from the current Section
        """
        op_type = "QUERY"
        if not self.exists():
            description = f"Movie Library '{self.name}' does not exist"
            raise LibraryOpError(
                op_type=op_type,
                library_type=LibraryType.MOVIE,
                description=description,
            )
        return cast("list[Movie]", self.get_section().searchMovies())

    def delete(self) -> None:
        return super().delete()

    def exists(self) -> bool:
        return super().exists()

    def __draw_items(self, expect_input: bool = False) -> DropdownItemDTO:
        sections = super().get_sections()
        dropdown = []
        for section in sections:
            media_count = len(cast("list[MovieSection]", section.searchMovies()))
            display_name = f"{section.title} ({media_count!s} Movies)"
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
