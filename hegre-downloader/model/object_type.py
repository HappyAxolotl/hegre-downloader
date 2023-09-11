from __future__ import annotations

from enum import Enum


class ObjectType(Enum):
    FILM = "films"
    MASSAGE = "massage"
    SEXED = "sexed"
    PHOTOS = "photos"

    def __str__(self) -> str:
        return self.value

    @staticmethod
    def from_str(type_str: str) -> ObjectType:
        match type_str:
            case ObjectType.FILM.value:
                return ObjectType.FILM
            case ObjectType.MASSAGE.value:
                return ObjectType.MASSAGE
            case ObjectType.SEXED.value:
                return ObjectType.SEXED
            case ObjectType.PHOTOS.value:
                return ObjectType.PHOTOS
            case _:
                raise ValueError(f"Invalid Hegre object type string '{type_str}'")
