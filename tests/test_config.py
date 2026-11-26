"""Tests for config.py."""

import pytest

from sprintsync import config

ALL_SET = {
    "TRELLO_KEY": "k",
    "TRELLO_TOKEN": "t",
    "TRELLO_BOARD_ID": "b",
    "WEBEX_BOT_TOKEN": "w",
    "WEBEX_ROOM_ID": "r",
}


def test_load_config_returns_values(monkeypatch):
    for name, value in ALL_SET.items():
        monkeypatch.setenv(name, value)
    result = config.load_config(env_file="does-not-exist.env")
    assert result["TRELLO_KEY"] == "k"
    assert result["NETCONF_PORT"] == "830"


def test_load_config_missing_value_raises(monkeypatch):
    for name in ALL_SET:
        monkeypatch.delenv(name, raising=False)
    with pytest.raises(config.ConfigError) as error:
        config.load_config(env_file="does-not-exist.env")
    assert "TRELLO_KEY" in str(error.value)

def test_load_config_strips_spaces_and_newlines(monkeypatch):
    for name, value in ALL_SET.items():
        monkeypatch.setenv(name, value)
    monkeypatch.setenv("TRELLO_TOKEN", " t\n")
    result = config.load_config(env_file="does-not-exist.env")
    assert result["TRELLO_TOKEN"] == "t"


def test_load_config_blank_value_counts_as_missing(monkeypatch):
    for name, value in ALL_SET.items():
        monkeypatch.setenv(name, value)
    monkeypatch.setenv("WEBEX_ROOM_ID", "   ")
    with pytest.raises(config.ConfigError) as error:
        config.load_config(env_file="does-not-exist.env")
    assert "WEBEX_ROOM_ID" in str(error.value)
