import sys

from jsonschema.exceptions import ValidationError
from peewee import DoesNotExist
from plexapi.server import PlexServer

from plexutil.core.library_factory import LibraryFactory
from plexutil.core.prompt import Prompt
from plexutil.core.server_config import ServerConfig
from plexutil.dto.library_preferences_dto import LibraryPreferencesDTO
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
from plexutil.exception.server_config_error import ServerConfigError
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
        instructions_dto = Prompt.get_user_instructions_dto()
        request = instructions_dto.request
        server_config_dto = instructions_dto.server_config_dto
        config = ServerConfig(bootstrap_paths_dto, server_config_dto)

        if request == UserRequest.CONFIG:
            server_config_dto = config.save()
            sys.exit(0)
        else:
            try:
                server_config_dto = config.get()
            except DoesNotExist as e:
                description = "No Server Config found"
                raise ServerConfigError(description) from e

        host = server_config_dto.host
        port = server_config_dto.port
        token = server_config_dto.token

        if (
            instructions_dto.is_show_configuration
            | instructions_dto.is_show_configuration_token
        ):
            if request:
                description = (
                    f"Received a request: '{request.value}' but also a call "
                    f"to show configuration?\n"
                    f"plexutil -sc OR plexutil -sct to show the token\n"
                )

                raise UserError(description)  # noqa: TRY301

            description = (
                "\n=====Server Configuration=====\n"
                "To update the configuration: plexutil config -token ...\n\n"
                f"Host: {host}\n"
                f"Port: {port}\n"
                f"Token: "
            )
            if instructions_dto.is_show_configuration_token:
                description = (
                    description + f"{token if token else 'NOT SUPPLIED'}\n"
                )
            else:
                description = (
                    description + "\n\nINFO: To show token use"
                    "--show_configuration_token\n"
                )

            PlexUtilLogger.get_console_logger().info(description)

            sys.exit(0)

        if not token:
            description = (
                "Plex Token has not been supplied, cannot continue\n"
                "Set a token -> plexutil config -token ..."
            )
            raise ServerConfigError(description)  # noqa: TRY301

        baseurl = f"http://{host}:{port}"
        plex_server = PlexServer(baseurl, token)

        if instructions_dto.request is UserRequest.SET_SERVER_SETTINGS:
            preferences_dto = LibraryPreferencesDTO()
            PlexOps.set_server_settings(plex_server, preferences_dto)
        else:
            library = LibraryFactory.get(
                user_instructions_dto=instructions_dto,
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

    except ServerConfigError as e:
        sys.tracebacklimit = 0
        description = f"\n=====Server Config Error=====\n{e!s}"
        PlexUtilLogger.get_logger().error(description)
        sys.exit(1)

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

    except ValidationError as e:
        sys.tracebacklimit = 0
        description = f"\n=====Invalid Schema Error=====\n{e!s}"
        PlexUtilLogger.get_logger().error(description)

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
