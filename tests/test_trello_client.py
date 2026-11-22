"""Tests for trello_client.py. All Trello calls are mocked."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from sprintsync import trello_client

LISTS = [
    {"id": "L0", "name": "Members"},
    {"id": "L1", "name": "Product Backlog"},
    {"id": "L2", "name": "In Progress"},
    {"id": "L3", "name": "Done"},
]
CARDS = [
    {"id": "C1", "name": "Build Trello client", "idList": "L2",
     "idMembers": ["M1"], "due": "2026-11-28T04:00:00.000Z"},
    {"id": "C2", "name": "Write README", "idList": "L1",
     "idMembers": [], "due": None},
    {"id": "C3", "name": "BARGOLA, Verrill M.", "idList": "L0",
     "idMembers": [], "due": None},
]
MEMBERS = [{"id": "M1", "fullName": "Reymond Pascual"}]


def fake_response(status_code, json_body=None):
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = json_body if json_body is not None else []
    return response


def test_build_backlog_groups_cards_by_list():
    backlog = trello_client.build_backlog(LISTS, CARDS, MEMBERS)
    assert backlog["In Progress"] == [
        {"name": "Build Trello client", "owners": ["Reymond Pascual"], "due": "2026-11-28"}
    ]
    assert backlog["Product Backlog"][0]["owners"] == []
    assert backlog["Product Backlog"][0]["due"] is None
    assert backlog["Done"] == []


def test_build_backlog_skips_members_list():
    backlog = trello_client.build_backlog(LISTS, CARDS, MEMBERS)
    assert "Members" not in backlog


def test_build_backlog_empty_board():
    assert trello_client.build_backlog([], [], []) == {}


def test_build_backlog_unknown_member():
    cards = [{"id": "C9", "name": "Task", "idList": "L1", "idMembers": ["X"], "due": None}]
    backlog = trello_client.build_backlog(LISTS, cards, MEMBERS)
    assert backlog["Product Backlog"][0]["owners"] == ["Unknown"]


@patch("sprintsync.trello_client.requests.get")
def test_get_lists_sends_key_and_token(mock_get):
    mock_get.return_value = fake_response(200, LISTS)
    result = trello_client.get_lists("board1", "key1", "token1")
    assert result == LISTS
    args, kwargs = mock_get.call_args
    assert args[0] == "https://api.trello.com/1/boards/board1/lists"
    assert kwargs["params"]["key"] == "key1"
    assert kwargs["params"]["token"] == "token1"
    assert kwargs["timeout"] == trello_client.TIMEOUT


@patch("sprintsync.trello_client.requests.get")
def test_get_backlog_calls_three_endpoints(mock_get):
    mock_get.side_effect = [
        fake_response(200, LISTS),
        fake_response(200, CARDS),
        fake_response(200, MEMBERS),
    ]
    backlog = trello_client.get_backlog("board1", "key1", "token1")
    assert mock_get.call_count == 3
    assert backlog["In Progress"][0]["name"] == "Build Trello client"


@pytest.mark.parametrize("status", [401, 404, 429])
@patch("sprintsync.trello_client.requests.get")
def test_known_errors(mock_get, status):
    mock_get.return_value = fake_response(status)
    with pytest.raises(trello_client.TrelloError) as error:
        trello_client.get_lists("board1", "key1", "token1")
    assert str(status) in str(error.value)


@patch("sprintsync.trello_client.requests.get")
def test_unexpected_status(mock_get):
    mock_get.return_value = fake_response(500)
    with pytest.raises(trello_client.TrelloError) as error:
        trello_client.get_cards("board1", "key1", "token1")
    assert "500" in str(error.value)


@patch("sprintsync.trello_client.requests.get")
def test_network_error(mock_get):
    mock_get.side_effect = requests.exceptions.ConnectionError("no internet")
    with pytest.raises(trello_client.TrelloError) as error:
        trello_client.get_members("board1", "key1", "token1")
    assert "Could not reach Trello" in str(error.value)
