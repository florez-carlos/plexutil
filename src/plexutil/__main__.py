import sys

from plexutil.core.auth import Auth
from plexutil.core.library_factory import LibraryFactory
from plexutil.core.prompt import Prompt
from plexutil.dto.dropdown_item_dto import DropdownItemDTO
from plexutil.enums.user_request import UserRequest
from plexutil.exception.bootstrap_error import BootstrapError
from plexutil.exception.library_illegal_state_error import (
    LibraryIllegalStateError,
)
from plexutil.exception.library_op_error import LibraryOpError
from plexutil.exception.library_poll_timeout_error import (
    LibraryPollTimeoutError,
)
from plexutil.exception.library_section_missing_error import (
    LibrarySectionMissingError,
)
from plexutil.exception.unexpected_argument_error import (
    UnexpectedArgumentError,
)
from plexutil.exception.user_error import UserError
from plexutil.plex_util_logger import PlexUtilLogger
from plexutil.util.file_importer import FileImporter
from plexutil.util.plex_ops import PlexOps


def main() -> None:
    try:
        bootstrap_paths_dto = FileImporter.bootstrap()
        user_request = Prompt.get_user_request()
        auth = Auth.get_resources(bootstrap_paths_dto)
        dropdown = [
            DropdownItemDTO(display_name=f"{x.name} - {x.device}", value=x)
            for x in auth
            if x.product == "Plex Media Server"
        ]
        user_response = Prompt.draw_dropdown(
            "Available Servers", "Choose a server to connect to", dropdown
        )
        plex_server = user_response.value.connect()

        if user_request is UserRequest.SETTINGS:
            PlexOps.set_server_settings(plex_server=plex_server)
        else:
            library = LibraryFactory.get(
                user_request=user_request,
                plex_server=plex_server,
                bootstrap_paths_dto=bootstrap_paths_dto,
            )
            library.do()

    except SystemExit as e:
        if e.code == 0:
            description = "Successful System Exit"
            PlexUtilLogger.get_logger().debug(description)
        else:
            description = f"\n=====Unexpected Error=====\n{e!s}"
            PlexUtilLogger.get_logger().exception(description)
            raise

    except UserError as e:
        sys.tracebacklimit = 0
        description = f"\n=====User Error=====\n{e!s}"
        PlexUtilLogger.get_logger().error(description)
        sys.exit(1)

    except LibraryIllegalStateError as e:
        sys.tracebacklimit = 0
        description = f"\n=====Library Illegal State Error=====\n{e!s}"
        PlexUtilLogger.get_logger().error(description)
        sys.exit(1)

    except LibraryOpError as e:
        sys.tracebacklimit = 0
        description = f"\n=====Library Operation Error=====\n{e!s}"
        PlexUtilLogger.get_logger().error(description)
        sys.exit(1)

    except LibraryPollTimeoutError as e:
        sys.tracebacklimit = 0
        description = f"\n=====Library Poll Tiemout Error=====\n{e!s}"
        PlexUtilLogger.get_logger().error(description)
        sys.exit(1)

    except LibrarySectionMissingError as e:
        sys.tracebacklimit = 0
        description = f"\n=====Library Not Found Error=====\n{e!s}"
        PlexUtilLogger.get_logger().error(description)
        sys.exit(1)

    except UnexpectedArgumentError as e:
        sys.tracebacklimit = 0
        description = (
            "\n=====User Argument Error=====\n"
            "These arguments are unrecognized: \n"
        )
        for argument in e.args[0]:
            description += "-> " + argument + "\n"
        PlexUtilLogger.get_logger().error(description)
        sys.exit(1)

    # No regular logger can be expected to be initialized
    except BootstrapError as e:
        description = f"\n=====Program Initialization Error=====\n{e!s}"
        e.args = (description,)
        raise

    except Exception as e:  # noqa: BLE001
        description = f"\n=====Unexpected Error=====\n{e!s}"
        PlexUtilLogger.get_logger().exception(description)


if __name__ == "__main__":
    main()
