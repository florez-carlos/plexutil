from abc import ABC, abstractmethod

from peewee import Model

from plexutil.mapper.mappable_dto import MappableDTO
from plexutil.mapper.mappable_entity import MappableEntity


class Mapper(ABC):
    @abstractmethod
    def get_dto(self, entity: Model) -> MappableDTO:
        pass

    @abstractmethod
    def get_entity(self, dto: MappableDTO) -> MappableEntity:
        pass
