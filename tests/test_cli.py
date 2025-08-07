"""Tests for the gtasks CLI."""

from click.testing import CliRunner
from gtasks.cli import main

def test_main():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Usage: main" in result.output
