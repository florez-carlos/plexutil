from __future__ import annotations

import re
from pathlib import Path

from plexutil.dto.local_file_dto import LocalFileDTO
from plexutil.dto.movie_dto import MovieDTO
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
        path_candidate_name: str = "",
        is_dir: bool = False,
        is_file: bool = False,
    ) -> Path:
        if not path_candidate:
            description = (
                "Expected a path candidate "
                f"for {path_candidate_name} but none supplied"
            )
            raise ValueError(description)

        path = Path(path_candidate)

        if not path.exists():
            description = (
                f"Path candidate for {path_candidate_name} does "
                f"not exist {path_candidate}"
            )
            raise ValueError(description)
        elif is_dir and not path.is_dir():
            description = (
                f"Expected a dir for {path_candidate_name} but path candidate "
                f"is not a dir {path_candidate}"
            )
            raise ValueError(description)
        elif is_file and not path.is_file():
            description = (
                f"Expected a file for {path_candidate_name} but path "
                f"candidate is not a file {path_candidate}"
            )
            raise ValueError(description)

        return path

    @staticmethod
    def __walk_tv_structure(
        show_name: str, first_aired_year: int, path: Path
    ) -> tuple[list[TVEpisodeDTO], list[str]]:
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
        episodes = []

        for path in paths:
            if not path.is_dir():
                description = f"Expected to encounter a directory: {path}!s"
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
    def get_local_movie(paths: list[Path]) -> list[MovieDTO]:
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
    def get_local_files(paths: list[Path]) -> list[LocalFileDTO]:
        files = []

        for path in paths:
            if path.is_file():
                file_name = path.stem
                file_extension = path.suffix.rsplit(".")[1]

                files.append(
                    LocalFileDTO(
                        name=file_name,
                        extension=FileType.get_file_type_from_str(
                            file_extension
                        ),
                        location=path,
                    )
                )
            else:
                for item in path.iterdir():
                    if item.is_file():
                        file_name = item.stem
                        file_extension = item.suffix.rsplit(".")[1]
                        files.append(
                            LocalFileDTO(
                                name=file_name,
                                extension=FileType.get_file_type_from_str(
                                    file_extension
                                ),
                                location=item,
                            )
                        )

        return files

    @staticmethod
    def get_show_name_and_year_from_str(candidate: str) -> tuple[str, int]:
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
        return Path(__file__).parent.parent.parent
