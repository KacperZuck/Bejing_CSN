import json
import os
from Modules.logger import logger


def load_config():
    """Insert base configuration from json file if exists"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config.json")

    default_config = {
        "server": {"host": "127.0.0.1", "smtp_port": 8025, "pop3_port": 8110},
        "account": {"username": "student", "password": "password", "email_address": "client@email.edu"},
        "defaults": {"recipient_email": "test@recipient.edu"}
    }

    if not os.path.exists(config_path):
        logger.warning("Not found config file, implementing base configuration")
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=4)
        except Exception as e:
            logger.error(f"Error in opening config.json: {e}")
        return default_config

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error in fetching data from file, implementing basic config: {e}")
        return default_config