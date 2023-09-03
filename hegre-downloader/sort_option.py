from enum import Enum


class SortOption(Enum):
    MOST_RECENT = "most_recent"
    MOST_VIEWED = "most_viewed"
    TOP_RATED = "top_rated"
    VINTAGE = "vintage"  # only applicable for galleries

    def __str__(self) -> str:
        return self.value
