"""Declare all global constants."""

COMMANDS = {
    "start": "Check whether the bot is alive",
    "forward": "Set a new forward",
    "remove": "Remove an existing forward",
    "help": "Learn usage",
}

REGISTER_COMMANDS = True

KEEP_LAST_MANY = 10000

CONFIG_FILE_NAME = "phoenixtgfw.config.json"
CONFIG_ENV_VAR_NAME = "PHOENIXTGFW_CONFIG"

MONGO_DB_NAME = "phoenixtgfw-config"
MONGO_COL_NAME = "phoenixtgfw-instance-0"
