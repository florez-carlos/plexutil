class PlexUtilConfigError(Exception):
    def __init__(self, original_exception=None):
        self.original_exception = original_exception

        if self.original_exception:
            message = (
                "INVALID PLEX UTIL CONFIG | %s"
                % (self.original_exception.args[0])
            )
            self.__cause__ = original_exception
        else:
            message = "INVALID PLEX UTIL CONFIG"

        super().__init__(message)
