from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BootstrapPathsDTO:
    config_dir: Path
    log_dir: Path
    plexutil_config_file: Path

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BootstrapPathsDTO):
            return False

        return (
            self.config_dir == other.config_dir
            and self.log_dir == other.log_dir
            and self.plexutil_config_file == other.plexutil_config_file
        )

    def __hash__(self) -> int:
        return hash((self.config_dir, self.log_dir, self.plexutil_config_file))
