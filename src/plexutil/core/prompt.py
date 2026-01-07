from __future__ import annotations

import argparse
import sys
from argparse import RawTextHelpFormatter
from importlib.metadata import PackageNotFoundError, version

from plexutil.dto.dropdown_item_dto import DropdownItemDTO
from plexutil.dto.library_setting_dto import LibrarySettingDTO
from plexutil.enums.language import Language
from plexutil.enums.user_request import UserRequest
from plexutil.exception.unexpected_argument_error import (
    UnexpectedArgumentError,
)
from plexutil.plex_util_logger import PlexUtilLogger
from plexutil.static import Static
from plexutil.util.file_importer import FileImporter
from plexutil.util.icons import Icons


class Prompt(Static):
    @staticmethod
    def get_user_request() -> UserRequest:
        """
        Receives initial user input with a request or --version

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
        default = "yes" if library_setting.user_response == 1 else "no"

        if library_setting.is_toggle:
            response = (
                input(
                    f"\n========== {library_setting.display_name} ==========\n"
                    f"{library_setting.description}\n"
                    f"{library_setting.display_name}? "
                    f"(Default: {default}) (y/n): "
                )
                .strip()
                .lower()
            )

            if isinstance(library_setting.user_response, int):
                user_response = 0
            elif isinstance(library_setting.user_response, bool):
                user_response = False
            else:
                user_response = ""

            if not response:
                description = "Unchanged"
                PlexUtilLogger.get_logger().info(description)

            if response in {"y", "yes"}:
                if isinstance(library_setting.user_response, int):
                    user_response = 1
                elif isinstance(library_setting.user_response, bool):
                    user_response = True
            elif response in {"n", "no"}:
                if isinstance(library_setting.user_response, int):
                    user_response = 0
                elif isinstance(library_setting.user_response, bool):
                    user_response = False
            else:
                if not response and library_setting.is_from_server:
                    description = "Setting Remains Unchanged"
                elif response and library_setting.is_from_server:
                    description = (
                        f"{Icons.WARNING} Did not understand your input: "
                        f"{response} | Setting Remains Unchanged"
                    )
                else:
                    description = (
                        f"{Icons.WARNING} Did not understand your input: "
                        f"{response} | Proceeding with default"
                    )
                    user_response = library_setting.user_response

                PlexUtilLogger.get_logger().warning(description)

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

        description = (
            f"Setting: {library_setting.name} | "
            f"User Input: {response!s} | Chosen: {user_response!s}"
        )
        PlexUtilLogger.get_logger().debug(description)

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
        response = (
            input(
                f"\n========== {title} ==========\n"
                f"{description}\n"
                f"{question}?: "
            )
            .strip()
            .split(",")
        )
        description = f"User Response: {response}"
        PlexUtilLogger.get_logger().debug(description)
        return response

    @staticmethod
    def draw_dropdown(
        title: str,
        description: str,
        dropdown: list[DropdownItemDTO],
        is_multi_column: bool = False,
        expect_input: bool = True,
    ) -> DropdownItemDTO:
        if dropdown:
            if expect_input:
                description = (
                    f"\n========== {title} ==========\n"
                    f"\n{description}\n"
                    f"Available Options:\n"
                    f" \n(Default: {dropdown[0].display_name})\n\n"
                )
            else:
                description = (
                    f"\n========== {title} ==========\n\n{description}\n\n"
                )

        else:
            description = (
                f"\n========== {title} ==========\n"
                f"\n{description}\n"
                f"\n{Icons.WARNING} Nothing Available\n"
            )
            PlexUtilLogger.get_console_logger().info(description)
            sys.exit(0)
        dropdown_count = 1
        columns_count = 1
        max_columns = 3 if is_multi_column else 1
        max_column_width = 25
        space = ""
        newline = "\n"

        for item in dropdown:
            offset = max_column_width - len(item.display_name)
            space = " " * offset
            number_format = (
                f"[ {dropdown_count}] "
                if dropdown_count < 10  # noqa: PLR2004
                else f"[{dropdown_count}] "
            )

            description = (
                description + number_format + f"-> {item.display_name}"
                f"{space if columns_count < max_columns else newline}"
            )

            dropdown_count = dropdown_count + 1
            columns_count = (
                1 if columns_count >= max_columns else columns_count + 1
            )

        PlexUtilLogger.get_console_logger().info(description)
        if not expect_input:
            return DropdownItemDTO()
        response = input(f"Pick (1-{len(dropdown)}): ").strip().lower()

        user_response = 0
        description = (
            f"{Icons.WARNING} Did not understand your input: "
            f"{response} | Proceeding with default"
        )

        if response.isdigit():
            int_response = int(response)
            if int_response > 0 and int_response <= len(dropdown):
                user_response = int_response - 1
            else:
                PlexUtilLogger.get_logger().warning(description)
        else:
            PlexUtilLogger.get_logger().warning(description)

        description = f"User Chose: {dropdown[user_response].value!s}"
        PlexUtilLogger.get_logger().debug(description)

        return dropdown[user_response]
