from __future__ import annotations

from enum import Enum


class UserRequest(Enum):
    SETTINGS = "settings"
    CREATE = "create"
    MODIFY = "modify"
    DELETE = "delete"
    DOWNLOAD = "download"
    UPLOAD = "upload"
    CHANGE_SHOW_LANGUAGE = "change_show_language"
    DISPLAY = "display"
    UPDATE = "update"

    @staticmethod
    # Forward Reference used here in type hint
    def get_all() -> list[UserRequest]:
        return list(UserRequest)

    @staticmethod
    def get_user_request_from_str(
        user_request_candidate: str,
    ) -> UserRequest:
        requests = UserRequest.get_all()
        user_request_candidate = user_request_candidate.lower()

        for request in requests:
            if (
                user_request_candidate == request.value
                or user_request_candidate.replace("_", " ") == request.value
            ):
                return request

        raise ValueError("Request not supported: " + user_request_candidate)
