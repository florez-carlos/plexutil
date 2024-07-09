# import requests
import os
import pathlib
from plexapi.server import PlexServer

from src.core.Playlist import Playlist
from src.dto.MusicPlaylistFileDTO import MusicPlaylistFileDTO
from src.core.Prompt import Prompt
from src.enum.UserRequest import UserRequest
from src.util.FileImporter import FileImporter


from src.core.MusicLibrary import MusicLibrary
from src.core.MovieLibrary import MovieLibrary
from src.core.TVLibrary import TVLibrary
from src.enum.Language import Language
from src.util.PathOps import PathOps


def main():

    instructions_dto = Prompt.get_user_instructions_dto()
            
    request = instructions_dto.request
    items = instructions_dto.items
    plex_config_dto = instructions_dto.plex_config_dto

    host = plex_config_dto.host
    port = int(plex_config_dto.port)
    token = plex_config_dto.token

    baseurl = 'http://% s:% s' % (host,port)
    plex_server = PlexServer(baseurl, token)

    music_location = instructions_dto.plex_config_dto.music_folder_path
    movie_location = instructions_dto.plex_config_dto.movie_folder_path
    tv_location = instructions_dto.plex_config_dto.tv_folder_path

    music_prefs_file_location = PathOps.get_project_root() / "src" / "config" / "MusicLibraryPrefs.json"
    movie_prefs_file_location =  PathOps.get_project_root() / "src" / "config" / "MovieLibraryPrefs.json"
    tv_prefs_file_location =  PathOps.get_project_root() / "src" / "config" / "TVLibraryPrefs.json"
    music_playlist_file_location = PathOps.get_project_root() / "src" / "config" / "MusicPlaylists.json"
    tv_language_manifest_file_location = PathOps.get_project_root() / "src" / "config" / "TVLanguageManifest.json"

    preferences_dto = FileImporter.get_library_preferences_dto(music_prefs_file_location,movie_prefs_file_location,tv_prefs_file_location) 
    music_playlist_file_dto = FileImporter.get_music_playlist_file_dto(music_playlist_file_location)
    tv_language_manifest_file_dto = FileImporter.get_tv_language_manifest(tv_language_manifest_file_location)

    playlists =[]
    music_playlist_file_dto_filtered = MusicPlaylistFileDTO()

    if items:
        for playlist in music_playlist_file_dto.playlists:
            if playlist.name in items:
                playlists.append(playlist)

        music_playlist_file_dto_filtered = MusicPlaylistFileDTO(music_playlist_file_dto.track_count,playlists)

    match request:
        # If config, we should already be done by now
        case UserRequest.CONFIG:
            return
        case UserRequest.INIT:

            music_library = MusicLibrary(plex_server,music_location,Language.ENGLISH_US,preferences_dto,music_playlist_file_dto)
            tv_library = TVLibrary(plex_server,tv_location,Language.ENGLISH_US,preferences_dto,tv_language_manifest_file_dto)
            movie_library = MovieLibrary(plex_server,movie_location,Language.ENGLISH_US,preferences_dto)

            music_library.delete()
            tv_library.delete()
            movie_library.delete()

            music_library.create()
            tv_library.create()
            movie_library.create()

            playlist_library = Playlist(plex_server,music_location,Language.ENGLISH_US,music_playlist_file_dto)
            playlist_library.delete()
            playlist_library = Playlist(plex_server,music_location,Language.ENGLISH_US,music_playlist_file_dto_filtered)
            playlist_library.create()

        case UserRequest.DELETE_MUSIC_PLAYLIST:

            playlist_library = Playlist(plex_server,music_location,Language.ENGLISH_US,music_playlist_file_dto_filtered)
            playlist_library.delete()

        case UserRequest.CREATE_MUSIC_PLAYLIST:

            playlist_library = Playlist(plex_server,music_location,Language.ENGLISH_US,music_playlist_file_dto_filtered)
            playlist_library.create()

        case UserRequest.DELETE_MUSIC_LIBRARY:

            music_library = MusicLibrary(plex_server,music_location,Language.ENGLISH_US,preferences_dto,music_playlist_file_dto)
            music_library.delete()

        case UserRequest.CREATE_MUSIC_LIBRARY:

            music_library = MusicLibrary(plex_server,music_location,Language.ENGLISH_US,preferences_dto,music_playlist_file_dto)
            music_library.create()

        case UserRequest.CREATE_MOVIE_LIBRARY:

            movie_library = MovieLibrary(plex_server,movie_location,Language.ENGLISH_US,preferences_dto)
            movie_library.create()

        case UserRequest.DELETE_MOVIE_LIBRARY:

            movie_library = MovieLibrary(plex_server,movie_location,Language.ENGLISH_US,preferences_dto)
            movie_library.delete()

        case UserRequest.CREATE_TV_LIBRARY:

            tv_library = TVLibrary(plex_server,tv_location,Language.ENGLISH_US,preferences_dto,tv_language_manifest_file_dto)
            tv_library.create()

        case UserRequest.DELETE_TV_LIBRARY:

            tv_library = TVLibrary(plex_server,tv_location,Language.ENGLISH_US,preferences_dto,tv_language_manifest_file_dto)
            tv_library.delete()


            



if __name__ == '__main__':
    main()
