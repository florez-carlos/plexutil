from pathlib import Path

from plexapi.utils import json
from src.dto.TVLanguageManifestFileDTO import TVLanguageManifestFileDTO
from src.serializer.TVLanguageManifestSerializer import TVLanguageManifestSerializer
from src.Static import Static
from src.exception.ImporterException import ImporterException
from src.dto.LibraryPreferencesDTO import LibraryPreferencesDTO
from src.dto.PlexConfigDTO import PlexConfigDTO
from src.dto.MusicPlaylistFileDTO import MusicPlaylistFileDTO
from src.serializer.PlexConfigSerializer import PlexConfigSerializer
from src.serializer.MusicPlaylistFileSerializer import MusicPlaylistFileSerializer


class FileImporter(Static):

    @staticmethod
    def get_library_preferences_dto(music_preferences_file_location: Path,
                                    movie_preferences_file_location: Path,
                                    tv_preferences_file_location: Path
                                    ) -> LibraryPreferencesDTO:

        music_prefs = {}
        movie_prefs = {}
        tv_prefs = {}

        try:

            with music_preferences_file_location.open(encoding='utf-8') as file:
                file_dict = json.load(file)
                music_prefs = file_dict.get("prefs")

            with movie_preferences_file_location.open(encoding='utf-8') as file:
                file_dict = json.load(file)
                movie_prefs = file_dict.get("prefs")

            with tv_preferences_file_location.open(encoding='utf-8') as file:
                file_dict = json.load(file)
                tv_prefs = file_dict.get("prefs")

            if not music_prefs:
                raise ImporterException("Could not import music preferences")
            elif not movie_prefs:
                raise ImporterException("Could not import movie preferences")
            elif not tv_prefs:
                raise ImporterException("Could not import tv preferences")

        except ImporterException as e:
            raise e
        except Exception as e:
            raise ImporterException(original_exception=e)

        return LibraryPreferencesDTO(music_prefs, movie_prefs, tv_prefs)
    
    @staticmethod
    def get_plex_config_dto(plex_config_file_location: Path) -> PlexConfigDTO:
        
        try:

            serializer = PlexConfigSerializer()

            with plex_config_file_location.open(encoding='utf-8') as file:
                file_dict = json.load(file)
                return serializer.to_dto(file_dict)


        except ImporterException as e:
            raise e
        except Exception as e:
            raise ImporterException(original_exception=e)

    @staticmethod
    def get_music_playlist_file_dto(music_playlist_file_location: Path) -> MusicPlaylistFileDTO:
        
        try:

            serializer = MusicPlaylistFileSerializer()

            with music_playlist_file_location.open(encoding='utf-8') as file:
                file_dict = json.load(file)
                return serializer.to_dto(file_dict)

        except ImporterException as e:
            raise e
        except Exception as e:
            raise ImporterException(original_exception=e)

    @staticmethod
    def get_tv_language_manifest(tv_language_manifest_location: Path) -> TVLanguageManifestFileDTO:
        
        try:

            serializer = TVLanguageManifestSerializer()

            with tv_language_manifest_location.open(encoding='utf-8') as file:
                file_dict = json.load(file)
                return serializer.to_dto(file_dict)

        except ImporterException as e:
            raise e
        except Exception as e:
            raise ImporterException(original_exception=e)

