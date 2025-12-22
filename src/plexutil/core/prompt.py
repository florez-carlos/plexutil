from __future__ import annotations

import argparse
import pathlib
import sys
from argparse import RawTextHelpFormatter
from importlib.metadata import PackageNotFoundError, version

from plexutil.dto.library_setting_dto import LibrarySettingDTO
from plexutil.dto.server_config_dto import ServerConfigDTO
from plexutil.dto.user_instructions_dto import UserInstructionsDTO
from plexutil.enums.agent import Agent
from plexutil.enums.icons import Icons
from plexutil.enums.language import Language
from plexutil.enums.library_type import LibraryType
from plexutil.enums.scanner import Scanner
from plexutil.enums.user_request import UserRequest
from plexutil.exception.unexpected_argument_error import (
    UnexpectedArgumentError,
)
from plexutil.exception.user_error import UserError
from plexutil.plex_util_logger import PlexUtilLogger
from plexutil.static import Static
from plexutil.util.file_importer import FileImporter


class Prompt(Static):
    @staticmethod
    def get_user_instructions_dto() -> UserInstructionsDTO:
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
            "-s",
            "--songs",
            metavar="songs",
            nargs="+",
            help=(
                "Songs to be passed to a musical request, "
                'i.e create_music_playlist --songs "path/to/song"'
                '" path_to_song"'
            ),
            default=[],
        )

        parser.add_argument(
            "-pn",
            "--playlist_name",
            metavar="Playlist Name",
            type=str,
            nargs="+",
            help=("Name of the playlist"),
            default=[],
        )

        parser.add_argument(
            "-loc",
            "--locations",
            metavar="Library Locations",
            type=pathlib.Path,
            nargs="+",
            help="Library Locations",
            default=[],
        )

        parser.add_argument(
            "-libn",
            "--library_name",
            metavar="Library Name",
            type=str,
            nargs="+",
            help="Library Name",
            default=[],
        )

        parser.add_argument(
            "-t",
            "--library_type",
            metavar="Library Type",
            type=str,
            nargs="+",
            help="Library Type",
            default=[],
        )

        parser.add_argument(
            "-scanner",
            "--library_scanner",
            metavar="Scanner",
            type=str,
            nargs="+",
            help="Library Scanner",
            default=[],
        )

        parser.add_argument(
            "-agent",
            "--library_agent",
            metavar="Agent",
            type=str,
            nargs="+",
            help="Library Agent",
            default=[],
        )

        parser.add_argument(
            "-l",
            "--language",
            metavar="Library Language",
            type=str,
            nargs="?",
            help="Library Language",
            default=Language.get_default().get_display_name(),
        )

        parser.add_argument(
            "-host",
            "--plex_server_host",
            metavar="Plex Server Host",
            type=str,
            nargs="?",
            help="Plex server host e.g. localhost",
        )

        parser.add_argument(
            "-port",
            "--plex_server_port",
            metavar="Plex Server Port",
            type=int,
            nargs="?",
            help="Plex server port e.g. 32400",
        )

        parser.add_argument(
            "-token",
            "--plex_server_token",
            metavar="Plex Server Token",
            type=str,
            nargs="?",
            help=(
                "Fetch the token by listening for an"
                "(X-Plex-Token) query parameter"
            ),
        )

        parser.add_argument(
            "-sc",
            "--show_configuration",
            action="store_true",
            help=("Displays host,port"),
        )

        parser.add_argument(
            "-sct",
            "--show_configuration_token",
            action="store_true",
            help=("Displays host,port,token"),
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
        songs = args.songs
        playlist_name = args.playlist_name
        is_version = args.version
        is_show_configuration = args.show_configuration
        is_show_configuration_token = args.show_configuration_token
        language = Language.get_from_str(args.language)
        plex_server_host = args.plex_server_host
        plex_server_port = args.plex_server_port
        plex_server_token = args.plex_server_token
        locations = args.locations
        scanner = args.library_scanner
        agent = args.library_agent
        library_type = args.library_type
        library_name = args.library_name

        playlist_name = " ".join(playlist_name) if playlist_name else ""
        library_name = " ".join(library_name) if library_name else ""
        library_type = " ".join(library_type) if library_type else ""
        scanner = " ".join(scanner) if scanner else ""
        agent = " ".join(agent) if agent else ""

        if is_version:
            plexutil_version = ""

            try:
                plexutil_version = version("plexutil")

            except PackageNotFoundError:
                pyproject = FileImporter.get_pyproject()
                plexutil_version = pyproject["project"]["version"]

            PlexUtilLogger.get_logger().info(plexutil_version)
            sys.exit(0)

        if request:
            request = UserRequest.get_user_request_from_str(request)
            if library_type:
                library_type = LibraryType.get_from_str(library_type)
            else:
                library_type = Prompt.confirm_library_type()
            scanner = (
                Scanner.get_from_str(scanner, library_type)
                if scanner
                else Scanner.get_default(library_type)
            )
            agent = (
                Agent.get_from_str(agent, library_type)
                if agent
                else Agent.get_default(library_type)
            )
        else:
            description = "Cannot continue without a request, see -h"
            raise UserError(description)

        server_config_dto = ServerConfigDTO(
            host=plex_server_host,
            port=plex_server_port,
            token=plex_server_token,
        )

        debug = (
            "Received a User Request:\n"
            f"Request: {request.value if request else None}\n"
            f"Songs: {songs!s}\n"
            f"Playlist Name: {playlist_name}\n"
            f"Host: {plex_server_host}\n"
            f"Port: {plex_server_port}\n"
            f"show config: {is_show_configuration!s}\n"
            f"show config token: {is_show_configuration_token!s}\n"
            f"Language: {language.get_value()}\n"
            f"Locations: {locations!s}\n"
            f"Library Name: {library_name}\n"
            f"Library Type: {library_type.get_value()}\n"
            f"Scanner: {scanner.get_value()}\n"
            f"Agent: {agent.get_value()}\n"
        )
        PlexUtilLogger.get_logger().debug(debug)

        return UserInstructionsDTO(
            request=request,
            is_show_configuration=is_show_configuration,
            is_show_configuration_token=is_show_configuration_token,
            library_type=library_type,
            library_name=library_name,
            playlist_name=playlist_name,
            songs=songs,
            locations=locations,
            server_config_dto=server_config_dto,
            language=language,
            scanner=scanner,
            agent=agent,
        )

    @staticmethod
    def confirm_library_setting(
        library_setting: LibrarySettingDTO,
    ) -> LibrarySettingDTO:
        user_response = library_setting.user_response
        response = library_setting.user_response

        if library_setting.is_toggle:
            response = (
                input(
                    f"\n========== {library_setting.display_name} ==========\n"
                    f"{library_setting.description}\n"
                    f"{library_setting.display_name}? (y/n): "
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

            if response == "y":
                if isinstance(library_setting.user_response, int):
                    user_response = 1
                elif isinstance(library_setting.user_response, bool):
                    user_response = True
            elif response == "n":
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
                        f"({response}) | Setting Remains Unchanged"
                    )
                else:
                    description = (
                        f"{Icons.WARNING} Did not understand your input: "
                        f"({response}) proceeding with default"
                    )

                PlexUtilLogger.get_logger().warning(description)

        elif library_setting.is_value:
            pass
        elif library_setting.is_dropdown:
            dropdown = library_setting.dropdown

            description = (
                f"\n========== {library_setting.display_name} ==========\n"
                f"{library_setting.description}\n"
                f"{library_setting.display_name}? (y/n): "
                f"Available Options:\nDefault is "
                f"({dropdown[0].display_name})\n"
            )
            dropdown_count = 1
            columns_count = 1
            max_columns = 5
            min_space = "   "
            newline = "\n"

            for item in dropdown:
                description = (
                    description + f"[{dropdown_count}] -> {item.display_name}"
                    f"{min_space if columns_count < max_columns else newline}"
                )

                dropdown_count = dropdown_count + 1
                columns_count = (
                    1 if columns_count >= max_columns else columns_count + 1
                )

            PlexUtilLogger.get_console_logger().info(description)
            response = input(f"Pick (1-{len(dropdown)}): ").strip().lower()

            if response.isdigit():
                int_response = int(response)
                if int_response > 0 and int_response <= len(dropdown):
                    user_response = int_response - 1
                else:
                    user_response = 0
            else:
                description = (
                    f"{Icons.WARNING} Did not understand your input: "
                    f"({response}) proceeding with default"
                )
                PlexUtilLogger.get_logger().warning(description)
                user_response = 0

            user_response = dropdown[user_response].value

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
    def confirm_library_type() -> LibraryType:
        dropdown = LibraryType.get_all()

        description = (
            "\n========== Library Type Selection ==========\n"
            "Available Options:\n"
        )
        dropdown_count = 1

        for lib in dropdown:
            description = (
                description
                + f"[{dropdown_count}] -> {lib.get_display_name()}\n"
            )

            dropdown_count = dropdown_count + 1

        PlexUtilLogger.get_console_logger().info(description)
        response = input(f"Pick (1-{len(dropdown)}): ").strip().lower()

        if response.isdigit():
            int_response = int(response)
            if int_response > 0 and int_response <= len(dropdown):
                user_response = int_response - 1
            else:
                user_response = 0
        else:
            description = f"Did not understand your input: {response}"
            raise UserError(description)

        description = (
            f"Prompt for Library Type Selection | "
            f"User Chose: {dropdown[user_response].get_value()}"
        )
        PlexUtilLogger.get_logger().debug(description)

        return dropdown[user_response]
