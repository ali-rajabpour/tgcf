"""Load all user defined config and env vars."""

import logging
import os
import sys
from typing import Dict, List, Optional, Union, Any

from dotenv import load_dotenv
from pydantic import BaseModel, validator  # pylint: disable=no-name-in-module
from pymongo import MongoClient
from telethon import TelegramClient
from telethon.sessions import StringSession

from tgcf import storage as stg
from tgcf.const import CONFIG_FILE_NAME
from tgcf.plugin_models import PluginConfig

pwd = os.getcwd()
env_file = os.path.join(pwd, ".env")

# Check if we're running in Docker with the config directory
config_dir = os.path.join(pwd, "config")
docker_config_path = "/app/config"
if os.path.isdir(docker_config_path):
    CONFIG_DIR = docker_config_path
elif os.path.isdir(config_dir):
    CONFIG_DIR = config_dir
else:
    CONFIG_DIR = pwd

load_dotenv(env_file)


class Forward(BaseModel):
    """Blueprint for the forward object."""

    # pylint: disable=too-few-public-methods
    con_name: str = ""
    use_this: bool = True
    source: Union[int, str] = ""
    dest: List[Union[int, str]] = []
    offset: int = 0
    end: Optional[int] = 0


class LiveSettings(BaseModel):
    """Settings to configure how tgcf operates in live mode."""

    # pylint: disable=too-few-public-methods
    sequential_updates: bool = False
    delete_sync: bool = False
    delete_on_edit: Optional[str] = ".deleteMe"


class PastSettings(BaseModel):
    """Configuration for past mode."""

    # pylint: disable=too-few-public-methods
    delay: int = 0

    @validator("delay")
    def validate_delay(cls, val):  # pylint: disable=no-self-use,no-self-argument
        """Check if the delay used by user is values. If not, use closest logical values."""
        if val not in range(0, 101):
            logging.warning("delay must be within 0 to 100 seconds")
            if val > 100:
                val = 100
            if val < 0:
                val = 0
        return val


class LoginConfig(BaseModel):

    API_ID: int = 0
    API_HASH: str = ""
    user_type: int = 0  # 0:bot, 1:user
    phone_no: int = 91
    USERNAME: str = ""
    SESSION_STRING: str = ""
    BOT_TOKEN: str = ""


class BotMessages(BaseModel):
    start: str = "Phoenix is Flying!"
    bot_help: str = "https://github.com/ali-rajabpour/Phoenix-TGFW"


class Config(BaseModel):
    """The blueprint for tgcf's whole config."""

    # pylint: disable=too-few-public-
    pid: int = 0
    theme: str = "light"
    login: LoginConfig = LoginConfig()
    admins: List[Union[int, str]] = []
    forwards: List[Forward] = []
    show_forwarded_from: bool = False
    mode: int = 0  # 0: live, 1:past
    live: LiveSettings = LiveSettings()
    past: PastSettings = PastSettings()

    plugins: PluginConfig = PluginConfig()
    bot_messages = BotMessages()


def write_config_to_file(config: Config):
    # Use the config directory and make sure it's a file path
    config_file_path = os.path.join(CONFIG_DIR, CONFIG_FILE_NAME)
    
    # If the path exists and is a directory, use an alternative filename
    if os.path.exists(config_file_path) and os.path.isdir(config_file_path):
        actual_file = os.path.join(CONFIG_DIR, "phoenixtgfw_config.json")
        logging.warning(f"{config_file_path} is a directory, using {actual_file} instead")
        with open(actual_file, "w", encoding="utf8") as file:
            file.write(config.json())
    else:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(config_file_path), exist_ok=True)
        with open(config_file_path, "w", encoding="utf8") as file:
            file.write(config.json())


def detect_config_type() -> int:
    # Get the storage mode from environment variable
    storage_mode = os.getenv("STORAGE_MODE", "file").lower()
    
    if storage_mode == "mongodb":
        # Strict MongoDB mode - fail if MongoDB connection string is not provided
        if not os.getenv("MONGO_CON_STR"):
            logging.error("STORAGE_MODE is set to 'mongodb' but MONGO_CON_STR is not provided")
            sys.exit(1)
            
        logging.info("Using MongoDB for storing config as specified by STORAGE_MODE")
        try:
            client = MongoClient(MONGO_CON_STR)
            # Test the connection
            client.server_info()
            stg.mycol = setup_mongo(client)
            return 2
        except Exception as e:
            logging.error(f"Failed to connect to MongoDB: {e}")
            logging.error("STORAGE_MODE is set to 'mongodb' but MongoDB connection failed")
            sys.exit(1)
    
    elif storage_mode == "file":
        # Strict file mode - use config file
        logging.info("Using file-based storage as specified by STORAGE_MODE")
        
        # Check if CONFIG_FILE_NAME exists in the config directory
        config_file_path = os.path.join(CONFIG_DIR, CONFIG_FILE_NAME)
        alt_file_path = os.path.join(CONFIG_DIR, "phoenixtgfw_config.json")
        
        if os.path.exists(config_file_path):
            logging.info(f"{config_file_path} detected!")
            # Check if it's a directory
            if os.path.isdir(config_file_path):
                logging.warning(f"{config_file_path} is a directory, will use alternative file")
                # Check if alternative config file exists
                if os.path.exists(alt_file_path):
                    logging.info(f"Using alternative config file {alt_file_path}")
                else:
                    logging.info(f"Creating alternative config file {alt_file_path}")
                    cfg = Config()
                    with open(alt_file_path, "w", encoding="utf8") as file:
                        file.write(cfg.json())
            return 1
        # If not in config directory, check current directory
        elif CONFIG_FILE_NAME in os.listdir():
            logging.info(f"{CONFIG_FILE_NAME} detected in current directory!")
            return 1
        else:
            logging.info("Creating new config file as none exists")
            # Ensure the config directory exists
            os.makedirs(CONFIG_DIR, exist_ok=True)
            cfg = Config()
            write_config_to_file(cfg)
            logging.info(f"Config file created!")
            return 1
    else:
        logging.error(f"Invalid STORAGE_MODE: {storage_mode}. Must be 'file' or 'mongodb'")
        sys.exit(1)


