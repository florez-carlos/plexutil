from __future__ import annotations

import argparse
import pathlib
from pathlib import Path

from plexutil.dto.plex_config_dto import PlexConfigDTO
from plexutil.dto.user_instructions_dto import UserInstructionsDTO
from plexutil.enums.user_request import UserRequest
from plexutil.plex_util_logger import PlexUtilLogger
from plexutil.static import Static
from plexutil.util.file_importer import FileImporter


class Prompt(Static):
    @staticmethod
    def get_user_instructions_dto(
        config_file_path: Path,
    ) -> UserInstructionsDTO:
        parser = argparse.ArgumentParser(description="Plex Util")

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
            "-music",
            "--music_folder_path",
            metavar="Music Folder Path",
            type=pathlib.Path,
            nargs="?",
            help="Path to music folder",
            default=pathlib.Path(),
        )

        parser.add_argument(
            "-movie",
            "--movie_folder_path",
            metavar="Movie Folder Path",
            type=pathlib.Path,
            nargs="?",
            help="Path to movie folder",
            default=pathlib.Path(),
        )

        parser.add_argument(
            "-tv",
            "--tv_folder_path",
            metavar="TV Folder Path",
            type=pathlib.Path,
            nargs="?",
            help="Path to tv folder",
            default=pathlib.Path(),
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

        args = parser.parse_args()

        request = args.request
        items = args.items
        is_all_items = args.all_items

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
        is_config = request == UserRequest.CONFIG
        
        music_folder_path = args.music_folder_path
        movie_folder_path = args.movie_folder_path
        tv_folder_path = args.tv_folder_path
        plex_server_host = args.plex_server_host
        plex_server_port = args.plex_server_port
        plex_server_token = args.plex_server_token

        plex_config_dto = PlexConfigDTO(
            music_folder_path=music_folder_path,
            movie_folder_path=movie_folder_path,
            tv_folder_path=tv_folder_path,
            host=plex_server_host,
            port=plex_server_port,
            token=plex_server_token,
        )

        if is_config:
            FileImporter.save_plex_config_dto(
                config_file_path,
                plex_config_dto,
            )
        else:
            plex_config_dto = FileImporter.get_plex_config_dto(
                config_file_path,
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
            items=items,
            plex_config_dto=plex_config_dto,
            is_all_items=is_all_items,
        )
