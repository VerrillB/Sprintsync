"""Tests for main.py. Trello and Webex are mocked."""

from datetime import date
from unittest.mock import patch

from sprintsync import main as cli
from sprintsync.config import ConfigError
from sprintsync.trello_client import TrelloError

CONFIG = {
    "TRELLO_KEY": "k",
    "TRELLO_TOKEN": "t",
    "TRELLO_BOARD_ID": "b",
    "WEBEX_BOT_TOKEN": "w",
    "WEBEX_ROOM_ID": "r",
}
BACKLOG = {
    "In Progress": [{"name": "Build CLI", "owners": ["Verrill Bargola"], "due": "2026-11-28"}],
    "Done": [],
}


def fake_input(answers):
    """Return an input function that gives the answers in order."""
    answers = iter(answers)
    return lambda prompt: next(answers)


@patch("sprintsync.main.send_message", return_value="msg1")
@patch("sprintsync.main.get_backlog", return_value=BACKLOG)
def test_run_standup_posts_message(mock_backlog, mock_send):
    message_id = cli.run_standup(CONFIG, today=date(2026, 11, 26))
    assert message_id == "msg1"
    mock_backlog.assert_called_once_with("b", "k", "t")
    message, token, room = mock_send.call_args.args
    assert "Build CLI" in message
    assert (token, room) == ("w", "r")


def test_format_backlog():
    text = cli.format_backlog(BACKLOG)
    assert "In Progress (1)" in text
    assert "  - Build CLI (Verrill Bargola, due 2026-11-28)" in text
    assert "Done (0)" in text


def test_format_backlog_unassigned():
    text = cli.format_backlog({"In Progress": [{"name": "Task", "owners": [], "due": None}]})
    assert "  - Task (Unassigned)" in text


@patch("sprintsync.main.get_backlog", return_value=BACKLOG)
def test_menu_show_backlog_then_exit(mock_backlog):
    output = []
    cli.run_menu(CONFIG, fake_input(["1", "3"]), output.append)
    assert any("Build CLI" in line for line in output)
    assert output[-1] == "Goodbye."


def test_menu_rejects_invalid_choice():
    output = []
    cli.run_menu(CONFIG, fake_input(["9", "abc", "3"]), output.append)
    assert output.count("Invalid choice. Enter 1, 2, or 3.") == 2


@patch("sprintsync.main.send_message", return_value="msg1")
@patch("sprintsync.main.get_backlog", return_value=BACKLOG)
def test_menu_post_standup(mock_backlog, mock_send):
    output = []
    cli.run_menu(CONFIG, fake_input(["2", "3"]), output.append)
    assert "Stand-up posted to Webex. Message ID: msg1" in output


@patch("sprintsync.main.run_standup", return_value="msg1")
@patch("sprintsync.main.load_config", return_value=CONFIG)
def test_main_standup_flag(mock_config, mock_standup, capsys):
    assert cli.main(["--standup"]) == 0
    assert "Message ID: msg1" in capsys.readouterr().out


@patch("sprintsync.main.get_backlog", return_value=BACKLOG)
@patch("sprintsync.main.load_config", return_value=CONFIG)
def test_main_backlog_flag(mock_config, mock_backlog, capsys):
    assert cli.main(["--backlog"]) == 0
    assert "Build CLI" in capsys.readouterr().out


@patch("sprintsync.main.load_config", side_effect=ConfigError("Missing settings: TRELLO_KEY"))
def test_main_missing_config_returns_error(mock_config, capsys):
    assert cli.main(["--standup"]) == 1
    assert "Error: Missing settings: TRELLO_KEY" in capsys.readouterr().out


@patch("sprintsync.main.get_backlog", side_effect=TrelloError("Trello board not found (404)."))
@patch("sprintsync.main.load_config", return_value=CONFIG)
def test_main_trello_error_returns_error(mock_config, mock_backlog, capsys):
    assert cli.main(["--backlog"]) == 1
    assert "404" in capsys.readouterr().out
