import logging
import logging.config
import re


class TokenMaskingFilter(logging.Filter):
    def __init__(self, name=""):
        super().__init__(name)
        # Regex to match 'Token:' followed by any non-whitespace characters
        self.token_pattern = re.compile(r"(Token:\s*)(\S+)")

    def filter(self, record):
        # Mask tokens in the log message
        record.msg = self.mask_tokens(record.msg)
        return True

    def mask_tokens(self, message):
        """
        Replace any token-like strings with asterisks
        Supports both string and non-string messages
        """
        # Convert non-string messages to string
        if not isinstance(message, str):
            message = str(message)

        # Replace token strings with masked version
        def mask_token(match):
            prefix = match.group(1)  # 'Token: '
            token = match.group(2)  # actual token value
            return f"{prefix}{'*' * len(token)}"

        return self.token_pattern.sub(mask_token, message)
