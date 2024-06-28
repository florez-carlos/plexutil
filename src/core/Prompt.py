import argparse
import json
import pathlib
from typing import Dict

from src.serializer.PlexConfigSerializer import PlexConfigSerializer
from src.Static import Static
from src.dto.PlexConfigDTO import PlexConfigDTO
from src.dto.UserInstructionsDTO import UserInstructionsDTO
from src.enum.LibraryType import LibraryType
from src.enum.UserRequest import UserRequest
from src.exception.PlexUtilConfigException import PlexUtilConfigException
from src.util.PathOps import PathOps


class Prompt(Static):

    @staticmethod
    def get_user_instructions_dto() -> UserInstructionsDTO:

        parser = argparse.ArgumentParser(description="Plex Util")

        request_help_str = "Supported Requests: \n"

        for request in UserRequest.get_all():
            request_help_str += "-> " + request.value + "\n"
        
        parser.add_argument('request',
                            metavar='Request',
                            type=str,
                            nargs='?',
                            help=request_help_str)

        parser.add_argument('-i', '--items',
                            metavar='Items',
                            type=str,
                            nargs='?',
                            help='Items to be passed for the request wrapped in double quotes and separated by comma i.e create_playlist --items "jazz classics,ambient"')


        #dest="subparser_name" allows reading if config has been invoked
        subparsers = parser.add_subparsers(dest="subparser_name",title="Plex Util Configuration Menu",description="Use this menu for the initial setup, the configuration is recorded in a config.json file", help="Configure paths and plex server connection parameters")
        # ,help='Config Help')
        
        parser_config = subparsers.add_parser('config', help='Plex Util Config Menu')
        
        parser_config.add_argument('-music','--music_folder_path', 
                                   metavar='Music Folder Path', 
                                   type=pathlib.Path,
                                   nargs="?",
                                   help="Path to music folder",
                                   default=pathlib.Path(""))
        
        parser_config.add_argument('-movie','--movie_folder_path',
                                   metavar='Movie Folder Path',
                                   type=pathlib.Path,
                                   nargs="?",
                                   help="Path to movie folder",
                                   default=pathlib.Path(""))
        
        parser_config.add_argument('-tv','--tv_folder_path',
                                   metavar='TV Folder Path',
                                   type=pathlib.Path,
                                   nargs="?",
                                   help="Path to tv folder",
                                   default=pathlib.Path(""))
        
        parser_config.add_argument('-playlist','--music_playlist_file_path',
                                   metavar='Music Playlist File Path',
                                   type=pathlib.Path,
                                   nargs="?",
                                   help="Path to music playlist file",
                                   default=pathlib.Path(""))
        
        parser_config.add_argument('-host','--plex_server_host',
                                   metavar='Plex Server Host',
                                   type=str,
                                   nargs="?",
                                   help="Plex server host e.g. localhost",
                                   default="localhost")
        
        parser_config.add_argument('-port','--plex_server_port',
                                   metavar='Plex Server Port',
                                   type=int,
                                   nargs="?",
                                   help="Plex server port e.g. 3200",
                                   default=3200)
        
        parser_config.add_argument('-token','--plex_server_token',
                                   metavar='Plex Server Token',
                                   type=str,
                                   nargs="?",
                                   help="Fetch the token by listening for an (X-Plex-Token) query parameter",
                                   default="")
        
        
        # Parse arguments
        args = parser.parse_args()
        request = args.request
        is_config = args.subparser_name is not None and args.subparser_name == "config"
        items = []

        print(args)
        
        if request is None and not is_config:
            raise ValueError("Positional argument (request) expected but none supplied, see -h")

        if args.items is not None:
            items = [x for x in args.items.split(",")]

        if is_config:
            request = args.subparser_name

        request = UserRequest.get_user_request_from_str(request)
        
        music_folder_path = args.music_folder_path
        movie_folder_path = args.movie_folder_path
        tv_folder_path = args.tv_folder_path
        music_playlist_file_path = args.music_playlist_file_path
        plex_server_host = args.plex_server_host
        plex_server_port = args.plex_server_port
        plex_server_token = args.plex_server_token


        current_path = pathlib.Path.cwd()
        config_file_path = current_path / "config.json"
        
        plex_config_dto = PlexConfigDTO(music_folder_path=music_folder_path,
                             movie_folder_path=movie_folder_path,
                             tv_folder_path=tv_folder_path,
                             music_playlist_file_path=music_playlist_file_path,
                             host=plex_server_host,
                             port=plex_server_port,
                             token=plex_server_token)

        if config_file_path.exists():

            with config_file_path.open() as f:
                file_dict = json.load(f)
                serializer = PlexConfigSerializer()
                plex_config_dto = serializer.to_dto(file_dict)
            
        else:
            
            try:
                
                with config_file_path.open(encoding='utf-8', mode="x") as f:
                    serializer = PlexConfigSerializer()
                    json.dump(serializer.to_json(plex_config_dto), f, indent=4)

            except FileExistsError:

                raise PlexUtilConfigException("Attempted to save new Plex Config but it already exists here: " + str(config_file_path))
                
            except Exception as e:
                
                raise PlexUtilConfigException(e)
            
        
        return UserInstructionsDTO(request=request,items=items,plex_config_dto=plex_config_dto)

