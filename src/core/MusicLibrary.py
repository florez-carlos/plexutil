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


class MusicLibrary(Library):

    def __init__(self,
                 plex_server: PlexServer,
                 name: LibraryName,
                 location:Path,
                 language: Language,
                 prefs_file_location: Path,
                 music_playlist_file_dto: MusicPlaylistFileDTO):
        
        super().__init__(plex_server,name,LibraryType.MUSIC,Agent.MUSIC,Scanner.MUSIC,location,language,prefs_file_location)
        self.music_playlist_file_dto = music_playlist_file_dto
        



    @throws(LibraryOpException)
    def create(self) -> None:

        try:
            part = ""
            prefs = {}

            with self.prefs_file_location.open(encoding='utf-8') as file:

                file_dict = json.load(file)
                prefs = file_dict.get("prefs")

                query_builder = QueryBuilder(
                    "/library/sections",
                    name=LibraryName.MUSIC.value,
                    the_type=LibraryType.MUSIC.value,
                    agent = Agent.MUSIC.value,
                    scanner = Scanner.MUSIC.value,
                    language = Language.ENGLISH_US.value,
                    importFromiTunes = "",
                    enableAutoPhotoTags="",
                    location=str(self.location),
                    prefs=prefs)

                part = query_builder.build()

            #This posts a music library
            if part:
                self.plex_server.query(part,method=self.plex_server._session.post)
            else:
                raise LibraryOpException("CREATE", "Query Builder has not built a part!")

            #Now we poll for library status
            # PlexOps.poll(100,self.music_playlist_file_dto.track_count,10)

        except LibraryOpException as e:
            raise e
        except Exception as e:
            raise LibraryOpException("CREATE", original_exception=e)

        
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

