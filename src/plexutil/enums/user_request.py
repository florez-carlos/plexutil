from __future__ import annotations

from enum import Enum


class UserRequest(Enum):
    SETTINGS = ("settings", "Modify Plex Server Settings")
    CREATE = ("create", "Movie, Music, TV Libraries or Music Playlist")
    MODIFY = ("modify", "An existing library or music playlist")
    DELETE = ("delete", "An existing library or music playlist")
    DOWNLOAD = (
        "download",
        "A music playlist, saved as playlist.db file in current dir",
    )
    UPLOAD = (
        "upload",
        "A music playlist, reads a playlist.db file in current dir",
    )
    DISPLAY = ("display", "List the items in a library")
    UPDATE = (
        "update",
        (
            "Perform an update on a library and poll for # of items "
            "while update is in progress"
        ),
    )
    CHANGELOG = (
        "changelog",
        "Display a server update changelog if an update is available",
    )

    @staticmethod
    # Forward Reference used here in type hint
    def get_all() -> list[UserRequest]:
        return list(UserRequest)

    @staticmethod
    def get_from_str(candidate: str) -> UserRequest:
        requests = UserRequest.get_all()

        for request in requests:
            if candidate.lower() == request.get_value().lower():
                return request

        description = f"Request not supported: {candidate}"
        raise ValueError(description)

    def get_display_name(self) -> str:
        return self.value[1]

    def get_value(self) -> str:
        return self.value[0]
