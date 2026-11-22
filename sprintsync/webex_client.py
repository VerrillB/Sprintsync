"""Post messages to the team's Webex space through the Webex Messages API.

Owner: John Reymond G. Pascual
Branch: feature/webex-client
"""

MESSAGES_URL = "https://webexapis.com/v1/messages"
TIMEOUT = 10


class WebexError(Exception):
    """Raised when Webex rejects a request."""


def send_message(markdown, bot_token, room_id):
    """Post a Markdown message to the room. Return the new message ID.

    Raise WebexError with a clear message on 401 (bad token)
    or 404 (wrong room, or bot not in the space).
    """
    raise NotImplementedError
