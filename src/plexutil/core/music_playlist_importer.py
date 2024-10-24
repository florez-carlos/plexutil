from plexutil.dto.music_playlist_file_dto import MusicPlaylistFileDTO
from plexutil.dto.plex_config_dto import PlexConfigDTO
from plexutil.model.music_playlist_entity import MusicPlaylistEntity
from plexutil.model.song_entity import SongEntity
from plexutil.model.song_music_playlist_entity import SongMusicPlaylistEntity


class MusicPlaylistImporter:
    def __init__(
        self,
        plex_config_dto: PlexConfigDTO,
        music_playlist_file_dto: MusicPlaylistFileDTO,
    ) -> None:
        self.plex_config_dto = plex_config_dto
        self.music_playlist_file_dto = music_playlist_file_dto

    def do(self) -> None:
        # Music location here
        # path = PathOps.get_project_root().parent
        # audio_files = (
        #     list(path.rglob("*.flac"))
        #     + list(path.rglob("*.mp3"))
        #     + list(path.rglob("*.aac"))
        #     + list(path.rglob("*.alac"))
        # )
        # for audio_file in audio_files:
        #     song = SongEntity(
        #         name=audio_file.stem, extension=audio_file.suffix.lstrip(".")
        #     )
        #     song.save(force_insert=True)

        playlists = self.music_playlist_file_dto.playlists
        for playlist in playlists:
            playlist_name = playlist.name
            # music_playlist_id = MusicPlaylistEntity(
            #     name=playlist_name,
            # ).save(force_insert=True)
            music_playlist_id = (
                MusicPlaylistEntity.select()
                .where(MusicPlaylistEntity.name == playlist_name)
                .get()
                .id
            )
            songs = playlist.songs
            for song in songs:
                song_name = song.name
                song_extension = song.extension.value
                song_found = (
                    SongEntity.select()
                    .where(
                        (SongEntity.name == song_name)
                        & (SongEntity.extension == song_extension)
                    )
                    .get()
                )
                song_id = song_found.id
                print(f"song_found: {song_found}")

                SongMusicPlaylistEntity(
                    playlist=music_playlist_id, song=song_id
                ).save(force_insert=True)
