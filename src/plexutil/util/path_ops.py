from pathlib import Path

from plexutil.dto.local_file_dto import LocalFileDTO
from plexutil.enums.file_type import FileType
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
    def get_local_files(paths: list[Path]) -> list[LocalFileDTO]:
        files = []

        filtered_paths = []
        for path in paths:
            if isinstance(path, Path):
                filtered_paths.append(path)
            elif isinstance(path, str):
                filtered_paths.append(Path(path))
            else:
                description = f"Unsupported local file type: {type(path)!s}"
                raise ValueError(description)

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
    def get_project_root() -> Path:
        return Path(__file__).parent.parent.parent
