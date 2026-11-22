"""Build the Markdown messages SprintSync posts to Webex.

Owner: Albert John C. Vendiola
Branch: feature/formatter
"""


def build_standup(backlog, today, device_status=None):
    """Return the daily stand-up message as Markdown.

    Includes: the date, each member's In Progress tasks,
    overdue cards, cards due in the next 2 days,
    and the device status line if device_status is given.
    """
    raise NotImplementedError


def build_build_notice(status, author, commit):
    """Return a short Jenkins build result message as Markdown."""
    raise NotImplementedError
