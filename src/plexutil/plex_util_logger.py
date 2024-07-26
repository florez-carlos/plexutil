import logging

# ruff: noqa: ANN002, ANN003, ANN204, RUF012
import logging.config
from datetime import datetime, timezone
from pathlib import Path

from plexutil.util.file_importer import FileImporter
from plexutil.util.path_ops import PathOps


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class PlexUtilLogger(metaclass=SingletonMeta):
    def __init__(self, log_dir: Path) -> None:
        if not hasattr(self, "initialized"):  # Avoid reinitialization
            # Time data in UTC required by date named log files
            day = str(datetime.now(timezone.utc).day)
            month = str(datetime.now(timezone.utc).month)
            year = str(datetime.now(timezone.utc).year)

            log_file_name = f"{month}-{day}-{year}.log"
            logging_config_path = (
                PathOps.get_project_root()
                / "src"
                / "plexutil"
                / "config"
                / "log_config.yaml"
            )
            # Load YAML config
            logging_config = FileImporter.get_logging_config(
                logging_config_path
            )
            # Rewrite contents of YAML config to accomodate
            # for date based log file names
            logging_config["handlers"]["regular_file_handler"]["filename"] = (
                log_dir / log_file_name
            )
            # Load config with changes as Dict
            logging.config.dictConfig(logging_config)
            # Initialize loggers
            self.logger = logging.getLogger("regular")
            self.initialized = True

    @classmethod
    def get_logger(cls) -> logging.Logger:
        instance = cls._instances[cls]
        return instance.logger
