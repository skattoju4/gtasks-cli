import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "gtasks"
CONFIG_FILE = CONFIG_DIR / "config.json"


def ensure_config_exists():
    """Ensures that the config file and directory exist."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.is_file():
        with open(CONFIG_FILE, "w") as f:
            json.dump({}, f)


def get_config():
    """Reads the config file and returns the config dictionary."""
    ensure_config_exists()
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def write_config(config):
    """Writes the given config dictionary to the config file."""
    ensure_config_exists()
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)


def get_current_task_list():
    """Returns the ID of the current task list."""
    config = get_config()
    return config.get("current_task_list")


def set_current_task_list(task_list_id):
    """Sets the current task list ID."""
    config = get_config()
    config["current_task_list"] = task_list_id
    write_config(config)
