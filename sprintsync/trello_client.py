"""Read the team's backlog from the Trello REST API.

Owner: Abraham Y. Ileto
Branch: feature/trello-client
"""

BASE_URL = "https://api.trello.com/1"
TIMEOUT = 10
SKIP_LISTS = ["Members"]


def get_lists(board_id, key, token):
    """Return the board's lists as a list of dicts (id, name)."""
    raise NotImplementedError


def get_cards(board_id, key, token):
    """Return all open cards on the board (id, name, idList, idMembers, due)."""
    raise NotImplementedError


def get_members(board_id, key, token):
    """Return the board's members (id, fullName)."""
    raise NotImplementedError


def get_backlog(board_id, key, token):
    """Return cards grouped by list name, with owner names and due dates.

    Example return value:
    {
        "In Progress": [
            {"name": "Build Trello client", "owners": ["John"], "due": "2026-11-28"}
        ],
        ...
    }
    Lists in SKIP_LISTS are left out.
    """
    raise NotImplementedError
