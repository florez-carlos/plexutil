from __future__ import annotations

from enum import Enum

from plexutil.dto.library_setting_dropdown_item_dto import (
    LibrarySettingDropdownItemDTO,
)
from plexutil.enums.icons import Icons
from plexutil.enums.library_type import LibraryType


class LibrarySetting(Enum):
    ENABLE_CINEMA_TRAILERS = (
        "enableCinemaTrailers",
        "Enable Cinema Trailers",
        (
            f"Play Trailers automatically prior to the selected movie\n"
            f"{Icons.WARNING.value} Also needs to be enabled in the "
            f"client app\n"
        ),
        [LibraryType.MOVIE],
        True,
        False,
        False,
        [],
        0,
    )

    ORIGINAL_TITLES = (
        "originalTitles",
        "Original Titles",
        (
            "Use the original titles for all items "
            "regardless of the library language\n"
        ),
        [LibraryType.MOVIE],
        True,
        False,
        False,
        [],
        1,
    )

    LOCALIZED_ARTWORK = (
        "localizedArtwork",
        "Prefer artwork based on library language",
        "Use localized posters when available\n",
        [LibraryType.MOVIE],
        True,
        False,
        False,
        [],
        1,
    )

    USE_LOCAL_ASSETS = (
        "useLocalAssets",
        "Prefer artwork based on library language",
        (
            "When scanning this library, "
            "use local posters and artwork if present\n"
        ),
        [LibraryType.MOVIE],
        True,
        False,
        False,
        [],
        1,
    )

    RESPECT_TAGS = (
        "respectTags",
        "Prefer local metadata",
        (
            "When scanning this library, prefer "
            "embedded tags and local files if present\n"
        ),
        [LibraryType.MOVIE],
        True,
        False,
        False,
        [],
        0,
    )

    ENABLE_BIF_GENERATION = (
        "enableBIFGeneration",
        "Enable video preview thumbnails",
        (
            "Generate video preview thumbnails for items in this library "
            "when enabled in server settings\n"
        ),
        [LibraryType.MOVIE],
        True,
        False,
        False,
        [],
        1,
    )

    RATINGS_SOURCE = (
        "ratingsSource",
        "Ratings Source",
        "Select a primary source for ratings\n",
        [LibraryType.MOVIE],
        False,
        False,
        True,
        [
            LibrarySettingDropdownItemDTO(
                display_name="Rotten Tomatoes", value="rottentomatoes"
            ),
            LibrarySettingDropdownItemDTO(display_name="IMDb", value="imdb"),
            LibrarySettingDropdownItemDTO(
                display_name="The Movie Database", value="themoviedb"
            ),
        ],
        0,
    )

    @staticmethod
    def get_all(library_type: LibraryType) -> list[LibrarySetting]:
        settings = list(LibrarySetting)
        return [
            x
            for x in settings
            if library_type in x.get_compatible_library_types()
        ]

    def get_name(self) -> str:
        """
        Name is the canonical name of the Setting in the Plex Server

        Returns:
            str: This Setting's canonical name
        """
        return self.value[0]

    def get_display_name(self) -> str:
        """
        Display Name of the Setting in the GUI

        Returns:
            str: The Display Name
        """
        return self.value[1]

    def get_description(self) -> str:
        """
        Short Description

        Returns:
            str: The Description
        """
        return self.value[2]

    def get_compatible_library_types(self) -> list[LibraryType]:
        """
        The Library Types this setting can be applied to

        Returns:
            str: The Description
        """
        return self.value[3]

    def is_toggle(self) -> bool:
        """
        Is this a Setting a toggle

        Returns:
            bool: Is this a Setting a toggle
        """
        return self.value[4]

    def is_value(self) -> bool:
        """
        Is this a Setting a value i.e: 2

        Returns:
            bool: Is this a Setting a value
        """
        return self.value[5]

    def is_dropdown(self) -> bool:
        """
        Is this a Setting a Dropdown

        Returns:
            bool: Is this a Setting Dropdown
        """
        return self.value[6]

    def get_dropdown(self) -> list[LibrarySettingDropdownItemDTO]:
        """
        Get the Dropdown items for this setting

        Returns:
            list[LibrarySettingDropdownItemDTO]: The Dropdown items
        """
        return self.value[7]

    def get_default_selection(self) -> bool | int | str:
        """
        Get the Default selection for this Setting

        Returns:
            bool | int | str: The Default selection
        """
        return self.value[8]
