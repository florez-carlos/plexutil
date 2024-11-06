from plexapi.server import Playlist

from plexutil.model.music_playlist_entity import MusicPlaylistEntity


class PlexPlaylistMusicPlaylistEntityMapper:
    @staticmethod
    def get_music_playlist_entity(playlist: Playlist) -> MusicPlaylistEntity:
        return MusicPlaylistEntity(name=playlist.title)
