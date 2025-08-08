from .auth import get_tasks_service
from .config import get_current_task_list


def get_task_lists():
    """Fetches all task lists from the Google Tasks API."""
    service = get_tasks_service()
    results = service.tasklists().list(maxResults=100).execute()
    return results.get("items", [])


def get_tasks(task_list_id=None, status="incomplete"):
    """Fetches all tasks from a given task list."""
    service = get_tasks_service()
    if not task_list_id:
        task_list_id = get_current_task_list()
        if not task_list_id:
            raise Exception("No current task list set.")

    show_completed = status in ["all", "completed"]
    results = (
        service.tasks().list(tasklist=task_list_id, showCompleted=show_completed).execute()
    )
    items = results.get("items", [])

    if status == "completed":
        items = [item for item in items if item.get("status") == "completed"]
    elif status == "incomplete":
        items = [item for item in items if item.get("status") != "completed"]

    return items


def add_task(title, task_list_id=None):
    """Adds a new task to the specified task list."""
    service = get_tasks_service()
    if not task_list_id:
        task_list_id = get_current_task_list()
        if not task_list_id:
            raise Exception("No current task list set.")
    body = {"title": title}
    result = service.tasks().insert(tasklist=task_list_id, body=body).execute()
    return result


def delete_task(task_id, task_list_id=None):
    """Deletes the specified task from the specified task list."""
    service = get_tasks_service()
    if not task_list_id:
        task_list_id = get_current_task_list()
        if not task_list_id:
            raise Exception("No current task list set.")
    service.tasks().delete(tasklist=task_list_id, task=task_id).execute()


def complete_task(task_id, task_list_id=None):
    """Marks the specified task as complete."""
    service = get_tasks_service()
    if not task_list_id:
        task_list_id = get_current_task_list()
        if not task_list_id:
            raise Exception("No current task list set.")
    body = {"status": "completed"}
    service.tasks().update(tasklist=task_list_id, task=task_id, body=body).execute()


def edit_task(task_list_id, task_id, description):
    """Edits the specified task."""
    service = get_tasks_service()
    body = {}
    if description:
        body["notes"] = description
    if not body:
        return
    service.tasks().patch(tasklist=task_list_id, task=task_id, body=body).execute()


def edit_task_list(list_id, name):
    """Edits the specified task list."""
    service = get_tasks_service()
    body = {}
    if name:
        body["title"] = name
    if not body:
        return
    service.tasklists().patch(tasklist=list_id, body=body).execute()
