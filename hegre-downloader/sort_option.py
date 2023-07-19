from enum import Enum


class SortOption(Enum):
    MOST_RECENT = "most_recent"
    MOST_VIEWED = "most_viewed"
    TOP_RATED = "top_rated"

    def __str__(self) -> str:
        return self.value
