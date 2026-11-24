"""Post messages to the team's Webex space through the Webex Messages API.

Owner: John Reymond G. Pascual
Branch: feature/webex-client
"""

import requests

MESSAGES_URL = "https://webexapis.com/v1/messages"
TIMEOUT = 10

ERROR_MESSAGES = {
    401: "Webex rejected the bot token (401). Check WEBEX_BOT_TOKEN in .env.",
    404: "Webex room not found (404). Check WEBEX_ROOM_ID and that the bot is in the space.",
    429: "Webex rate limit reached (429). Wait a moment and try again.",
}


class WebexError(Exception):
    """Raised when Webex rejects a request or cannot be reached."""


def send_message(markdown, bot_token, room_id):
    """Post a Markdown message to the room. Return the new message ID."""
    headers = {
        "Authorization": f"Bearer {bot_token}",
        "Content-Type": "application/json",
    }
    body = {"roomId": room_id, "markdown": markdown}

    try:
        response = requests.post(MESSAGES_URL, headers=headers, json=body, timeout=TIMEOUT)
    except requests.exceptions.RequestException as error:
        raise WebexError(f"Could not reach Webex: {error}") from error

    if response.status_code in ERROR_MESSAGES:
        raise WebexError(ERROR_MESSAGES[response.status_code])
    if response.status_code != 200:
        raise WebexError(f"Webex returned an unexpected status: {response.status_code}")

    return response.json()["id"]
