from dataclasses import dataclass
from pathlib import Path

from src.serializer.Serializable import Serializable


@dataclass(frozen=True)
class PlexConfigDTO(Serializable):
    music_folder_path: Path = Path()
    movie_folder_path: Path = Path()
    tv_folder_path: Path = Path()
    # music_playlist_file_path: Path = Path()
    host: str = "localhost"
    port: int = 32000
    token: str = ""


def __eq__(self, other):
    if not isinstance(other, PlexConfigDTO):
        return NotImplemented

    return (
        self.music_folder_path == other.music_folder_path
        and self.movie_folder_path == other.movie_folder_path
        and self.tv_folder_path == other.tv_folder_path
        and self.host == other.host
        and self.port == other.port
        and self.token == other.token
    )


def __hash__(self):
    return hash(
        (
            self.music_folder_path,
            self.movie_folder_path,
            self.tv_folder_path,
            self.host,
            self.port,
            self.token,
        )
    )
