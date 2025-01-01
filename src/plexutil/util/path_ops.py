from __future__ import annotations

import re
from pathlib import Path

from plexutil.dto.movie_dto import MovieDTO
from plexutil.dto.song_dto import SongDTO
from plexutil.dto.tv_episode_dto import TVEpisodeDTO
from plexutil.enums.file_type import FileType
from plexutil.exception.unexpected_naming_pattern_error import (
    UnexpectedNamingPatternError,
)
from plexutil.plex_util_logger import PlexUtilLogger
from plexutil.static import Static


class PathOps(Static):
    @staticmethod
    def get_path_from_str(
        path_candidate: str,
        is_dir_expected: bool = False,
        is_file_expected: bool = False,
    ) -> Path:
        """
        Get pathlib.Path from a str

        Args:
            path_candidate (str): The likely Path
            is_dir_expected (bool): Is the path expected to be a dir?
            is_file_expected (bool): Is the path expected to be a file?

        Returns:
            A pathlib.Path

        Raises:
            ValueError: If path_candidate is not supplied or path doesn't exist
            or path does not meet is_dir_expected/is_file_expected condition
        """
        if not path_candidate:
            description = "Expected a path candidate but none supplied "
            raise ValueError(description)

        path = Path(path_candidate)

        if not path.exists():
            description = f"Path candidate ({path_candidate}) does not exist"
            raise ValueError(description)

        if is_dir_expected and not path.is_dir():
            description = (
                f"Expected a dir for ({path_candidate}) but this is not a dir"
            )
            raise ValueError(description)

        if is_file_expected and not path.is_file():
            description = (
                f"Expected a file for ({path_candidate}) but path not a file"
                f"candidate is not a file {path_candidate}"
            )
            raise ValueError(description)

        return path

    @staticmethod
    def __walk_tv_structure(
        show_name: str, first_aired_year: int, path: Path
    ) -> tuple[list[TVEpisodeDTO], list[str]]:
        """
        *Private refer to PathOps.get_local_tv()
        Walks subdirectories in search of TV episodes
        A TV episode is expected to have a file name with a pattern
        of S##E##

        Args:
            show_name (str): The name of the TV show
            first_aired_year (int): The year of the TV show
            path (pathlib.Path): The parent directory of the TV show

        Returns:
            A tuple of:
            1) [TVEpisodeDTO] for each file found and understood as an episode
            2) [str] The name of the files encountered that were not
            understood as episodes
        """
        episodes = []
        unknown = []

        children = path.rglob("*")
        for child in children:
            if child.is_dir():
                sub_episodes, sub_unknown = PathOps.__walk_tv_structure(
                    show_name, first_aired_year, child
                )
                episodes.extend(sub_episodes)
                unknown.extend(sub_unknown)
            elif child.is_file():
                try:
                    tv_episode_dto = PathOps.get_episode_from_str(
                        show_name=show_name,
                        first_aired_year=first_aired_year,
                        candidate=child.stem,
                    )
                    episodes.append(tv_episode_dto)
                except UnexpectedNamingPatternError:
                    unknown.append(child.stem)

        return episodes, unknown

    @staticmethod
    def get_local_tv(paths: list[Path]) -> list[TVEpisodeDTO]:
        """
        Scans local directories in search of TV episodes
        A TV episode is expected to have a file name with a pattern of S##E##
        and a parent directory with a pattern of <series_name> (<year>)

        Expects to see:
        <series_name> (<year>) *directory
            |- S01E01
            |- S01E02
            ...

        Args:
            paths (pathlib.Path): The directories to scan

        Returns:
            [TVEpisodeDTO]: Found episodes

        Raises:
            ValueError: If any of the parent paths is not a directory
        """
        episodes = []

        for path in paths:
            if not path.is_dir():
                description = f"Expected to encounter a directory: {path!s}"
                raise ValueError(description)

            name, year = PathOps.get_show_name_and_year_from_str(path.name)
            known, unknown = PathOps.__walk_tv_structure(name, year, path)
            description = (
                f"Evaluated TV Series: {name}\n"
                f"Understood {len(known)} episodes\n"
                f"Did not understand: {len(unknown)} episodes:\n"
                f"{unknown}"
            )
            PlexUtilLogger.get_logger().debug(unknown)
            episodes.extend(known)

        return episodes

    @staticmethod
    def get_local_movies(paths: list[Path]) -> list[MovieDTO]:
        """
        Scans local directories in search of movies
        A movie is expected to have a file name or directory name
        with a pattern of name (year) -optional arbitrary text-

        Args:
            paths (pathlib.Path): The directories to scan

        Returns:
            [MovieDTO]: Found movies
        """
        movies = []
        for path in paths:
            if path.is_dir():
                file_name = path.name
                file_extension = FileType.UNKNOWN
            else:
                file_name = path.stem
                file_extension = FileType.get_file_type_from_str(
                    path.suffix.replace(".", "")
                )

            name, year = PathOps.get_show_name_and_year_from_str(file_name)
            movies.append(
                MovieDTO(name=name, year=year, extension=file_extension)
            )

        return movies

    @staticmethod
    def get_local_songs(paths: list[Path]) -> list[SongDTO]:
        """
        Scans local directories in search of songs
        Songs are expected to be grouped in the same parent directory

        songs (dir)
          |-> song.mp3
          |-> another_song.flac

        Args:
            paths (pathlib.Path): The directories to scan

        Returns:
            [SongDTO]: Found songs

        """
        files = []

        for path in paths:
            if path.is_file():
                file_name = path.stem
                file_extension = path.suffix.rsplit(".")[1]

                files.append(
                    SongDTO(
                        name=file_name,
                        extension=FileType.get_file_type_from_str(
                            file_extension
                        ),
                    )
                )
            elif path.is_dir():
                return PathOps.get_local_songs(list(path.iterdir()))
            else:
                description = f"Expected to find a file but got: {path!s}"
                raise UnexpectedNamingPatternError(description)

        return files

    @staticmethod
    def get_show_name_and_year_from_str(candidate: str) -> tuple[str, int]:
        """
        Extracts Show name and year from a str,
        expects to find <show_name> (<year>) pattern

        Args:
            candidate (str): The likely show_name,year

        Returns:
            A tuple of:
            1) show name
            2) year

        Raises:
            UnexpectedNamingPatternError: If candiate str does not match
            the expected parttern

        """
        pattern = r"([a-zA-Z\s]+)\s\((\d{4})\)"
        match = re.search(pattern, candidate)

        if match:
            show_name = match.group(1)
            year = match.group(2)
        else:
            description = (
                f"Could not extract show name, year from: {candidate}\n"
                f"Expected to see a 'show_name (year)' pattern"
            )
            raise UnexpectedNamingPatternError(description)

        return show_name.lower(), int(year)

    @staticmethod
    def get_episode_from_str(
        show_name: str, first_aired_year: int, candidate: str
    ) -> TVEpisodeDTO:
        """
        Extracts season, episode numbers from a str,
        expects to find a S#E# pattern

        Args:
            show_name (str): The name of the TV show (case insensitive)
            first_aired_year (int): Year of first airing
            candidate (str): Episode info (case insensitive)

        Returns:
            TVEpisodeDTO: Poulated with the supplied name and season, episode

        Raises:
            ValueError: If S#E# naming pattern not present in candidate
        """

        match = re.search(r"s(\d{2})e(\d{2})", candidate, re.IGNORECASE)

        if match:
            season = int(match.group(1))
            episode = int(match.group(2))
            return TVEpisodeDTO(
                name=show_name,
                first_aired_year=first_aired_year,
                season=season,
                episode=episode,
            )

        else:
            description = f"Did not understand this as an episode: {candidate}"
            raise UnexpectedNamingPatternError(description)

    @staticmethod
    def get_project_root() -> Path:
        """
        Gets the root of this project

        Returns:
            pathlib.Path: The project's root
        """
        return Path(__file__).parent.parent.parent
