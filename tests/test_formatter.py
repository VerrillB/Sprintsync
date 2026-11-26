"""Tests for formatter.py."""

from datetime import date

from sprintsync import formatter

TODAY = date(2026, 11, 24)

BACKLOG = {
    "Product Backlog": [
        {"name": "Jira support", "owners": [], "due": None},
    ],
    "In Progress": [
        {"name": "Build formatter", "owners": ["Albert Vendiola"], "due": "2026-11-25"},
        {"name": "Fix README", "owners": ["Verrill Bargola"], "due": "2026-11-20"},
    ],
    "In Review": [],
    "Done": [
        {"name": "Old task", "owners": ["Reymond Pascual"], "due": "2026-11-01"},
    ],
}


def test_standup_has_date_header():
    message = formatter.build_standup(BACKLOG, TODAY)
    assert message.startswith("**Daily Stand-up: Tuesday, Nov 24, 2026**")


def test_standup_lists_in_progress_with_owner_and_due():
    message = formatter.build_standup(BACKLOG, TODAY)
    assert "- Build formatter (Albert Vendiola), due Nov 25" in message


def test_find_overdue_skips_done_cards():
    overdue = formatter.find_overdue(BACKLOG, TODAY)
    assert [card["name"] for card in overdue] == ["Fix README"]


def test_find_due_soon():
    due_soon = formatter.find_due_soon(BACKLOG, TODAY)
    assert [card["name"] for card in due_soon] == ["Build formatter"]


def test_standup_overdue_section():
    message = formatter.build_standup(BACKLOG, TODAY)
    assert "**Overdue**" in message
    assert "Fix README (Verrill Bargola), due Nov 20" in message


def test_standup_unassigned_card():
    backlog = {"In Progress": [{"name": "Task", "owners": [], "due": None}]}
    message = formatter.build_standup(backlog, TODAY)
    assert "- Task (Unassigned)" in message


def test_standup_empty_board():
    message = formatter.build_standup({"In Progress": []}, TODAY)
    assert "- No tasks in progress" in message
    assert "**Overdue**" not in message


def test_standup_board_summary_counts():
    message = formatter.build_standup(BACKLOG, TODAY)
    assert "Product Backlog: 1, In Progress: 2, In Review: 0, Done: 1" in message


def test_standup_device_status():
    message = formatter.build_standup(BACKLOG, TODAY, [("GigabitEthernet1", "up")])
    assert "- GigabitEthernet1: up" in message


def test_standup_device_unreachable():
    message = formatter.build_standup(BACKLOG, TODAY, [])
    assert "- Device unreachable" in message


def test_standup_no_device_section_by_default():
    message = formatter.build_standup(BACKLOG, TODAY)
    assert "**Device status**" not in message


def test_build_notice_success():
    message = formatter.build_build_notice("SUCCESS", "Reymond Pascual", "abc1234def")
    assert message == "**Jenkins build PASSED** for commit `abc1234` by Reymond Pascual"


def test_build_notice_failure():
    message = formatter.build_build_notice("FAILURE", "Reymond Pascual", "abc1234def")
    assert "BROKEN" in message
