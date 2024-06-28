class LibraryOpException(Exception):
    def __init__(self, op_type: str = "UNKNOWN", description: str = "", original_exception=None):

        self.original_exception = original_exception

        if self.original_exception:
            message = "LIBRARY %s EXCEPTION | %s" % (op_type, self.original_exception.args[0])
            self.__cause__ = original_exception
        else:
            message = "LIBRARY %s EXCEPTION | %s" % (op_type, description)

        super().__init__(message)
