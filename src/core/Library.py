from pathlib import Path
from typing import List, overload
from plexapi.audio import Audio
from plexapi.server import PlexServer
from plexapi.video import Video
from throws import throws
from src.exception.LibraryOpException import LibraryOpException
from src.dto.MusicPlaylistDTO import MusicPlaylistDTO
from src.enum.Agent import Agent
from src.enum.LibraryName import LibraryName
from src.enum.Scanner import Scanner
from src.dto.MusicPlaylistFileDTO import MusicPlaylistFileDTO
from src.enum.Language import Language
from src.enum.LibraryType import LibraryType

from abc import ABC,abstractmethod

class Library(ABC):

    def __init__(self,
                 plex_server: PlexServer,
                 name: LibraryName,
                 library_type: LibraryType,
                 agent: Agent,
                 scanner: Scanner,
                 location: Path,
                 language: Language,
                 prefs_file_location: Path):
                 # tv_library_language_manifest_file_location: Path,
                 # music_playlist_file_dto: MusicPlaylistFileDTO) -> None:
        self.plex_server = plex_server
        self.name = name
        self.library_type = library_type
        self.agent = agent
        self.scanner = scanner
        self.location = location
        self.language = language
        self.prefs_file_location = prefs_file_location
        # self.music_playlist_file_dto = music_playlist_file_dto

    @abstractmethod
    @throws(LibraryOpException)
    def create(self) -> None:
        pass

    @abstractmethod
    @throws(LibraryOpException)
    def delete(self) -> None:
        pass

    @abstractmethod
    def query(self) -> List[Audio] | List[Video]:
        pass

