class ImporterError(Exception):
    def __init__(self, description: str = "", original_exception=None):
        self.original_exception = original_exception

        if self.original_exception:
            message = (
                "IMPORTER EXCEPTION | %s" % (self.original_exception.args[0])
            )
            self.__cause__ = original_exception
        else:
            message = "IMPORTER EXCEPTION | %s" % (description)

        super().__init__(message)
