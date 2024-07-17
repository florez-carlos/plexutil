from __future__ import annotations

from enum import Enum


class FileType(Enum):
    MP3 = "mp3"
    MP4 = "mp4"
    FLAC = "flac"
    MKV = "mkv"
    JSON = "json"
    UNKNOWN = ""

    @staticmethod
    # Forward Reference used here in type hint
    def get_all() -> list[FileType]:
        return [
            FileType.MP3,
            FileType.MP4,
            FileType.FLAC,
            FileType.MKV,
            FileType.JSON,
            FileType.UNKNOWN,
        ]

    @staticmethod
    def get_file_type_from_str(file_type_candidate: str) -> FileType:
        file_types = FileType.get_all()
        file_type_candidate = file_type_candidate.lower()

        for file_type in file_types:
            if file_type_candidate == file_type.value.lower():
                return file_type

        raise ValueError("File Type not supported: " + file_type_candidate)