def read_config(count=1) -> Config:
    """Load the configuration defined by user."""
    if count > 3:
        logging.warning("Failed to read config, returning default config")
        return Config()
    if count != 1:
        logging.info(f"Trying to read config time:{count}")
    try:
        if stg.CONFIG_TYPE == 1:
            # Check for config file in the config directory first
            config_file_path = os.path.join(CONFIG_DIR, CONFIG_FILE_NAME)
            alt_file_path = os.path.join(CONFIG_DIR, "phoenixtgfw_config.json")
            
            # Check if the config path exists and is a directory
            if os.path.exists(config_file_path) and os.path.isdir(config_file_path):
                # Try to use an alternative filename
                logging.warning(f"{config_file_path} is a directory, trying {alt_file_path} instead")
                if os.path.isfile(alt_file_path):
                    with open(alt_file_path, encoding="utf8") as file:
                        return Config.parse_raw(file.read())
                else:
                    # Create a new config file with the alternative name
                    cfg = Config()
                    with open(alt_file_path, "w", encoding="utf8") as file:
                        file.write(cfg.json())
                    return cfg
            # If config path exists and is a file
            elif os.path.isfile(config_file_path):
                with open(config_file_path, encoding="utf8") as file:
                    return Config.parse_raw(file.read())
            # Fallback to the original behavior if not found in config directory
            elif os.path.isfile(CONFIG_FILE_NAME):
                with open(CONFIG_FILE_NAME, encoding="utf8") as file:
                    return Config.parse_raw(file.read())
            else:
                # Create a new config file
                cfg = Config()
                write_config_to_file(cfg)
                return cfg
        elif stg.CONFIG_TYPE == 2:
            return read_db()
        else:
            return Config()
    except Exception as err:
        logging.warning(err)
        stg.CONFIG_TYPE = detect_config_type()
        return read_config(count=count + 1)


def write_config(config: Config, persist=True):
    """Write changes in config back to file."""
    if stg.CONFIG_TYPE == 1 or stg.CONFIG_TYPE == 0:
        write_config_to_file(config)
    elif stg.CONFIG_TYPE == 2:
        if persist:
            update_db(config)


def get_env_var(name: str, optional: bool = False) -> str:
    """Fetch an env var."""
    var = os.getenv(name, "")

    while not var:
        if optional:
            return ""
        var = input(f"Enter {name}: ")
    return var


async def get_id(client: TelegramClient, peer):
    return await client.get_peer_id(peer)


async def load_from_to(
    client: TelegramClient, forwards: List[Forward]
) -> Dict[int, List[int]]:
    """Convert a list of Forward objects to a mapping.

    Args:
        client: Instance of Telegram client (logged in)
        forwards: List of Forward objects

    Returns:
        Dict: key = chat id of source
                value = List of chat ids of destinations

    Notes:
    -> The Forward objects may contain username/phn no/links
    -> But this mapping strictly contains signed integer chat ids
    -> Chat ids are essential for how storage is implemented
    -> Storage is essential for edit, delete and reply syncs
    """
    from_to_dict = {}

    async def _(peer):
        return await get_id(client, peer)

    for forward in forwards:
        if not forward.use_this:
            continue
        source = forward.source
        if not isinstance(source, int) and source.strip() == "":
            continue
        src = await _(forward.source)
        from_to_dict[src] = [await _(dest) for dest in forward.dest]
    logging.info(f"From to dict is {from_to_dict}")
    return from_to_dict


async def load_admins(client: TelegramClient):
    for admin in CONFIG.admins:
        ADMINS.append(await get_id(client, admin))
    logging.info(f"Loaded admins are {ADMINS}")
    return ADMINS


def setup_mongo(client):

    mydb = client[MONGO_DB_NAME]
    mycol = mydb[MONGO_COL_NAME]
    if not mycol.find_one({"_id": 0}):
        mycol.insert_one({"_id": 0, "author": "tgcf", "config": Config().dict()})

    return mycol


def update_db(cfg):
    stg.mycol.update_one({"_id": 0}, {"$set": {"config": cfg.dict()}})


def read_db():
    obj = stg.mycol.find_one({"_id": 0})
    cfg = Config(**obj["config"])
    return cfg


# Password protection is completely disabled
PASSWORD = None
ADMINS = []

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
MONGO_CON_STR = os.getenv("MONGO_CON_STR")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "tgcf-config")
MONGO_COL_NAME = os.getenv("MONGO_COL_NAME", "tgcf-instance-0")

stg.CONFIG_TYPE = detect_config_type()
CONFIG = read_config()

from_to = {}
is_bot: Optional[bool] = None
logging.info("config.py got executed")


def get_SESSION(section: Any = CONFIG.login, default: str = 'tgcf_bot'):
    if section.SESSION_STRING and section.user_type == 1:
        logging.info("using session string")
        SESSION = StringSession(section.SESSION_STRING)
    elif section.BOT_TOKEN and section.user_type == 0:
        logging.info("using bot account")
        SESSION = default
    else:
        logging.warning("Login information not set!")
        sys.exit()
    return SESSION