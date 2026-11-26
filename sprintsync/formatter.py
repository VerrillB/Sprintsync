"""Build the Markdown messages SprintSync posts to Webex.

Owner: Albert John C. Vendiola
Branch: feature/formatter
"""

from datetime import date, timedelta

DONE_LIST = "Done"
IN_PROGRESS_LIST = "In Progress"
DUE_SOON_DAYS = 2


def _format_date(iso_date):
    """Turn '2026-11-28' into 'Nov 28'."""
    return date.fromisoformat(iso_date).strftime("%b %d").replace(" 0", " ")


def _owners(card):
    """Return owner names as text, or 'Unassigned'."""
    return ", ".join(card["owners"]) if card["owners"] else "Unassigned"


def _card_line(card):
    """Return one bullet line for a card."""
    line = f"- {card['name']} ({_owners(card)})"
    if card["due"]:
        line += f", due {_format_date(card['due'])}"
    return line


def _open_cards(backlog):
    """Yield every card that is not in the Done list."""
    for list_name, cards in backlog.items():
        if list_name == DONE_LIST:
            continue
        for card in cards:
            yield card


def find_overdue(backlog, today):
    """Return open cards whose due date is before today."""
    return [
        card for card in _open_cards(backlog)
        if card["due"] and date.fromisoformat(card["due"]) < today
    ]


def find_due_soon(backlog, today):
    """Return open cards due today or within the next DUE_SOON_DAYS days."""
    limit = today + timedelta(days=DUE_SOON_DAYS)
    return [
        card for card in _open_cards(backlog)
        if card["due"] and today <= date.fromisoformat(card["due"]) <= limit
    ]


def build_standup(backlog, today, device_status=None):
    """Return the daily stand-up message as Markdown.

    backlog: output of trello_client.get_backlog()
    today: a datetime.date
    device_status: optional list of (interface name, status) tuples
    """
    lines = [f"**Daily Stand-up: {today.strftime('%A, %b %d, %Y').replace(' 0', ' ')}**", ""]

    lines.append("**In Progress**")
    in_progress = backlog.get(IN_PROGRESS_LIST, [])
    lines.extend(_card_line(card) for card in in_progress)
    if not in_progress:
        lines.append("- No tasks in progress")
    lines.append("")

    overdue = find_overdue(backlog, today)
    if overdue:
        lines.append("**Overdue**")
        lines.extend(_card_line(card) for card in overdue)
        lines.append("")

    due_soon = find_due_soon(backlog, today)
    if due_soon:
        lines.append(f"**Due in the next {DUE_SOON_DAYS} days**")
        lines.extend(_card_line(card) for card in due_soon)
        lines.append("")

    counts = ", ".join(f"{name}: {len(cards)}" for name, cards in backlog.items())
    lines.append(f"**Board summary:** {counts}")
    lines.append("")

    if device_status is not None:
        lines.append("**Device status**")
        if device_status:
            lines.extend(f"- {name}: {status}" for name, status in device_status)
        else:
            lines.append("- Device unreachable")
        lines.append("")

    lines.append("Reply with: what you did yesterday, what you will do today, and any blockers.")
    return "\n".join(lines)


def build_build_notice(status, author, commit):
    """Return a short Jenkins build result message as Markdown."""
    result = "PASSED" if status.upper() == "SUCCESS" else "FAILED"
    return f"**Jenkins build {result}** for commit `{commit[:7]}` by {author}"
