from enum import Enum
from typing import List

class UserRequest(Enum):
    
    CONFIG = "config"
    INIT = "init"
    CREATE_MUSIC_LIBRARY = "create_music_library"
    DELETE_MUSIC_LIBRARY = "delete_music_library"
    CREATE_MUSIC_PLAYLIST = "create_music_playlist"
    DELETE_MUSIC_PLAYLIST = "delete_music_playlist"


    @staticmethod
    #Forward Reference used here in type hint
    def get_all() -> List['UserRequest']:

        return [UserRequest.CONFIG,
                UserRequest.INIT,
                UserRequest.CREATE_MUSIC_LIBRARY,
                UserRequest.DELETE_MUSIC_LIBRARY,
                UserRequest.CREATE_MUSIC_PLAYLIST,
                UserRequest.DELETE_MUSIC_PLAYLIST]

    @staticmethod
    def get_user_request_from_str(user_request_candidate: str) -> "UserRequest":

        requests = UserRequest.get_all()
        user_request_candidate = user_request_candidate.lower()
        
        for request in requests:
            if user_request_candidate == request.value or user_request_candidate.replace("_"," ") == request.value:
                return request
        
        raise ValueError("Request not supported: " + user_request_candidate) 


