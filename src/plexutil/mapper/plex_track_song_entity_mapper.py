from plexapi.audio import Track

from plexutil.enums.file_type import FileType
from plexutil.model.song_entity import SongEntity
from plexutil.util.path_ops import PathOps


class PlexTrackSongEntityMapper:
    @staticmethod
    def get_song_entity(track: Track) -> SongEntity:
        plex_track_absolute_location = track.locations[0]
        plex_track_path = PathOps.get_path_from_str(
            plex_track_absolute_location,
        )
        plex_track_full_name = plex_track_path.name
        plex_track_name = plex_track_full_name.rsplit(".", 1)[0]
        plex_track_ext = FileType.get_file_type_from_str(
            plex_track_full_name.rsplit(".", 1)[1],
        )
        return SongEntity(name=plex_track_name, extension=plex_track_ext.value)
