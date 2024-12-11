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
    def get_from_str(candidate: str) -> Language:
        languages = Language.get_all()

        for language in languages:
            if candidate.lower() == language.value.lower():
                return language

        description = f"Language not supported: {candidate}"
        raise ValueError(description)
