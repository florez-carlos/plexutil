from typing import cast

from plexutil.dto.plex_config_dto import PlexConfigDTO
from plexutil.enums.library_type import LibraryType
from plexutil.serializer.serializable import Serializable
from plexutil.serializer.serializer import Serializer
from plexutil.util.path_ops import PathOps


class PlexConfigSerializer(Serializer):
    def to_json(self, serializable: Serializable) -> dict:
        if not isinstance(serializable, PlexConfigDTO):
            description = "Expected PlexConfigDTO"
            raise TypeError(description)
        plex_config_dto = cast(PlexConfigDTO, serializable)
        return {
            "paths": {
                "music_folder": str(plex_config_dto.music_folder_path),
                "movie_folder": str(plex_config_dto.movie_folder_path),
                "tv_folder": str(plex_config_dto.tv_folder_path),
            },
            "plex": {
                "host": plex_config_dto.host,
                "port": plex_config_dto.port,
                "token": plex_config_dto.token,
            },
        }

    def to_dto(self, json_dict: dict) -> PlexConfigDTO:
        paths = json_dict["paths"]

        music_folder_path = PathOps.get_path_from_str(
            paths["music_folder"],
            LibraryType.MUSIC.value,
            is_dir=True,
        )
        movie_folder_path = PathOps.get_path_from_str(
            paths["movie_folder"],
            LibraryType.MOVIE.value,
            is_dir=True,
        )
        tv_folder_path = PathOps.get_path_from_str(
            paths["tv_folder"],
            LibraryType.TV.value,
            is_dir=True,
        )

        plex = json_dict["plex"]

        plex_server_host = plex["host"]
        plex_server_port = plex["port"]

        if not isinstance(plex_server_port, int):
            description = f"""Expected plex server port to be an int
            but got a {type(plex_server_port)}"""
            raise ValueError(description)

        plex_server_token = plex["token"]

        return PlexConfigDTO(
            music_folder_path=music_folder_path,
            movie_folder_path=movie_folder_path,
            tv_folder_path=tv_folder_path,
            host=plex_server_host,
            port=plex_server_port,
            token=plex_server_token,
        )
