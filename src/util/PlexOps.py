from pathlib import Path
import time
from plexapi.server import PlexServer
from plexapi.audio import Audio
from plexapi.video import Video
from alive_progress import alive_bar

from src.enum.LibraryName import LibraryName
from src.enum.LibraryType import LibraryType
from src.exception.ExpectedLibraryCountException import ExpectedLibraryCountException


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
    # def poll(self, requested_attempts: int = 0, expected_count: int = 0,interval_seconds: int = 0, tvdb_ids: List[int] = []) -> None:
    #
    #
    #     current_count = len(self.__query_library__())
    #
    #     offset = abs(expected_count - current_count)
    #     print("Requested attempts: "+str(requested_attempts))
    #     print("Interval seconds: "+str(interval_seconds))
    #     print("Current count: "+str(current_count)+". Expected: "+str(expected_count))
    #     print("Expected net change: "+str(offset))
    #
    #     with alive_bar(offset) as bar:
    #         
    #         attempts = -1
    #
    #         while(attempts<requested_attempts):
    #
    #             time.sleep(interval_seconds)
    #             attempts = attempts+1
    #             if attempts >= requested_attempts:
    #                 raise ExpectedLibraryCountException("TIMEOUT: Did not reach expected count")
    #
    #             if tvdb_ids:
    #                 updated_current_count = len(self.__query_library__(tvdb_ids))
    #             else:
    #                 updated_current_count = len(self.__query_library__())
    #
    #             offset = abs(updated_current_count - current_count)
    #
    #             if offset == 0:
    #                 continue
    #             else:
    #                 current_count = updated_current_count
    #                 for j in range(offset):
    #                     bar()
    #
    #     return
    #
    #
    # def __query_library__(self,tvdb_ids: List[int] = []) -> List[Audio] | List[Video]:
    #
    #     if (self.library_type is LibraryType.MUSIC):
    #         if tvdb_ids:
    #             raise ValueError("Library type: "+ 
    #                 LibraryType.MUSIC.value +
    #                 " not compatible with tvdb ids but tvdb ids supplied: " +
    #                 str(tvdb_ids))
    #         return self.plex_server.library.section(self.library_name).searchTracks()
    #     elif (self.library_type is LibraryType.TV):
    #
    #         shows = self.plex_server.library.section(self.library_name).all()
    #         shows_filtered = []
    #
    #         if tvdb_ids:
    #
    #             for show in shows:
    #                 guids = show.guids
    #                 for guid in guids:
    #                     if "tvdb://" in guid.id:
    #                         tvdb = guid.id.replace("tvdb://","")
    #                         if int(tvdb) in tvdb_ids:
    #                             shows_filtered.append(show)
    #
    #         return shows_filtered
    #
    #     else:
    #         raise ExpectedLibraryCountException("Unsupported Library Type: " + self.library_type.value)
    #
    #
