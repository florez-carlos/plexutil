from __future__ import annotations

from dataclasses import dataclass


# Frozen=True creates an implicit hash method, eq is created by default
@dataclass(frozen=True)
class LibrarySettingDropdownItemDTO:
    display_name: str = ""
    value: int | str = 0
