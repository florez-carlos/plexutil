from pathlib import Path
from plexapi.audio import os
from plexapi.server import PlexServer
from dto.LibraryPreferencesDTO import LibraryPreferencesDTO
from dto.MusicPlaylistFileDTO import MusicPlaylistFileDTO
from enum.Agent import Agent
from enum.Language import Language
from enum.LibraryName import LibraryName
from enum.LibraryType import LibraryType
from enum.Scanner import Scanner
from src.core.Library import Library


class Playlist(Library):

    def __init__(self, 
                 plex_server: PlexServer,
                 location:Path,
                 language: Language,
                 music_playlist_file_dto: MusicPlaylistFileDTO):
        
        super().__init__(plex_server,LibraryName.MUSIC,LibraryType.MUSIC,Agent.MUSIC,Scanner.MUSIC,location,language,LibraryPreferencesDTO({},{},{}))
        self.music_playlist_file_dto = music_playlist_file_dto


    def create(self) -> None:

        tracks = self.plex_server.library.section(self.name).searchTracks()
        plex_track_dict = {}
        plex_playlist = []

        playlists = self.music_playlist_file_dto.playlists

        for track in tracks:
            
            plex_track_location = track.locations[0]
            plex_track_name = plex_track_location.replace(str(self.location)+os.sep,"")
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
        # if (deleteAll):
        #     [x.delete() for x in plex.playlists(playlistType="audio")]
        # else:

        playlist_names =  [x.name for x in self.music_playlist_file_dto.playlists]
        
        for playlist in self.plex_server.playlists(playlistType="audio"):
            if (playlist.title in playlist_names):
                playlist.delete()








