"""Tests for notify.py. Git and Webex are mocked."""

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from sprintsync import notify
from sprintsync.webex_client import WebexError


@pytest.fixture
def webex_env(monkeypatch):
    monkeypatch.setenv("WEBEX_BOT_TOKEN", "w")
    monkeypatch.setenv("WEBEX_ROOM_ID", "r")
    monkeypatch.delenv("BUILD_URL", raising=False)


@patch("sprintsync.notify.subprocess.run")
def test_git_value_returns_output(mock_run):
    mock_run.return_value = MagicMock(stdout="Reymond Pascual\n")
    assert notify.git_value("%an") == "Reymond Pascual"


@patch("sprintsync.notify.subprocess.run", side_effect=OSError("git not found"))
def test_git_value_without_git(mock_run):
    assert notify.git_value("%an") == "unknown"


@patch("sprintsync.notify.subprocess.run",
       side_effect=subprocess.CalledProcessError(128, "git"))
def test_git_value_outside_repo(mock_run):
    assert notify.git_value("%H") == "unknown"


def test_build_message_with_link():
    message = notify.build_message("SUCCESS", "Reymond", "abc1234def", "http://jenkins/job/1/")
    assert "**Jenkins build PASSED** for commit `abc1234` by Reymond" in message
    assert "[View build in Jenkins](http://jenkins/job/1/)" in message


def test_build_message_without_link():
    message = notify.build_message("FAILURE", "Reymond", "abc1234def")
    assert "FAILED" in message
    assert "View build" not in message


@patch("sprintsync.notify.send_message", return_value="msg1")
@patch("sprintsync.notify.git_value", side_effect=["Reymond", "abc1234def"])
@patch("sprintsync.notify.load_dotenv")
def test_main_posts_notice(mock_dotenv, mock_git, mock_send, webex_env, capsys):
    assert notify.main(["--status", "SUCCESS"]) == 0
    message, token, room = mock_send.call_args.args
    assert "PASSED" in message
    assert (token, room) == ("w", "r")
    assert "Message ID: msg1" in capsys.readouterr().out


@patch("sprintsync.notify.send_message")
@patch("sprintsync.notify.load_dotenv")
def test_main_missing_webex_settings(mock_dotenv, mock_send, monkeypatch, capsys):
    monkeypatch.delenv("WEBEX_BOT_TOKEN", raising=False)
    monkeypatch.delenv("WEBEX_ROOM_ID", raising=False)
    assert notify.main(["--status", "SUCCESS"]) == 0
    mock_send.assert_not_called()
    assert "not set" in capsys.readouterr().out


@patch("sprintsync.notify.send_message", side_effect=WebexError("Webex room not found (404)."))
@patch("sprintsync.notify.git_value", side_effect=["Reymond", "abc1234def"])
@patch("sprintsync.notify.load_dotenv")
def test_main_webex_error_does_not_fail_build(mock_dotenv, mock_git, mock_send, webex_env, capsys):
    assert notify.main(["--status", "FAILURE"]) == 0
    assert "Warning: build notice not sent" in capsys.readouterr().out


def test_invalid_status_rejected():
    with pytest.raises(SystemExit):
        notify.parse_args(["--status", "MAYBE"])
