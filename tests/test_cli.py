"""Tests for the gtasks CLI."""

from unittest.mock import MagicMock, patch
from click.testing import CliRunner
from gtasks.cli import main


def test_main():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Usage: main" in result.output


@patch('gtasks.cli.get_tasks_service')
def test_lists_command(mock_get_tasks_service):
    """Test the 'lists' command."""
    mock_service = MagicMock()
    mock_get_tasks_service.return_value = mock_service

    # Mock the API response
    mock_service.tasklists().list().execute.return_value = {
        "items": [
            {"title": "List 1", "id": "1"},
            {"title": "List 2", "id": "2"},
        ]
    }

    runner = CliRunner()
    result = runner.invoke(main, ["lists"])

    assert result.exit_code == 0
    assert "List 1 (1)" in result.output
    assert "List 2 (2)" in result.output


@patch('gtasks.cli.get_tasks_service')
def test_lists_command_no_lists(mock_get_tasks_service):
    """Test the 'lists' command when there are no lists."""
    mock_service = MagicMock()
    mock_get_tasks_service.return_value = mock_service

    # Mock the API response for no lists
    mock_service.tasklists().list().execute.return_value = {}

    runner = CliRunner()
    result = runner.invoke(main, ["lists"])

    assert result.exit_code == 0
    assert "No task lists found." in result.output


@patch('gtasks.cli.get_tasks_service')
def test_tasks_command(mock_get_tasks_service):
    """Test the 'tasks' command."""
    mock_service = MagicMock()
    mock_get_tasks_service.return_value = mock_service

    # Mock the API response
    mock_service.tasks().list().execute.return_value = {
        "items": [
            {"title": "Task 1", "id": "1", "status": "needsAction"},
            {"title": "Task 2", "id": "2", "status": "completed"},
        ]
    }

    runner = CliRunner()
    result = runner.invoke(main, ["tasks", "tasklist1"])

    assert result.exit_code == 0
    assert "Task 1 (id: 1, status: Needs Action)" in result.output
    assert "Task 2 (id: 2, status: Completed)" in result.output


@patch('gtasks.cli.get_tasks_service')
def test_tasks_command_no_tasks(mock_get_tasks_service):
    """Test the 'tasks' command when there are no tasks."""
    mock_service = MagicMock()
    mock_get_tasks_service.return_value = mock_service

    # Mock the API response for no tasks
    mock_service.tasks().list().execute.return_value = {}

    runner = CliRunner()
    result = runner.invoke(main, ["tasks", "tasklist1"])

    assert result.exit_code == 0
    assert "No tasks found in the specified list." in result.output


@patch('gtasks.cli.get_tasks_service')
def test_add_command(mock_get_tasks_service):
    """Test the 'add' command."""
    mock_service = MagicMock()
    mock_get_tasks_service.return_value = mock_service

    # Mock the API response
    mock_service.tasks().insert().execute.return_value = {"title": "New Task"}

    runner = CliRunner()
    result = runner.invoke(main, ["add", "tasklist1", "New Task"])

    assert result.exit_code == 0
    assert "Task 'New Task' created." in result.output
    mock_service.tasks().insert.assert_called_with(
        tasklist="tasklist1", body={"title": "New Task"}
    )


@patch('gtasks.cli.get_tasks_service')
def test_complete_command(mock_get_tasks_service):
    """Test the 'complete' command."""
    mock_service = MagicMock()
    mock_get_tasks_service.return_value = mock_service

    # Mock the API response for get()
    mock_service.tasks().get().execute.return_value = {
        "title": "Task to complete",
        "status": "needsAction",
    }
    # Mock the API response for update()
    mock_service.tasks().update().execute.return_value = {
        "title": "Task to complete",
        "status": "completed",
    }

    runner = CliRunner()
    result = runner.invoke(main, ["complete", "tasklist1", "task1"])

    assert result.exit_code == 0
    assert "Task 'Task to complete' marked as complete." in result.output

    # Assert that get and update were called correctly
    mock_service.tasks().get.assert_called_with(tasklist="tasklist1", task="task1")
    mock_service.tasks().update.assert_called_with(
        tasklist="tasklist1",
        task="task1",
        body={"title": "Task to complete", "status": "completed"},
    )


@patch('gtasks.cli.get_tasks_service')
def test_delete_command(mock_get_tasks_service):
    """Test the 'delete' command."""
    mock_service = MagicMock()
    mock_get_tasks_service.return_value = mock_service

    runner = CliRunner()
    result = runner.invoke(main, ["delete", "tasklist1"])

    assert result.exit_code == 0
    assert "Task list with id 'tasklist1' deleted." in result.output
    mock_service.tasklists().delete.assert_called_with(tasklist="tasklist1")
