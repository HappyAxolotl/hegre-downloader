from __future__ import annotations

from enum import Enum


class MovieType(Enum):
    FILM = "films"
    MASSAGE = "massage"
    SEXED = "sexed"

    def __str__(self) -> str:
        return self.value

    @staticmethod
    def from_str(type_str: str) -> MovieType:
        match type_str:
            case MovieType.FILM.value:
                return MovieType.FILM
            case MovieType.MASSAGE.value:
                return MovieType.MASSAGE
            case MovieType.SEXED.value:
                return MovieType.SEXED
            case _:
                raise ValueError(f"Invalid movie type string '{type_str}'")
