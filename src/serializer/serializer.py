from __future__ import annotations

from abc import ABC, abstractmethod

from src.serializer.serializable import Serializable


class Serializer(ABC):
    @abstractmethod
    def to_json(self, serializable: Serializable) -> dict:
        pass

    @abstractmethod
    def to_dto(self, json_dict: dict) -> Serializable:
        pass
