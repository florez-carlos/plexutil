from pathlib import Path

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
    def get_project_root() -> Path:
        return Path(__file__).parent.parent.parent
