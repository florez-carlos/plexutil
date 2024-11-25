from __future__ import annotations

import argparse
import pathlib
import sys
from argparse import RawTextHelpFormatter
from importlib.metadata import PackageNotFoundError, version

from plexutil.dto.server_config_dto import ServerConfigDTO
from plexutil.dto.user_instructions_dto import UserInstructionsDTO
from plexutil.enums.language import Language
from plexutil.enums.library_name import LibraryName
from plexutil.enums.library_type import LibraryType
from plexutil.enums.user_request import UserRequest
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
            "-i",
            "--items",
            metavar="Items",
            type=str,
            nargs="?",
            help=(
                "Items to be passed for the request wrapped"
                "in double quotes and separated by comma"
                'i.e create_playlist --items "jazz classics,ambient"'
            ),
        )

        parser.add_argument(
            "-ai",
            "--all_items",
            action="store_true",
            help=(
                "Indicates operation to be performed on all available items"
                "instead of specifying individual items"
            ),
        )

        parser.add_argument(
            "-loc",
            "--locations",
            metavar="Library Locations",
            type=pathlib.Path,
            nargs="+",
            help="Library Locations",
            default=pathlib.Path(),
        )

        parser.add_argument(
            "-lib",
            "--library_type",
            metavar="Library Type",
            type=str,
            nargs="?",
            help="Library Type",
            default=LibraryType.MUSIC.value,
        )

        parser.add_argument(
            "-libn",
            "--library_name",
            metavar="Library Name",
            type=str,
            nargs="?",
            help="Library Type",
            default=LibraryName.MUSIC.value,
        )

        parser.add_argument(
            "-l",
            "--language",
            metavar="Library Language",
            type=str,
            nargs="?",
            help="Library Language",
            default=Language.ENGLISH_US.value,
        )

        parser.add_argument(
            "-host",
            "--plex_server_host",
            metavar="Plex Server Host",
            type=str,
            nargs="?",
            help="Plex server host e.g. localhost",
            default="localhost",
        )

        parser.add_argument(
            "-port",
            "--plex_server_port",
            metavar="Plex Server Port",
            type=int,
            nargs="?",
            help="Plex server port e.g. 32400",
            default=32400,
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
            default="",
        )

        parser.add_argument(
            "-sc",
            "--show_configuration",
            action="store_true",
            help=("Displays host,port,token"),
        )

        parser.add_argument(
            "-v",
            "--version",
            action="store_true",
            help=("Displays version"),
        )

        args = parser.parse_args()

        request = args.request
        items = args.items
        is_all_items = args.all_items
        is_version = args.version
        is_show_configuration = args.show_configuration
        language = Language.get_language_from_str(args.language)
        plex_server_host = args.plex_server_host
        plex_server_port = args.plex_server_port
        plex_server_token = args.plex_server_token
        locations = args.locations
        library_type = UserRequest.get_library_type_from_request(
            UserRequest.get_user_request_from_str(args.library_type)
        )
        library_name = args.library_name
        print(f"Locations: {locations}")

        if is_version:
            plexutil_version = ""

            try:
                plexutil_version = version("plexutil")

            except PackageNotFoundError:
                pyproject = FileImporter.get_pyproject()
                plexutil_version = pyproject["project"]["version"]

            PlexUtilLogger.get_logger().info(plexutil_version)
            sys.exit(0)

        if is_show_configuration:
            sys.exit(0)

        if request is None:
            description = (
                (
                    "Positional argument (request) "
                    "expected but none supplied, see -h"
                ),
            )
            raise ValueError(description)

        if items is not None:
            if is_all_items:
                description = (
                    (
                        "--all_items requested but --items also specified,"
                        "only one can be used at a time"
                    ),
                )
                raise ValueError(description)

            items = list(items.split(","))

        request = UserRequest.get_user_request_from_str(request)

        server_config_dto = ServerConfigDTO(
            host=plex_server_host,
            port=plex_server_port,
            token=plex_server_token,
        )

        debug = (
            "Received a User Request:\n"
            f"Request: {request.value}\n"
            f"items: {items or []}\n"
            f"is_all_items: {is_all_items or False}\n"
            f"Host: {plex_server_host}\n"
            f"Port: {plex_server_port}\n"
        )
        PlexUtilLogger.get_logger().debug(debug)

        return UserInstructionsDTO(
            request=request,
            library_type=library_type,
            library_name=library_name,
            items=items,
            locations=locations,
            is_all_items=is_all_items,
            server_config_dto=server_config_dto,
            language=language,
        )
