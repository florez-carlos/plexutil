from __future__ import annotations

from enum import Enum


class Language(Enum):
    ENGLISH = "en"
    ENGLISH_US = "en-US"
    SPANISH = "es"
    SPANISH_SPAIN = "es-ES"

    @staticmethod
    # Forward Reference used here in type hint
    def get_all() -> list[Language]:
        return [
            Language.ENGLISH,
            Language.ENGLISH_US,
            Language.SPANISH,
            Language.SPANISH_SPAIN,
        ]

    @staticmethod
    def get_language_from_str(language_candidate: str) -> Language:
        languages = Language.get_all()
        language_candidate = language_candidate.lower()

        for language in languages:
            if language_candidate == language.value.lower():
                return language

        raise ValueError("Language not supported: " + language_candidate)
