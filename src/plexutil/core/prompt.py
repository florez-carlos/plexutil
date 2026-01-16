from __future__ import annotations

import argparse
import sys
from argparse import RawTextHelpFormatter
from importlib.metadata import PackageNotFoundError, version
from typing import cast

from plexutil.dto.dropdown_item_dto import DropdownItemDTO
from plexutil.dto.library_setting_dto import LibrarySettingDTO
from plexutil.enums.language import Language
from plexutil.enums.user_request import UserRequest
from plexutil.exception.unexpected_argument_error import (
    UnexpectedArgumentError,
)
from plexutil.exception.user_error import UserError
from plexutil.plex_util_logger import PlexUtilLogger
from plexutil.static import Static
from plexutil.util.file_importer import FileImporter
from plexutil.util.icons import Icons


class Prompt(Static):
    @staticmethod
    def confirm_user_request() -> UserRequest:
        """
        Receives initial user input with a request or --version
        Issues early termination if --version is requested

        Returns:
            UserRequest: Based on user's input
        """
        parser = argparse.ArgumentParser(
            description="Plexutil", formatter_class=RawTextHelpFormatter
        )

        request_help_str = "Supported Requests: \n"

        for request in UserRequest.get_all():
            request_help_str += "-> " + request.value + "\n"

        parser.add_argument(
            "request",
            metavar="Request",
            type=str,
            nargs="?",
            help=request_help_str,
        )

        parser.add_argument(
            "-v",
            "--version",
            action="store_true",
            help=("Displays version"),
        )

        args, unknown = parser.parse_known_args()

        if unknown:
            raise UnexpectedArgumentError(unknown)

        request = args.request
        is_version = args.version

        if is_version:
            plexutil_version = ""

            try:
                plexutil_version = version("plexutil")

            except PackageNotFoundError:
                pyproject = FileImporter.get_pyproject()
                plexutil_version = pyproject["project"]["version"]

            debug = "Received a User Request: version"
            PlexUtilLogger.get_logger().debug(debug)
            PlexUtilLogger.get_logger().info(plexutil_version)
            sys.exit(0)

        debug = f"Received a User Request: {request or None}"
        PlexUtilLogger.get_logger().debug(debug)

        return UserRequest.get_user_request_from_str(request)

    @staticmethod
    def confirm_library_setting(
        library_setting: LibrarySettingDTO,
    ) -> LibrarySettingDTO:
        user_response = library_setting.user_response
        response = library_setting.user_response
        default_selection = bool(library_setting.user_response)

        if library_setting.is_toggle:
            response = Prompt.__get_toggle_response(
                title=library_setting.display_name,
                description=library_setting.description,
                question=library_setting.display_name,
                default_selection=default_selection,
                is_from_server=library_setting.is_from_server,
            )
            user_response = (
                int(response)
                if isinstance(library_setting.user_response, int)
                else bool(response)
            )

        elif library_setting.is_value:
            pass
        elif library_setting.is_dropdown:
            dropdown = library_setting.dropdown
            user_response = Prompt.draw_dropdown(
                title=library_setting.display_name,
                description=library_setting.description,
                dropdown=dropdown,
                is_multi_column=True,
            ).value

        return LibrarySettingDTO(
            name=library_setting.name,
            display_name=library_setting.display_name,
            description=library_setting.description,
            is_toggle=library_setting.is_toggle,
            is_value=library_setting.is_value,
            is_dropdown=library_setting.is_dropdown,
            dropdown=library_setting.dropdown,
            user_response=user_response,
        )

    @staticmethod
    def confirm_language() -> Language:
        """
        Prompts user for a Language

        Returns:
            Language: The chosen Language
        """
        languages = Language.get_all()
        items = [
            DropdownItemDTO(
                display_name=language.get_display_name(),
                value=language,
            )
            for language in languages
        ]

        response = Prompt.draw_dropdown(
            title="Language Selection",
            description="Choose the Language",
            dropdown=items,
            is_multi_column=True,
        )

        return response.value

    @staticmethod
    def confirm_remote() -> bool:
        """
        Prompts user if this device is running the Plex Server

        Returns:
            bool: Is this a remote device (Not the Plex Server)
        """
        description = (
            "\nSelecting yes will check local media files stored in this "
            "device match those in the server\n"
            "*Pick no if this isn't the device the Plex Server is running on\n"
        )
        response = Prompt.__get_toggle_response(
            title="Is the selected device hosting the Plex Server?",
            description=description,
            question="Is the selected server this device",
            default_selection=True,
            is_from_server=False,
        )
        return not response

    @staticmethod
    def confirm_text(title: str, description: str, question: str) -> list[str]:
        """
        Prompts the user for text,
        expects one or multiple entries separated by ,

        Args:
            title (str): Top banner title
            description (str): Helpful text
            question (str): Question

        Returns:
            str: The User's response
        """
        Prompt.__draw_banner(
            title=title,
            description=description,
            question=question,
        )
        return cast(
            "str", Prompt.__get_multi_response(default_selection="")
        ).split(",")

    @staticmethod
    def draw_dropdown(
        title: str,
        description: str,
        dropdown: list[DropdownItemDTO],
        is_multi_column: bool = False,
        expect_input: bool = True,
    ) -> DropdownItemDTO:
        if dropdown:
            default_display_name = dropdown[0].display_name
            default_selection_idx = 0
            idx = 0
            for item in dropdown:
                if item.is_default:
                    default_display_name = item.display_name
                    default_selection_idx = idx
                    break
                idx = idx + 1

            if expect_input:
                description = f"{description}\nAvailable Options:\n\n"

            Prompt.__draw_banner(
                title=title,
                description=description,
                default_selection=default_display_name,
                is_from_server=False,
            )

        else:
            description = (
                f"\n{description}\n\n{Icons.WARNING} Nothing Available\n"
            )
            Prompt.__draw_banner(
                title=title, description=description, is_from_server=False
            )
            sys.exit(0)

        dropdown_count = 1
        columns_count = 1
        max_columns = 3 if is_multi_column else 1
        max_column_width = 25
        space = ""
        newline = "\n"

        description = ""
        for item in dropdown:
            if item.is_default:
                offset = max_column_width - (len(item.display_name) + 1)
            else:
                offset = max_column_width - len(item.display_name)

            space = " " * offset
            number_format = (
                f"[ {dropdown_count}] "
                if dropdown_count < 10  # noqa: PLR2004
                else f"[{dropdown_count}] "
            )

            if item.is_default:
                display_name = f"{item.display_name} {Icons.STAR}"
            else:
                display_name = f"{item.display_name}"

            description = (
                f"{description}{number_format} -> {display_name}"
                f"{space if columns_count < max_columns else newline}"
            )

            dropdown_count = dropdown_count + 1
            columns_count = (
                1 if columns_count >= max_columns else columns_count + 1
            )

        PlexUtilLogger.get_console_logger().info(description)

        if not expect_input:
            return DropdownItemDTO()

        response = cast(
            "int",
            Prompt.__get_multi_response(
                default_selection=default_selection_idx,
                dropdown_length=len(dropdown),
                is_from_server=False,
            ),
        )

        return dropdown[response]

    @staticmethod
    def __draw_banner(
        title: str,
        description: str,
        default_selection: bool | int | str = "",
        is_from_server: bool = False,
        question: str = "",
    ) -> None:
        """
        Draws a banner

        Args:
            title (str): Message to display at the top of the banner
            description (str): helpful message to display in banner body
            default_selection (bool): The value to display as Default/Current
            is_current (bool): is default_selection an existing value
            from the plex server?
            question (str): The question, ? (y/n) is appended after it
            if default_selection is a bool

        Returns:
            None: This method does not return a value
        """
        question = question.replace("?", "")
        question = f"\n{question}?\n" if question else ""

        banner = (
            f"\n{Icons.BANNER_LEFT} {title} {Icons.BANNER_RIGHT}\n"
            f"\n{description}"
            f"{question}"
        )

        PlexUtilLogger.get_console_logger().info(banner)

    @staticmethod
    def __get_toggle_response(
        title: str,
        description: str,
        question: str,
        default_selection: bool = False,
        is_from_server: bool = False,
    ) -> bool:
        """
        Prompt user for a y/n response
        Returns default_selection if user response not recognized

        Args:
            title (str): Message to display at the top of the banner
            description (str): helpful message to display in banner body
            question (str): The question, ? (y/n) is appended after it
            default_selection (bool): The default value
            is_current (bool): is default_selection an existing value
            from the plex server?

        Returns:
            bool: yes/no selection from user
        """
        Prompt.__draw_banner(
            title=title,
            description=description,
            question=question,
            default_selection=default_selection,
            is_from_server=is_from_server,
        )

        response = (
            input(f"\n\nAnswer (y/n) {Icons.CHEVRON_RIGHT}").strip().lower()
        )
        description = f"{question}? User chose: {response}"
        PlexUtilLogger.get_logger().debug(description)

        if response in {"y", "yes"}:
            return True
        elif response in {"n", "no"}:
            return False
        else:
            if is_from_server:
                description = (
                    f"{Icons.WARNING} Did not understand your input: "
                    f"{response} | Setting Remains Unchanged "
                    f"({'y' if default_selection else 'n'})"
                )
            else:
                description = (
                    f"{Icons.WARNING} Did not understand your input: "
                    f"{response} | Proceeding with default "
                    f"({'y' if default_selection else 'n'})"
                )
                PlexUtilLogger.get_logger().warning(description)
            return default_selection

    @staticmethod
    def __get_multi_response(
        default_selection: bool | str | int = "",
        dropdown_length: int = 0,
        is_from_server: bool = False,
    ) -> bool | str | int:
        response = ""

        try:
            if isinstance(default_selection, bool):
                description = f"\n\nAnswer (y/n) {Icons.CHEVRON_RIGHT}"

                response = input(description).strip().lower()

                if response in {"y", "yes"}:
                    return True
                elif response in {"n", "no"}:
                    return False
                else:
                    raise UserError

            elif isinstance(default_selection, str):
                description = (
                    f"\n\nEnter text (For multiple values, "
                    f"separate w/ comma) {Icons.CHEVRON_RIGHT}"
                )
                return input(description).strip()
            elif dropdown_length > 0:
                description = (
                    f"Pick (1-{dropdown_length!s}) {Icons.CHEVRON_RIGHT} "
                )
                response = input(description).strip()
                if response.isdigit():
                    int_response = int(response)
                    if int_response > 0 and int_response <= dropdown_length:
                        return int_response - 1
                    else:
                        raise UserError
                else:
                    raise UserError
            else:
                return default_selection

        except UserError:
            if is_from_server:
                description = (
                    f"{Icons.WARNING} Did not understand your input: "
                    f"{response} | Setting Remains Unchanged"
                )
            else:
                description = (
                    f"{Icons.WARNING} Did not understand your input: "
                    f"{response} | Proceeding with default"
                )
                PlexUtilLogger.get_logger().warning(description)
            return default_selection
