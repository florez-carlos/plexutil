from plexutil.dto.music_playlist_dto import MusicPlaylistDTO
from plexutil.mapper.music_playlist_mapper import MusicPlaylistMapper
from plexutil.mapper.song_mapper import SongMapper
from plexutil.model.music_playlist_entity import MusicPlaylistEntity
from plexutil.model.song_entity import SongEntity
from plexutil.model.song_music_playlist_entity import SongMusicPlaylistEntity
from plexutil.static import Static


class SongMusicPlaylistCompositeService(Static):
    @staticmethod
    def get_music_playlist_dto(
        playlist_names: list[str],
    ) -> list[MusicPlaylistDTO]:
        song_playlists = (
            SongEntity.select(
                SongEntity.id.alias("song_id"),
                SongEntity.name.alias("song_name"),
                MusicPlaylistEntity.name.alias("playlist_id"),
                MusicPlaylistEntity.name.alias("playlist_name"),
            )
            .join(
                SongMusicPlaylistEntity,
                on=(SongEntity.id == SongMusicPlaylistEntity.song),
            )
            .join(
                MusicPlaylistEntity,
                on=(
                    SongMusicPlaylistEntity.playlist == MusicPlaylistEntity.id
                ),
            )
            .where(MusicPlaylistEntity.name.in_(playlist_names))
        )

        playlists = {}
        for song_playlist in song_playlists:
            music_playlist_mapper = MusicPlaylistMapper()
            song_mapper = SongMapper()

            song_entity = SongEntity(
                id=song_playlist.song_id,
                name=song_playlist.song_name,
            )

            music_playlist_entity = MusicPlaylistEntity(
                id=song_playlist.playlist_id,
                name=song_playlist.playlist_name,
            )

            song_dto = song_mapper.get_dto(song_entity)
            music_playlist_dto = music_playlist_mapper.get_dto(
                music_playlist_entity
            )

            if music_playlist_dto.name not in playlists:
                playlists[music_playlist_dto.name] = music_playlist_dto

            playlists[music_playlist_dto.name].songs.append(song_dto)

        result = []
        for k, v in playlists.items():
            result.append(v)
        return result
