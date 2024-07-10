import time
from pathlib import Path
from typing import Dict, List, overload
from alive_progress import alive_bar
from plexapi.audio import Audio
from plexapi.exceptions import NotFound
from plexapi.server import PlexServer
from plexapi.video import Video
from throws import throws
from src.dto.LibraryPreferencesDTO import LibraryPreferencesDTO
from src.exception.ExpectedLibraryCountException import ExpectedLibraryCountException
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
                 preferences: LibraryPreferencesDTO):
        self.plex_server = plex_server
        self.name = name
        self.library_type = library_type
        self.agent = agent
        self.scanner = scanner
        self.location = location
        self.language = language
        self.preferences = preferences

    @abstractmethod
    @throws(LibraryOpException)
    def create(self) -> None:
        pass

    @abstractmethod
    @throws(LibraryOpException)
    def delete(self) -> None:

        try:
            
            result = self.plex_server.library.section(self.name.value)
            
            if (result):
                result.delete()
            else:
                raise LibraryOpException("DELETE " + self.name.value + " LIBRARY | Nothing to delete")
                
        except LibraryOpException as e:
            raise e
        except NotFound as e:
            raise LibraryOpException("DELETE " + self.name.value + " LIBRARY | Not found", original_exception=e)
        except Exception as e:
            raise LibraryOpException("DELETE " + self.name.value + " LIBRARY", original_exception=e)

    @abstractmethod
    @throws(LibraryOpException)
    def exists(self) -> bool:

        try:

            result = self.plex_server.library.section(self.name.value)

            if not result:
                return False

        except NotFound as e:
            return False
        except Exception as e:
            raise LibraryOpException("EXISTS " + self.name.value + " LIBRARY", original_exception=e)


        return True

    def poll(self, requested_attempts: int = 0, expected_count: int = 0,interval_seconds: int = 0, tvdb_ids: List[int] = []) -> None:

        current_count = len(self.query(tvdb_ids))
        init_offset = abs(expected_count - current_count)

        print("Requested attempts: "+str(requested_attempts))
        print("Interval seconds: "+str(interval_seconds))
        print("Current count: "+str(current_count)+". Expected: "+str(expected_count))
        print("Expected net change: "+str(init_offset))

        with alive_bar(init_offset) as bar:
            
            attempts = 0
            display_count = 0
            offset = init_offset

            while(attempts<requested_attempts):

                updated_current_count = len(self.query(tvdb_ids))
                offset = abs(updated_current_count - current_count)
                current_count = updated_current_count

                if (current_count == expected_count):

                    for j in range(abs(current_count-display_count)):
                        bar()
                        
                    break


                for j in range(offset):
                    display_count = display_count+1
                    bar()

                time.sleep(interval_seconds)
                attempts = attempts+1
                if attempts >= requested_attempts:
                    raise ExpectedLibraryCountException("TIMEOUT: Did not reach expected count")



    def query(self,tvdb_ids: List[int] = []) -> List[Audio] | List[Video]:

        if (self.library_type is LibraryType.MUSIC):
            if tvdb_ids:
                raise ValueError("Library type: "+ 
                    LibraryType.MUSIC.value +
                    " not compatible with tvdb ids but tvdb ids supplied: " +
                    str(tvdb_ids))
            return self.plex_server.library.section(self.name.value).searchTracks()
        elif (self.library_type is LibraryType.TV):

            shows = self.plex_server.library.section(self.name.value).all()
            shows_filtered = []

            if tvdb_ids:

                for show in shows:
                    guids = show.guids
                    for guid in guids:
                        if "tvdb://" in guid.id:
                            tvdb = guid.id.replace("tvdb://","")
                            if int(tvdb) in tvdb_ids:
                                shows_filtered.append(show)

            return shows_filtered

        else:
            raise ExpectedLibraryCountException("Unsupported Library Type: " + self.library_type.value)

