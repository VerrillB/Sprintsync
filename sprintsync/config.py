"""Load SprintSync settings from environment variables or a local .env file.

Owner: John Reymond G. Pascual
"""

import os

from dotenv import load_dotenv

REQUIRED_VARS = [
    "TRELLO_KEY",
    "TRELLO_TOKEN",
    "TRELLO_BOARD_ID",
    "WEBEX_BOT_TOKEN",
    "WEBEX_ROOM_ID",
]

OPTIONAL_VARS = {
    "NETCONF_HOST": "",
    "NETCONF_PORT": "830",
    "NETCONF_USER": "",
    "NETCONF_PASS": "",
}


class ConfigError(Exception):
    """Raised when a required setting is missing."""


def load_config(env_file=".env"):
    """Return a dict of settings. Raise ConfigError if a required one is missing."""
    load_dotenv(env_file)
    missing = [name for name in REQUIRED_VARS if not os.getenv(name)]
    if missing:
        raise ConfigError(
            "Missing settings: " + ", ".join(missing)
            + ". Copy .env.example to .env and fill them in."
        )
    config = {name: os.getenv(name) for name in REQUIRED_VARS}
    for name, default in OPTIONAL_VARS.items():
        config[name] = os.getenv(name, default)
    return config
