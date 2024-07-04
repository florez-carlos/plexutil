from src.enum.LibraryType import LibraryType
from src.dto.PlexConfigDTO import PlexConfigDTO
from src.serializer.Serializer import Serializer
from src.util.PathOps import PathOps


class PlexConfigSerializer(Serializer):


    def to_json(self, serializable: PlexConfigDTO) -> dict:

        config = {
            "config": {

                "paths": {
                    "music_folder":str(serializable.music_folder_path),
                    "movie_folder":str(serializable.movie_folder_path),
                    "tv_folder":str(serializable.tv_folder_path),
                    # "music_playlist_file":str(serializable.music_playlist_file_path),
                },
                "plex": {
                    "host": serializable.host,
                    "port": serializable.port,
                    "token": serializable.token,

                }
        }}

        return config

    def to_dto(self, json_dict: dict) -> PlexConfigDTO:

        paths = json_dict["config"]["paths"]

        music_folder_path = PathOps.get_path_from_str(paths["music_folder"],LibraryType.MUSIC.value,is_dir=True)
        movie_folder_path = PathOps.get_path_from_str(paths["movie_folder"],LibraryType.MOVIE.value,is_dir=True)
        tv_folder_path = PathOps.get_path_from_str(paths["tv_folder"],LibraryType.TV.value,is_dir=True)
        # music_playlist_file_path = PathOps.get_path_from_str(paths["music_playlist_file"],"Music Playlist",is_file=True)

        plex = json_dict["config"]["plex"]

        plex_server_host = plex["host"]
        plex_server_port = plex["port"]
        
        if not isinstance(plex_server_port,int):
            raise ValueError("Expected plex server port to be an int but got a %s" % (type(plex_server_port)))

        plex_server_token = plex["token"]

        return PlexConfigDTO(music_folder_path=music_folder_path,
                             movie_folder_path=movie_folder_path,
                             tv_folder_path=tv_folder_path,
                             # music_playlist_file_path=music_playlist_file_path,
                             host=plex_server_host,
                             port=plex_server_port,
                             token=plex_server_token)
