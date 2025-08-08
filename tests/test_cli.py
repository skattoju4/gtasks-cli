"""Tests for the gtasks CLI."""

from unittest.mock import MagicMock, patch

from click.testing import CliRunner
from gtasks.cli import main


def test_main():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Usage: main" in result.output


@patch("gtasks.cli.get_current_task_list", return_value="test_list")
@patch("gtasks.cli.get_tasks_service")
class TestTopLevelCommands:
    def test_add(self, mock_get_tasks_service, mock_get_current_task_list):
        mock_service = MagicMock()
        mock_get_tasks_service.return_value = mock_service
        mock_service.tasks.return_value.insert.return_value.execute.return_value = {
            "title": "Test Task"
        }

        runner = CliRunner()
        result = runner.invoke(main, ["add", "--title", "Test Task"])

        assert result.exit_code == 0
        assert "Task 'Test Task' created." in result.output
        mock_service.tasks.return_value.insert.assert_called_with(
            tasklist="test_list", body={"title": "Test Task"}
        )

    def test_delete(self, mock_get_tasks_service, mock_get_current_task_list):
        mock_service = MagicMock()
        mock_get_tasks_service.return_value = mock_service

        runner = CliRunner()
        result = runner.invoke(main, ["delete", "--task-id", "1"])

        assert result.exit_code == 0
        assert "Task deleted." in result.output
        mock_service.tasks.return_value.delete.assert_called_with(
            tasklist="test_list", task="1"
        )

    def test_complete(self, mock_get_tasks_service, mock_get_current_task_list):
        mock_service = MagicMock()
        mock_get_tasks_service.return_value = mock_service

        runner = CliRunner()
        result = runner.invoke(main, ["complete", "--task-id", "1"])

        assert result.exit_code == 0
        assert "Task marked as complete." in result.output
        mock_service.tasks.return_value.update.assert_called_with(
            tasklist="test_list", task="1", body={"status": "completed"}
        )


@patch("gtasks.cli.get_tasks_service")
class TestListCommands:
    def test_list_task_lists(self, mock_get_tasks_service):
        mock_service = MagicMock()
        mock_get_tasks_service.return_value = mock_service
        mock_service.tasklists.return_value.list.return_value.execute.return_value = {
            "items": [{"title": "Test List 1", "id": "1"}]
        }

        runner = CliRunner()
        result = runner.invoke(main, ["list", "task-lists"])

        assert result.exit_code == 0
        assert "Test List 1 (1)" in result.output

    @patch("gtasks.cli.get_current_task_list", return_value="test_list")
    def test_list_tasks(self, mock_get_current_task_list, mock_get_tasks_service):
        mock_service = MagicMock()
        mock_get_tasks_service.return_value = mock_service
        mock_service.tasks.return_value.list.return_value.execute.return_value = {
            "items": [{"title": "Test Task 1", "id": "1"}]
        }

        runner = CliRunner()
        result = runner.invoke(main, ["list", "tasks"])

        assert result.exit_code == 0
        assert "Test Task 1 (1)" in result.output
        mock_service.tasks.return_value.list.assert_called_with(
            tasklist="test_list", showCompleted=False
        )


@patch("gtasks.cli.set_current_task_list")
@patch("gtasks.cli.get_tasks_service")
class TestUseCommands:
    def test_use_list_by_id(self, mock_get_tasks_service, mock_set_current_task_list):
        runner = CliRunner()
        result = runner.invoke(main, ["use", "list", "--id", "test_list"])

        assert result.exit_code == 0
        assert "Current task list set to 'test_list'." in result.output
        mock_set_current_task_list.assert_called_with("test_list")

    def test_use_list_by_name(self, mock_get_tasks_service, mock_set_current_task_list):
        mock_service = MagicMock()
        mock_get_tasks_service.return_value = mock_service
        mock_service.tasklists.return_value.list.return_value.execute.return_value = {
            "items": [{"title": "Test List", "id": "test_list_id"}]
        }

        runner = CliRunner()
        result = runner.invoke(main, ["use", "list", "--name", "Test List"])

        assert result.exit_code == 0
        assert "Current task list set to 'test_list_id'." in result.output
        mock_set_current_task_list.assert_called_with("test_list_id")


@patch("gtasks.cli.get_current_task_list", return_value="test_list")
@patch("gtasks.cli.get_tasks_service")
class TestEditCommands:
    def test_edit_task(self, mock_get_tasks_service, mock_get_current_task_list):
        mock_service = MagicMock()
        mock_get_tasks_service.return_value = mock_service

        runner = CliRunner()
        result = runner.invoke(
            main, ["edit", "task", "--id", "1", "--description", "new desc"]
        )

        assert result.exit_code == 0
        assert "Task updated." in result.output
        mock_service.tasks.return_value.patch.assert_called_with(
            tasklist="test_list", task="1", body={"notes": "new desc"}
        )

    def test_edit_task_lists(self, mock_get_tasks_service, mock_get_current_task_list):
        mock_service = MagicMock()
        mock_get_tasks_service.return_value = mock_service

        runner = CliRunner()
        result = runner.invoke(
            main, ["edit", "task-lists", "--id", "1", "--name", "new name"]
        )

        assert result.exit_code == 0
        assert "Task list updated." in result.output
        mock_service.tasklists.return_value.patch.assert_called_with(
            tasklist="1", body={"title": "new name"}
        )
