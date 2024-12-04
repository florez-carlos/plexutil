from pathlib import Path

from plexutil.dto.music_playlist_dto import MusicPlaylistDTO
from plexutil.mapper.music_playlist_mapper import MusicPlaylistMapper
from plexutil.mapper.song_mapper import SongMapper
from plexutil.model.music_playlist_entity import MusicPlaylistEntity
from plexutil.model.song_entity import SongEntity
from plexutil.model.song_music_playlist_entity import SongMusicPlaylistEntity
from plexutil.service.db_manager import db_manager
from plexutil.service.music_playlist_service import MusicPlaylistService
from plexutil.service.song_service import SongService


class SongMusicPlaylistCompositeService:
    def __init__(self, db_path: Path):
        self.db_path = db_path

    def get(
        self,
        entities: list[MusicPlaylistEntity],
    ) -> list[MusicPlaylistDTO]:
        with db_manager(
            self.db_path,
            [MusicPlaylistEntity, SongEntity, SongMusicPlaylistEntity],
        ):
            playlist_names = [x.name for x in entities]
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
                        SongMusicPlaylistEntity.playlist
                        == MusicPlaylistEntity.id
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
            for _, v in playlists.items():
                result.append(v)
            return result

    def add(self, music_playlist_dto: MusicPlaylistDTO) -> None:
        self.add_many([music_playlist_dto])

    def add_many(self, music_playlist_dtos: list[MusicPlaylistDTO]) -> None:
        with db_manager(
            self.db_path,
            [MusicPlaylistEntity, SongEntity, SongMusicPlaylistEntity],
        ):
            song_service = SongService(self.db_path)
            music_playlist_service = MusicPlaylistService(self.db_path)
            song_mapper = SongMapper()
            music_playlist_mapper = MusicPlaylistMapper()

            playlists = [
                music_playlist_mapper.get_entity(x)
                for x in music_playlist_dtos
            ]
            music_playlist_service.add_many(playlists)

            songs = []
            for music_playlist_dto in music_playlist_dtos:
                songs.append(
                    [
                        song_mapper.get_entity(x)
                        for x in music_playlist_dto.songs
                    ]
                )

            flattened_songs = [item for sublist in songs for item in sublist]
            song_service.add_many(flattened_songs)

            to_save = []
            for music_playlist_dto in music_playlist_dtos:
                playlist = music_playlist_service.get(
                    music_playlist_mapper.get_entity(music_playlist_dto)
                )
                songs = [
                    song_mapper.get_entity(x) for x in music_playlist_dto.songs
                ]
                songs = song_service.get_many(songs)
                for song in songs:
                    to_save.append(
                        SongMusicPlaylistEntity(
                            playlist=playlist.id, song=song.id
                        )
                    )

                bulk = [(entity.playlist, entity.song) for entity in to_save]

                SongMusicPlaylistEntity.insert_many(
                    bulk,
                    fields=[
                        SongMusicPlaylistEntity.playlist,
                        SongMusicPlaylistEntity.song,
                    ],
                ).execute()

            return
