from __future__ import annotations

from typing import TYPE_CHECKING, cast

from plexapi.audio import Track
from plexapi.exceptions import NotFound
from plexapi.video import Movie, Show

from plexutil.core.prompt import Prompt
from plexutil.dto.dropdown_item_dto import DropdownItemDTO
from plexutil.dto.library_setting_dto import LibrarySettingDTO
from plexutil.dto.movie_dto import MovieDTO
from plexutil.dto.song_dto import SongDTO
from plexutil.dto.tv_series_dto import TVSeriesDTO
from plexutil.enums.server_setting import ServerSetting
from plexutil.exception.library_illegal_state_error import (
    LibraryIllegalStateError,
)
from plexutil.exception.unexpected_naming_pattern_error import (
    UnexpectedNamingPatternError,
)
from plexutil.model.music_playlist_entity import MusicPlaylistEntity
from plexutil.plex_util_logger import PlexUtilLogger
from plexutil.static import Static
from plexutil.util.icons import Icons
from plexutil.util.path_ops import PathOps

if TYPE_CHECKING:
    from pathlib import Path

    from plexapi.library import LibrarySection
    from plexapi.server import Playlist, PlexServer


class PlexOps(Static):
    @staticmethod
    def set_server_settings(
        plex_server: PlexServer,
    ) -> None:
        """
        Sets Plex Server Settings

        Args:
            plex_server (plexapi.server.PlexServer): A Plex Server instance

        Returns:
            None: This method does not return a value

        """
        server_settings = ServerSetting.get_all()

        for server_setting in server_settings:
            dropdown = server_setting.get_dropdown()
            is_from_server = False
            user_response = server_setting.get_default_selection()
            plex_setting = plex_server.settings.get(server_setting.get_name())
            if plex_setting:
                user_response = plex_setting.value
                is_from_server = True

                dropdown = PlexOps.override_dropdown_default(
                    dropdown=dropdown, value=user_response
                )
            response = Prompt.confirm_library_setting(
                library_setting=server_setting.to_dto(
                    is_from_server=is_from_server
                ),
            )
            plex_setting.set(response.user_response)

        plex_server.settings.save()

    @staticmethod
    def set_library_settings(
        plex_server: PlexServer,
        section: LibrarySection,
        settings: list[LibrarySettingDTO],
    ) -> None:
        """
        Sets Library Settings
        Logs a warning if setting doesn't exist

        Args:
            settings (LibrarySettingDTO): The Setting to apply to this Library

        Returns:
            None: This method does not return a value
        """
        for setting in settings:
            if setting.is_from_server:
                name = setting.name
                plex_setting = plex_server.settings.get(name)
                if plex_setting:
                    response = plex_setting.value

                    server_setting = LibrarySettingDTO(
                        name=setting.name,
                        display_name=setting.display_name,
                        description=setting.description,
                        user_response=response,
                        is_toggle=setting.is_toggle,
                        is_value=setting.is_value,
                        is_dropdown=setting.is_dropdown,
                        dropdown=setting.dropdown,
                        is_from_server=True,
                    )
                    response = Prompt.confirm_library_setting(server_setting)
                else:
                    description = (
                        f"{Icons.WARNING} Could not load library setting "
                        f"{name}\n"
                        f"Skipping -> {name}"
                    )
                    PlexUtilLogger.get_logger().warning(description)
                    continue
            else:
                response = Prompt.confirm_library_setting(setting)

            try:
                section.editAdvanced(**{response.name: response.user_response})
            except NotFound:
                description = (
                    f"{Icons.WARNING} Library Setting not accepted "
                    f"by the server: {response.name}\n"
                    f"Skipping -> {response.name}:{response.user_response}"
                )
                PlexUtilLogger.get_logger().warning(description)
                continue

    @staticmethod
    def override_dropdown_default(
        dropdown: list[DropdownItemDTO], value: bool | int | str
    ) -> list[DropdownItemDTO]:
        dropdown_no_default = []
        dropdown_default = []
        if dropdown:
            for item in dropdown:
                new_item = DropdownItemDTO()
                if item.is_default:
                    new_item = DropdownItemDTO(
                        display_name=item.display_name,
                        value=item.value,
                        is_default=False,
                    )
                else:
                    new_item = item
                dropdown_no_default.append(new_item)

            for item in dropdown_no_default:
                new_item = DropdownItemDTO()
                if item.value == value:
                    new_item = DropdownItemDTO(
                        display_name=item.display_name,
                        value=item.value,
                        is_default=True,
                    )
                else:
                    new_item = item
                dropdown_default.append(new_item)

        return dropdown_default

    @staticmethod
    def get_music_playlist_entity(playlist: Playlist) -> MusicPlaylistEntity:
        """
        Maps a plexapi.server.Playlist to a MusicPlaylsitEntity

        Args:
            playlist (plexapi.server.Playlist): A plex playlist

        Returns:
            MusicPlaylistEntity: Mapped from playlist
        """
        return MusicPlaylistEntity(name=playlist.title)

    @staticmethod
    def normalize_dto(
        dto: SongDTO | MovieDTO | TVSeriesDTO,
        media: list[Track] | list[Movie] | list[Show],
    ) -> SongDTO | MovieDTO | TVSeriesDTO:
        """
        Adds the missing properties to a DTO based on the information
        from a Plex Media in the server

        Args:
            dto (SongDTO, MovieDTO, TVSeriesDTO): The DTO to match against
            media ([Track|Movie|Show]): The plex media objects

        Returns:
            SongDTO | MovieDTO | TVSeriesDTO: A normalized DTO
        """

        for m in media:
            location = PathOps.get_path_from_str(m.locations[0])
            if isinstance(m, Track) and isinstance(dto, SongDTO):
                name = location.stem
                if name == dto.name:
                    return SongDTO(name=dto.name, location=location)
            elif isinstance(m, Movie) and isinstance(dto, MovieDTO):
                name, year = PathOps.get_show_name_and_year_from_str(
                    str(location)
                )
                if name == dto.name and year == dto.year:
                    return MovieDTO(name=name, year=year, location=location)
            elif isinstance(m, Show) and isinstance(dto, TVSeriesDTO):
                name, year = PathOps.get_show_name_and_year_from_str(
                    str(location)
                )
                if name == dto.name and year == dto.year:
                    return TVSeriesDTO(name=name, year=year, location=location)

        description = (
            f"Could not match a provided DTO to any Plex Media:\n{dto}\n"
        )
        raise ValueError(description)

    @staticmethod
    def get_dto_from_plex_media(
        media: Track | Movie | Show,
    ) -> SongDTO | MovieDTO | TVSeriesDTO:
        """
        Converts Track,Movie,Show to a corresponding DTO

        Args:
            media (Track|Movie|Show): The plex media object

        Returns:
            SongDTO | MovieDTO | TVSeriesDTO: The converted DTO from media

        Raise:
            ValueError: If Track/Movie location is not a file
            or Show location is a dir or media is not a Track/Movie/Show
        """
        location = PathOps.get_path_from_str(path_candidate=media.locations[0])
        if isinstance(media, Track):
            name = location.stem
            return SongDTO(name=name, location=location)
        elif isinstance(media, Movie):
            if location.is_file():
                try:
                    PathOps.get_show_name_and_year_from_str(
                        str(location.parent)
                    )
                    location = location.parent
                except UnexpectedNamingPatternError:
                    description = (
                        f"Found movie not nested in a dir: {location} "
                        f"| Proceeding with location as is"
                    )
                    PlexUtilLogger.get_logger().debug(description)
            name, year = PathOps.get_show_name_and_year_from_str(str(location))
            return MovieDTO(name=name, year=year, location=location)
        elif isinstance(media, Show):
            name, year = PathOps.get_show_name_and_year_from_str(str(location))
            return TVSeriesDTO(name=name, year=year, location=location)
        else:
            description = f"Unsupported Plex Media: {type(media)}"
            raise ValueError(description)

    @staticmethod
    def validate_local_files(
        plex_files: list[Track] | list[Show] | list[Movie] | list[Playlist],
        locations: list[Path],
    ) -> None:
        """
        Verifies that all local files match the provided plex tracks
        in the locations indicated

        Args:
            plex_files ([Track] | [Show] | [Movie] | [Playlist]): plexapi media
            locations ([Path]): local file locations.

        Returns:
            None: This method does not return a value

        Raises:
            LibraryIllegalStateError: if local files do not match plex files
            LibraryOpError: If plex_file type is not supported
        """
        if not plex_files:
            description = "Did not receive any Plex Files\n"
            raise ValueError(description)

        if all(isinstance(plex_file, Track) for plex_file in plex_files):
            songs = PathOps.get_local_songs(locations)
            _, unknown = PlexOps.filter_plex_media(
                cast("list[Track]", plex_files), songs
            )
        elif all(isinstance(plex_file, Show) for plex_file in plex_files):
            tv = PathOps.get_local_tv(locations)
            _, unknown = PlexOps.filter_plex_media(
                cast("list[Show]", plex_files), tv
            )
        elif all(isinstance(plex_file, Movie) for plex_file in plex_files):
            movies = PathOps.get_local_movies(locations)
            _, unknown = PlexOps.filter_plex_media(
                cast("list[Movie]", plex_files), movies
            )
        else:
            description = "Expected to find Tracks, Movies or Shows"
            raise ValueError(description)

        if unknown:
            description = "These local files are unknown to the plex server:\n"
            for u in unknown:
                description = description + f"-> {u!s}\n"
            PlexUtilLogger.get_logger().debug(description)

            raise LibraryIllegalStateError(description)

    @staticmethod
    def filter_plex_media(
        plex_media: list[Movie] | list[Track] | list[Show],
        dtos: list[MovieDTO] | list[SongDTO] | list[TVSeriesDTO],
    ) -> tuple[
        list[MovieDTO] | list[SongDTO] | list[TVSeriesDTO],
        list[MovieDTO] | list[SongDTO] | list[TVSeriesDTO],
    ]:
        """
        Filters the provided Plex media with the provided dtos

        Args:
            plex_media ([
            plexapi.video.Movie |
            plexapi.video.Show |
            plexapi.audio.Track]): A list of plex media to compare against

            plexapi movies
            dtos ([
            MovieDTO |
            SongDTO |
            TVSeriesDTO]): Dtos to match against plex media

        Returns:
            A tuple of:
            1) DTOs that match the provided plex media
            2) DTOS that did not match to any plex media
        """
        filtered_media = []
        unknown_media = []

        plex_media_dto = [
            PlexOps.get_dto_from_plex_media(media) for media in plex_media
        ]

        for dto in dtos:
            if dto not in plex_media_dto:
                unknown_media.append(dto)
            else:
                filtered_media.append(dto)

        return filtered_media, unknown_media
