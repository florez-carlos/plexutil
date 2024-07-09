from pathlib import Path
from plexapi.audio import os
from plexapi.server import PlexServer
from src.dto.LibraryPreferencesDTO import LibraryPreferencesDTO
from src.dto.MusicPlaylistFileDTO import MusicPlaylistFileDTO
from src.enum.Agent import Agent
from src.enum.Language import Language
from src.enum.LibraryName import LibraryName
from src.enum.LibraryType import LibraryType
from src.enum.Scanner import Scanner
from src.core.Library import Library
from src.util.PathOps import PathOps


class Playlist(Library):

    def __init__(self, 
                 plex_server: PlexServer,
                 location:Path,
                 language: Language,
                 music_playlist_file_dto: MusicPlaylistFileDTO):
        
        super().__init__(plex_server,LibraryName.MUSIC,LibraryType.MUSIC,Agent.MUSIC,Scanner.MUSIC,location,language,LibraryPreferencesDTO({},{},{}))
        self.music_playlist_file_dto = music_playlist_file_dto


    def create(self) -> None:

        tracks = self.plex_server.library.section(self.name.value).searchTracks()
        plex_track_dict = {}
        plex_playlist = []

        print("Checking server track count meets expected count: " + str(self.music_playlist_file_dto.track_count))
        self.poll(10,self.music_playlist_file_dto.track_count,10)

        playlists = self.music_playlist_file_dto.playlists

        for track in tracks:
            
            plex_track_absolute_location = track.locations[0]
            plex_track_path = PathOps.get_path_from_str(plex_track_absolute_location)
            plex_track_full_name = plex_track_path.name
            plex_track_name = plex_track_full_name.rsplit(".", 1)[0]
            plex_track_dict[plex_track_name] = track

        for playlist in playlists:

            playlist_name = playlist.name
            songs = playlist.songs

            for song in songs:

                song_name = song.name

                if (plex_track_dict.get(song_name) is None):
                    raise ValueError("File in music playlist: \'" + song_name + "\' does not exist in server")

                plex_playlist.append(plex_track_dict.get(song_name))

            self.plex_server.createPlaylist(title=playlist_name, items=plex_playlist)


    def delete(self) -> None:

        playlist_names =  [x.name for x in self.music_playlist_file_dto.playlists]
        
        for playlist in self.plex_server.playlists(playlistType="audio"):
            if (playlist.title in playlist_names):
                playlist.delete()








