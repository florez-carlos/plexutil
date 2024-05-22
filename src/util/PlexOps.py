import time
from plexapi.server import PlexServer
from plexapi.utils import json
from throws import throws
from alive_progress import alive_bar

from dto.ResourceLocationDTO import ResourceLocationDTO
from src.enum.LibraryName import LibraryName
from src.enum.LibraryType import LibraryType
from src.enum.Agent import Agent
from src.enum.Scanner import Scanner
from src.enum.Language import Language
from src.exception.ExpectedLibraryCountException import ExpectedLibraryCountException
from src.util.QueryBuilder import QueryBuilder


class PlexOps():


    def __init__(self, plex_server: PlexServer,
                 library_type: LibraryType,
                 library_name: LibraryName,
                 library_location: ResourceLocationDTO,
                 music_playlist_file_location: ResourceLocationDTO,
                 movie_library_prefs_file_location: ResourceLocationDTO,
                 tv_library_prefs_file_location: ResourceLocationDTO,
                 music_library_prefs_file_location: ResourceLocationDTO):
        self.plex_server = plex_server
        self.library_type = library_type
        self.library_name = library_name
        self.library_location = library_location
        self.music_playlist_file_location = music_playlist_file_location
        self.movie_library_prefs_file_location = movie_library_prefs_file_location
        self.tv_library_prefs_file_location = tv_library_prefs_file_location
        self.music_library_prefs_file_location = music_library_prefs_file_location
        self.test = [516,519,544,559,580,589,591,591,591,611,620,621]

    # @throws(ExpectedLibraryCountException)
    #
    def poll(self, requested_attempts: int = 0, expected_count: int = 0,interval_seconds: int = 0) -> None:


        current_count = __query_library__(self,0)

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

                updated_current_count = __query_library__(self,attempts)
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

        with open(self.music_library_prefs_file_location.build_uri(),encoding='utf-8') as file:
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
                location=self.library_location.build_uri(),
                prefs=prefs)

            part = query_builder.build()

        #This posts a library
        if part:
            self.plex_server.query(part,method=self.plex_server._session.post)


        with open(self.music_playlist_file_location.build_uri(),encoding='utf-8') as file:
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
            location=self.library_location.build_uri(),
            language=Language.ENGLISH_US.value)

        #TODO: This line triggers something that refreshes that library, how can I remove this?
        self.plex_server.library.sections()

        prefs = {}

        with open(self.movie_library_prefs_file_location.build_uri(),encoding='utf-8') as file:
            file_dict = json.load(file)
            prefs = file_dict.get("prefs")


        self.plex_server.library.section(self.library_name).editAdvanced(**prefs)


    def create_tv_library(self):

        self.plex_server.library.add(
            name=self.library_name.value,
            type=self.library_type.value,
            agent=Agent.TV.value,
            scanner=Scanner.TV.value,
            location=self.library_location.build_uri(),
            language=Language.ENGLISH_US.value)

        #TODO: This line triggers something that refreshes that library, how can I remove this?
        self.plex_server.library.sections()

        prefs = {}

        with open(self.tv_library_prefs_file_location.build_uri(),encoding='utf-8') as file:
            file_dict = json.load(file)
            prefs = file_dict.get("prefs")

        self.plex_server.library.section(self.library_name).editAdvanced(**prefs)

        return

    # elif type == "show":

    #     #This sets languageOverride to es-ES for spanish shows
    #     #These are tvdb ids
    #     shows_es = [327417,396583,388477,292262,282670,274522]
    #     found_shows_es = []
    #
    #     attempts = 0
    #     print("Waiting for es-ES shows to become available")
    #     while(True):
    #         attempts = attempts+1
    #         if attempts > 100:
    #             raise ValueError("Plex could not populate es-ES shows")
    #         shows_found = 0
    #         for show in plex.library.section(libraryName).all():
    #             guids = show.guids
    #             for guid in guids:
    #                 if "tvdb://" in guid.id:
    #                     tvdb = guid.id.replace("tvdb://","")
    #                     if int(tvdb) in shows_es:
    #                         shows_found = shows_found + 1
    #
    #         print("===================")
    #         print("Attempt {}/{}".format(str(attempts),"100"))
    #         print("Expected es-ES show count: " + str(len(shows_es)))
    #         print("Current es-ES show count: " + str(shows_found))
    #         if shows_found == len(shows_es):
    #             print("es-ES shows ready, proceeding to update metadata")
    #             break
    #         time.sleep(20)
    #
    #     for show in plex.library.section(libraryName).all():
    #         guids = show.guids
    #         for guid in guids:
    #             if "tvdb://" in guid.id:
    #                 tvdb = guid.id.replace("tvdb://","")
    #                 if int(tvdb) in shows_es:
    #                     found_shows_es.append(show)
    #
    #     for found_show_es in found_shows_es:
    #         found_show_es.editAdvanced(languageOverride="es-ES")
    #     plex.library.section(libraryName).refresh()
    #
    # else:
    #     raise ValueError("Library type: "+"\'"+type+"\' not supported")
    #
    #
    #     pass
    # else:
    #     raise ValueError("Unsupported Library")

def delete_library(self) -> None:

    if (self.library_type is LibraryType.MUSIC):
        result = self.plex_server.library.section(self.library_name)
        if (result):
            result.delete()
    else:
        raise ValueError("Unsupported Library")

def __query_library__(self,count):

    if (self.library_type is LibraryType.MUSIC):
        return self.test[count]
        # return len(self.plex_server.library.section(self.library_name).searchTracks())
    else:
        raise ExpectedLibraryCountException("Unsupported Library Type: " + self.library_type.value)


