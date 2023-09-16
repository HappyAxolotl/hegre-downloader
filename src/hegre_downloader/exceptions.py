class HegreError(Exception):
    def __init__(self, message):
        super().__init__(message)


class MovieAlreadyDownloaded(HegreError):
    """The movie has already been downloaded"""
