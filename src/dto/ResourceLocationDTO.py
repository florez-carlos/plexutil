from dataclasses import dataclass
from typing import List
import os

from enum.FileType import FileType

@dataclass(frozen=True)
class ResourceLocationDTO():

    drive: str = ""
    sep: str = os.path.sep
    uri_path_components: List[str] = []
    file_name: str = ""
    file_extension: FileType = FileType.UNKNOWN


    def build_uri(self) -> str:

        if os.name != 'nt' and self.drive:  # sys.platform == 'win32':
            raise ValueError("A drive has been set but this is not win32")
        elif os.name == 'nt' and not self.drive:  # sys.platform == 'win32':
            raise ValueError("A drive has not been set but this is win32 and drive is expected")

        uri = ""

        if self.drive:
            uri += (self.drive.upper() + ":") + self.sep
        elif not self.drive:
            uri +=  self.sep

        for uri_path_component in self.uri_path_components:
            uri += (uri_path_component + self.sep)

        if self.file_name and self.file_extension is FileType.UNKNOWN:
            raise ValueError("A file name has been set but no file extension has been set: "+self.file_name)
        if not self.file_name and self.file_extension is not FileType.UNKNOWN:
            raise ValueError("A file extension has been set but no file name has been set: "+self.file_extension.value)

        uri += (self.file_name+"."+self.file_extension.value)

        return uri


    def __eq__(self, other):

        if not isinstance(other, ResourceLocationDTO):
            return NotImplemented

        return self.drive == other.drive and self.sep == other.sep and self.uri_path_components == other.uri_path_components and self.file_name == other.file_name and self.file_extension is other.file_extension

    def __hash__(self):
        return hash((self.drive, self.sep, self.uri_path_components, self.file_name, self.file_extension))



