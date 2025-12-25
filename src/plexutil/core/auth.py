from plexapi.myplex import MyPlexAccount, MyPlexJWTLogin, MyPlexResource

from plexutil.dto.bootstrap_paths_dto import BootstrapPathsDTO
from plexutil.exception.auth_error import AuthError
from plexutil.plex_util_logger import PlexUtilLogger
from plexutil.static import Static
from plexutil.util.file_importer import FileImporter


class Auth(Static):
    @staticmethod
    def get_resources(
        bootstrap_paths_dto: BootstrapPathsDTO,
    ) -> list[MyPlexResource]:
        private_key_path = bootstrap_paths_dto.private_key_dir
        public_key_path = bootstrap_paths_dto.public_key_dir
        token_path = bootstrap_paths_dto.token_dir

        if (
            not private_key_path.exists()
            or not public_key_path.exists()
            or not token_path.exists()
        ):
            jwt_login = MyPlexJWTLogin(
                oauth=True,
            )
            jwt_login.generateKeypair(
                keyfiles=(f"{private_key_path!s}", f"{public_key_path!s}"),
                overwrite=True,
            )
            url = jwt_login.oauthUrl()
            description = f"\n========== Login ==========\nLogin here: {url}\n"
            PlexUtilLogger.get_console_logger().info(description)
            jwt_login.run()
            jwt_login.waitForLogin()
            token = jwt_login.jwtToken

            if isinstance(token, str):
                FileImporter.save_jwt(bootstrap_paths_dto.token_dir, token)
            else:
                description = "Did not receive a token"
                raise AuthError(description)

            account = MyPlexAccount(token=token)
            return account.resources()
        else:
            token = FileImporter.get_jwt(bootstrap_paths_dto.token_dir)
            jwt_login = MyPlexJWTLogin(
                token=token,
                keypair=(f"{private_key_path!s}", f"{public_key_path!s}"),
            )
            jwt_login.registerDevice()
            token = jwt_login.refreshJWT()

            account = MyPlexAccount(token=token)
            return account.resources()
