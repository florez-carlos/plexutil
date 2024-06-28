from pathlib import Path
from typing import List
from alive_progress import alive_bar
from plexapi.audio import Audio
from plexapi.server import PlexServer
from plexapi.utils import json
from throws import throws
from src.exception.ExpectedLibraryCountException import ExpectedLibraryCountException
from src.exception.LibraryOpException import LibraryOpException
from src.enum.Agent import Agent
from src.enum.Language import Language
from src.enum.LibraryName import LibraryName
from src.enum.LibraryType import LibraryType
from src.enum.Scanner import Scanner
from src.dto.MusicPlaylistFileDTO import MusicPlaylistFileDTO
from src.core.Library import Library
from src.util.QueryBuilder import QueryBuilder

import time

from src.util.PlexOps import PlexOps


class MovieLibrary(Library):

    def __init__(self,
                 plex_server: PlexServer,
                 name: LibraryName,
                 location:Path,
                 language: Language,
                 prefs_file_location: Path):
        
        super().__init__(plex_server,name,LibraryType.MOVIE,Agent.MOVIE,Scanner.MOVIE,location,language,prefs_file_location)
        



    @throws(LibraryOpException)
    def create(self) -> None:
        
        try:
                
            self.plex_server.library.add(
                name=self.name.value,
                type=self.library_type.value,
                agent=self.agent.value,
                scanner=self.scanner.value,
                location=str(self.location),
                language=self.language.value)

            #This line triggers a refresh of the library
            self.plex_server.library.sections()

            prefs = {}

            with self.prefs_file_location.open(encoding='utf-8') as file:
                
                file_dict = json.load(file)
                prefs = file_dict.get("prefs")


            self.plex_server.library.section(self.name).editAdvanced(**prefs)

        except LibraryOpException as e:
            raise e
        except Exception as e:
            raise LibraryOpException("CREATE", original_exception=e)

        return


        
    @throws(LibraryOpException)
    def delete(self) -> None:

        try:
            
            result = self.plex_server.library.section(self.name)
            
            if (result):
                result.delete()
            else:
                raise LibraryOpException("DELETE", "Not found: " + self.name.value + " of library type: " + self.library_type.value)
                
        except LibraryOpException as e:
            raise e
        except Exception as e:
            raise LibraryOpException("DELETE", original_exception=e)

    @throws(LibraryOpException)
    def query(self) -> List[Audio]:

        try:
            
            return self.plex_server.library.section(self.name).searchTracks()
            
        except Exception as e:
            
                raise LibraryOpException("QUERY", original_exception=e)

