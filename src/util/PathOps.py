from pathlib import Path

from src.Static import Static


class PathOps(Static):

    @staticmethod
    def get_path_from_str(path_candidate: str, path_candidate_name: str = "", is_dir: bool = False, is_file: bool = False) -> Path:

        try:
            
            if not path_candidate:
                raise ValueError("Expected a path candidate for %s but none supplied" % (path_candidate_name))

            path = Path(path_candidate)
            
            if not path.exists():
                raise ValueError("Path candidate for %s does not exist %s" % (path_candidate_name, path_candidate))
            elif is_dir and not path.is_dir():
                raise ValueError("Expected a dir for %s but path candidate is not a dir %s" % (path_candidate_name, path_candidate))
            elif is_file and not path.is_file():
                raise ValueError("Expected a file for %s but path candidate is not a file %s" % (path_candidate_name, path_candidate))

            return path
            
        except:
            raise

    @staticmethod
    def get_project_root() -> Path:
        return Path(__file__).parent.parent.parent

