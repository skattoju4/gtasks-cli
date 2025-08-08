import os
import json

CONFIG_FILE = os.path.expanduser("~/.gtasks_config.json")


def get_current_task_list():
    """Gets the current task list from the config file."""
    if not os.path.exists(CONFIG_FILE):
        return None
    with open(CONFIG_FILE, "r") as f:
        try:
            config = json.load(f)
        except json.JSONDecodeError:
            return None
    return config.get("current_task_list")


def set_current_task_list(task_list_id):
    """Sets the current task list in the config file."""
    config = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            try:
                config = json.load(f)
            except json.JSONDecodeError:
                pass
    config["current_task_list"] = task_list_id
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)
