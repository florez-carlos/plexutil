from pathlib import Path
import time
from typing import Dict, List
from plexapi.server import PlexServer
from plexapi.utils import json
from plexapi.audio import Audio
from plexapi.video import Video
from throws import throws
from alive_progress import alive_bar

from src.dto.PlexConfigDTO import PlexConfigDTO
from src.exception.PlexUtilConfigException import PlexUtilConfigException
from src.enum.LibraryName import LibraryName
from src.enum.LibraryType import LibraryType
from src.enum.Agent import Agent
from src.enum.Scanner import Scanner
from src.enum.Language import Language
from src.exception.ExpectedLibraryCountException import ExpectedLibraryCountException
from src.util.QueryBuilder import QueryBuilder
from src.util.PathOps import PathOps


class PlexOps():


    def __init__(self, plex_server: PlexServer,
                 library_type: LibraryType,
                 library_name: LibraryName,
                 library_location: Path,
                 music_playlist_file_location: Path,
                 movie_library_prefs_file_location: Path,
                 tv_library_prefs_file_location: Path,
                 music_library_prefs_file_location: Path,
                 tv_library_language_manifest_file_location: Path):
        self.plex_server = plex_server
        self.library_type = library_type
        self.library_name = library_name
        self.library_location = library_location
        self.music_playlist_file_location = music_playlist_file_location
        self.movie_library_prefs_file_location = movie_library_prefs_file_location
        self.tv_library_prefs_file_location = tv_library_prefs_file_location
        self.music_library_prefs_file_location = music_library_prefs_file_location
        self.tv_library_language_manifest_file_location = tv_library_language_manifest_file_location

    # @throws(ExpectedLibraryCountException)
    #
    def poll(self, requested_attempts: int = 0, expected_count: int = 0,interval_seconds: int = 0, tvdb_ids: List[int] = []) -> None:


        current_count = len(self.__query_library__())

        offset = abs(expected_count - current_count)
        print("Requested attempts: "+str(requested_attempts))
        print("Interval seconds: "+str(interval_seconds))
        print("Current count: "+str(current_count)+". Expected: "+str(expected_count))
        print("Expected net change: "+str(offset))

        with alive_bar(offset) as bar:
            
            attempts = -1

            while(attempts<requested_attempts):

                time.sleep(interval_seconds)
                attempts = attempts+1
                if attempts >= requested_attempts:
                    raise ExpectedLibraryCountException("TIMEOUT: Did not reach expected count")

                if tvdb_ids:
                    updated_current_count = len(self.__query_library__(tvdb_ids))
                else:
                    updated_current_count = len(self.__query_library__())

                offset = abs(updated_current_count - current_count)

                if offset == 0:
                    continue
                else:
                    current_count = updated_current_count
                    for j in range(offset):
                        bar()

        return

    def create_music_library(self) -> None:

        part = ""
        prefs = {}

        with self.music_library_prefs_file_location.open(encoding='utf-8') as file:

            file_dict = json.load(file)
            prefs = file_dict.get("prefs")

        if (self.library_type is LibraryType.MUSIC):

            query_builder = QueryBuilder(
                "/library/sections",
                name=LibraryName.MUSIC.value,
                the_type=LibraryType.MUSIC.value,
                agent = Agent.MUSIC.value,
                scanner = Scanner.MUSIC.value,
                language = Language.ENGLISH_US.value,
                importFromiTunes = "",
                enableAutoPhotoTags="",
                location=str(self.library_location),
                prefs=prefs)

            part = query_builder.build()

        #This posts a library
        if part:
            self.plex_server.query(part,method=self.plex_server._session.post)


        with self.music_playlist_file_location.open(encoding='utf-8') as file:
            
            file_dict = json.load(file)
            track_count = file_dict.get("trackCount")

        try:
            self.poll(100,track_count,10)
        except:
            pass

    def create_movie_library(self) -> None:

        self.plex_server.library.add(
            name=self.library_name.value,
            type=self.library_type.value,
            agent=Agent.MOVIE.value,
            scanner=Scanner.MOVIE.value,
            location=str(self.library_location),
            language=Language.ENGLISH_US.value)

        #TODO: This line triggers something that refreshes that library, how can I remove this?
        self.plex_server.library.sections()

        prefs = {}

        with self.movie_library_prefs_file_location.open(encoding='utf-8') as file:
            
            file_dict = json.load(file)
            prefs = file_dict.get("prefs")


        self.plex_server.library.section(self.library_name).editAdvanced(**prefs)


    def create_tv_library(self):

        self.plex_server.library.add(
            name=self.library_name.value,
            type=self.library_type.value,
            agent=Agent.TV.value,
            scanner=Scanner.TV.value,
            location=str(self.library_location),
            language=Language.ENGLISH_US.value)

        #TODO: This line triggers something that refreshes that library, how can I remove this?
        self.plex_server.library.sections()

        prefs = {}

        with self.tv_library_prefs_file_location.open(encoding='utf-8') as file:
            
            file_dict = json.load(file)
            prefs = file_dict.get("prefs")

        self.plex_server.library.section(self.library_name).editAdvanced(**prefs)

        tvdb_ids = {}

        with self.tv_library_language_manifest_file_location.open(encoding='utf-8') as file:
            
            file_dict = json.load(file)
            languages = file_dict.get("languages")
            for language in languages:
                language_name = language["name"]
                regions = language["regions"]
                for region in regions:
                    region_name = region["name"]
                    ids = region["tvdbIds"]
                    tvdb_ids[language_name+"-"+region_name] = ids

        for name,ids in tvdb_ids.items():

            try:
                self.poll(100,len(ids),10,ids)
                shows = self.__query_library__(ids)
                for show in shows:
                    show.editAdvanced(languageOverride=name)
                self.plex_server.library.section(self.library_name).refresh()
            except:
                pass


        return


    def delete_library(self) -> None:

        if (self.library_type is LibraryType.MUSIC):
            result = self.plex_server.library.section(self.library_name)
            if (result):
                result.delete()
        else:
            raise ValueError("Unsupported Library")

    def __query_library__(self,tvdb_ids: List[int] = []) -> List[Audio] | List[Video]:

        if (self.library_type is LibraryType.MUSIC):
            if tvdb_ids:
                raise ValueError("Library type: "+ 
                    LibraryType.MUSIC.value +
                    " not compatible with tvdb ids but tvdb ids supplied: " +
                    str(tvdb_ids))
            return self.plex_server.library.section(self.library_name).searchTracks()
        elif (self.library_type is LibraryType.TV):

            shows = self.plex_server.library.section(self.library_name).all()
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


