from __future__ import annotations

import urllib.parse
from pathlib import Path


class QueryBuilder:
    def __init__(self, path: str = "", **kwargs) -> None:  # noqa: ANN003
        self.path = path
        self.query_parameters = kwargs

    def build(self) -> str:
        result = self.path

        if self.query_parameters:
            result += "?"

        result += self.__walk__(self.query_parameters)

        # Remove the last &
        if self.query_parameters:
            result = result[:-1]

        return result

    def __walk__(
        self,
        path: dict[str, str]
        | dict[str, bool]
        | dict[str, int]
        | dict[str, dict]
        | None = None,
        nested_parent_name: str = "",
    ) -> str:
        result = ""

        if path is None:
            path = {}

        for k, v in path.items():
            if k.startswith("location"):
                k = "location" # noqa: PLW2901
            if k == "the_type":
                k = "type"  # noqa: PLW2901

            if isinstance(v, bool):
                v = "1" if v else "0"  # noqa: PLW2901

            if isinstance(v, int) | isinstance(v, Path):
                v = str(v)  # noqa: PLW2901

            if isinstance(v, dict):
                result += self.__walk__(v, k)
                continue


            v = urllib.parse.quote(str(v))  # noqa: PLW2901 

            if nested_parent_name:
                bracket_open = urllib.parse.quote("[")
                bracket_close = urllib.parse.quote("]")
                result += (
                    nested_parent_name
                    + bracket_open
                    + k
                    + bracket_close
                    + "="
                    + v
                    + "&"
                )
                continue

            result += k + "=" + v + "&"

        return result
