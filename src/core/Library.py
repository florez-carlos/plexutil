from typing import List
from plexapi.server import PlexServer
from dto.MusicPlaylistDTO import MusicPlaylistDTO
from enum.LibraryName import LibraryName
from src.dto.MusicPlaylistFileDTO import MusicPlaylistFileDTO
from src.enum.Language import Language
from src.enum.LibraryType import LibraryType
from util.PlexOps import PlexOps


class Library():

    def __init__(self,
                 plex_server: PlexServer,
                 name: str,
                 library_type: str,
                 agent: str,
                 scanner: str,
                 location: str,
                 language: Language,
                 music_playlist_file_dto: MusicPlaylistFileDTO) -> None:
        self.plex_server = plex_server
        self.name = name
        self.library_type = library_type
        self.agent = agent
        self.scanner = scanner
        self.location = location
        self.language = language
        self.music_playlist_file_dto = music_playlist_file_dto
    
    #Check if drive letter exists
    def create(self) -> None:
        pass
        
        # if self.library_type == LibraryType.MUSIC:


    # elif type == "movie":
    #     plex.library.add(name=libraryName, type=type,agent=agent,scanner=scanner, location=location,language=language)
    #     plex.library.sections()
    #     plex.library.section(libraryName).editAdvanced(hidden=0, enableCinemaTrailers=1, country="US", originalTitles=0, localizedArtwork=1, useLocalAssets=1, respectTags=0, useExternalExtras=1, skipNonTrailerExtras=0, useRedbandTrailers=0, includeExtrasWithLocalizedSubtitles=0, includeAdultContent=0, autoCollectionThreshold=0, enableBIFGeneration=1, augmentWithProviderContent=1, collectionMode=2)
    # elif type == "show":
    #     plex.library.add(name=libraryName, type=type,agent=agent,scanner=scanner, location=location,language=language)
    #     plex.library.sections()
    #     plex.library.section(libraryName).editAdvanced(hidden=0, episodeSort="0", country="US", showOrdering="aired", useSeasonTitles=0, originalTitles=1, localizedArtwork=1, useLocalAssets=1, respectTags=0, useExternalExtras=1, skipNonTrailerExtras=0, useRedbandTrailers=0, includeExtrasWithLocalizedSubtitles=0, includeAdultContent=0, enableBIFGeneration=1, augmentWithProviderContent=1, flattenSeasons=0)
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

#Exception handling here and return bool
def __create_music__(self,expected_track_count: int, playlists: List[MusicPlaylistDTO]) -> None:
    
    #TODO: replace values in str
    # This creates the library
    part = (f'/library/sections?name=Music&type=music&agent=tv.plex.agents.music'
    f'&scanner=Plex%20Music&language=en-US&importFromiTunes=&enableAutoPhotoTags=&location=F%3A%5Cmedia%5Cmusic&prefs%5BrespectTags%5D=1&prefs%5BaugmentWithSharedContent%5D=0&prefs%5BartistBios%5D=0&prefs%5BalbumReviews%5D=0&prefs%5BpopularTracks%5D=0&prefs%5Bgenres%5D=2&prefs%5BalbumPosters%5D=3&')

    self.plex_server.query(part,method=self.plex_server._session.post)

    requested_attempts = 0
    timeout_seconds = 0

    # Library created, now poll for expected_track_count
    plex_ops = PlexOps(self.plex_server,LibraryType.MUSIC,LibraryName.MUSIC)

    plex_ops.poll(requested_attempts,expected_track_count,timeout_seconds)
    return


