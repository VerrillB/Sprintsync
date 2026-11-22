"""Read the team's backlog from the Trello REST API.

Owner: John Reymond G. Pascual
Branch: feature/trello-client
"""

import requests

BASE_URL = "https://api.trello.com/1"
TIMEOUT = 10
SKIP_LISTS = ["Members"]

ERROR_MESSAGES = {
    401: "Trello rejected the key or token (401). Check TRELLO_KEY and TRELLO_TOKEN in .env.",
    404: "Trello board not found (404). Check TRELLO_BOARD_ID in .env.",
    429: "Trello rate limit reached (429). Wait a moment and try again.",
}


class TrelloError(Exception):
    """Raised when Trello rejects a request or cannot be reached."""


def _get(path, key, token, params=None):
    """Send a GET request to Trello and return the parsed JSON."""
    query = {"key": key, "token": token}
    if params:
        query.update(params)

    try:
        response = requests.get(f"{BASE_URL}{path}", params=query, timeout=TIMEOUT)
    except requests.exceptions.RequestException as error:
        raise TrelloError(f"Could not reach Trello: {error}") from error

    if response.status_code in ERROR_MESSAGES:
        raise TrelloError(ERROR_MESSAGES[response.status_code])
    if response.status_code != 200:
        raise TrelloError(f"Trello returned an unexpected status: {response.status_code}")

    return response.json()


def get_lists(board_id, key, token):
    """Return the board's open lists as a list of dicts (id, name)."""
    return _get(f"/boards/{board_id}/lists", key, token, {"fields": "name"})


def get_cards(board_id, key, token):
    """Return all open cards on the board (id, name, idList, idMembers, due)."""
    return _get(
        f"/boards/{board_id}/cards",
        key,
        token,
        {"fields": "name,idList,idMembers,due"},
    )


def get_members(board_id, key, token):
    """Return the board's members (id, fullName)."""
    return _get(f"/boards/{board_id}/members", key, token, {"fields": "fullName"})


def build_backlog(lists, cards, members):
    """Group cards by list name, with owner names and due dates.

    Lists in SKIP_LISTS are left out. Due dates are cut to YYYY-MM-DD.
    """
    member_names = {member["id"]: member["fullName"] for member in members}
    backlog = {}
    list_names = {}

    for trello_list in lists:
        if trello_list["name"] in SKIP_LISTS:
            continue
        backlog[trello_list["name"]] = []
        list_names[trello_list["id"]] = trello_list["name"]

    for card in cards:
        list_name = list_names.get(card["idList"])
        if list_name is None:
            continue
        backlog[list_name].append({
            "name": card["name"],
            "owners": [member_names.get(mid, "Unknown") for mid in card.get("idMembers", [])],
            "due": card["due"][:10] if card.get("due") else None,
        })

    return backlog


def get_backlog(board_id, key, token):
    """Fetch the board from Trello and return cards grouped by list name.

    Example return value:
    {
        "In Progress": [
            {"name": "Build Trello client", "owners": ["Reymond Pascual"], "due": "2026-11-28"}
        ],
        "Done": []
    }
    """
    lists = get_lists(board_id, key, token)
    cards = get_cards(board_id, key, token)
    members = get_members(board_id, key, token)
    return build_backlog(lists, cards, members)
