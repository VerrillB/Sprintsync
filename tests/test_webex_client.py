"""Tests for webex_client.py. All Webex calls are mocked."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from sprintsync import webex_client


def fake_response(status_code, json_body=None):
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = json_body or {}
    return response


@patch("sprintsync.webex_client.requests.post")
def test_send_message_returns_id(mock_post):
    mock_post.return_value = fake_response(200, {"id": "msg123"})
    assert webex_client.send_message("hi", "token", "room") == "msg123"


@patch("sprintsync.webex_client.requests.post")
def test_send_message_sends_bearer_header_and_room(mock_post):
    mock_post.return_value = fake_response(200, {"id": "msg123"})
    webex_client.send_message("**hello**", "token", "room")
    _, kwargs = mock_post.call_args
    assert kwargs["headers"]["Authorization"] == "Bearer token"
    assert kwargs["json"] == {"roomId": "room", "markdown": "**hello**"}
    assert kwargs["timeout"] == webex_client.TIMEOUT


@pytest.mark.parametrize("status", [401, 404, 429])
@patch("sprintsync.webex_client.requests.post")
def test_send_message_known_errors(mock_post, status):
    mock_post.return_value = fake_response(status)
    with pytest.raises(webex_client.WebexError) as error:
        webex_client.send_message("hi", "token", "room")
    assert str(status) in str(error.value)


@patch("sprintsync.webex_client.requests.post")
def test_send_message_unexpected_status(mock_post):
    mock_post.return_value = fake_response(500)
    with pytest.raises(webex_client.WebexError) as error:
        webex_client.send_message("hi", "token", "room")
    assert "500" in str(error.value)


@patch("sprintsync.webex_client.requests.post")
def test_send_message_network_error(mock_post):
    mock_post.side_effect = requests.exceptions.ConnectionError("no internet")
    with pytest.raises(webex_client.WebexError) as error:
        webex_client.send_message("hi", "token", "room")
    assert "Could not reach Webex" in str(error.value)