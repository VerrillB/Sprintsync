"""SprintSync command-line entry point.

Owner: Verrill M. Bargola
Branch: feature/cli

Usage:
    python -m sprintsync.main --standup    post the stand-up to Webex
    python -m sprintsync.main --backlog    print the backlog in the terminal
    python -m sprintsync.main --menu       open the interactive menu
"""

import argparse
import sys
from datetime import date

from sprintsync.config import ConfigError, load_config
from sprintsync.formatter import build_standup
from sprintsync.trello_client import TrelloError, get_backlog
from sprintsync.webex_client import WebexError, send_message

MENU = """
SprintSync
1. Show backlog
2. Post stand-up to Webex
3. Exit
"""


def fetch_backlog(config):
    """Get the backlog from Trello using the loaded settings."""
    return get_backlog(config["TRELLO_BOARD_ID"], config["TRELLO_KEY"], config["TRELLO_TOKEN"])


def run_standup(config, today=None):
    """Build the stand-up from Trello and post it to Webex. Return the message ID."""
    backlog = fetch_backlog(config)
    message = build_standup(backlog, today or date.today())
    return send_message(message, config["WEBEX_BOT_TOKEN"], config["WEBEX_ROOM_ID"])


def format_backlog(backlog):
    """Return the backlog as plain text for the terminal."""
    lines = []
    for list_name, cards in backlog.items():
        lines.append(f"{list_name} ({len(cards)})")
        for card in cards:
            owners = ", ".join(card["owners"]) or "Unassigned"
            due = f", due {card['due']}" if card["due"] else ""
            lines.append(f"  - {card['name']} ({owners}{due})")
    return "\n".join(lines)


def run_menu(config, input_func=input, print_func=print):
    """Show the interactive menu until the user chooses Exit."""
    while True:
        print_func(MENU)
        choice = input_func("Choose 1-3: ").strip()
        if choice == "1":
            print_func(format_backlog(fetch_backlog(config)))
        elif choice == "2":
            message_id = run_standup(config)
            print_func(f"Stand-up posted to Webex. Message ID: {message_id}")
        elif choice == "3":
            print_func("Goodbye.")
            return
        else:
            print_func("Invalid choice. Enter 1, 2, or 3.")


def parse_args(argv=None):
    """Parse command-line options."""
    parser = argparse.ArgumentParser(description="SprintSync bot")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--standup", action="store_true",
                       help="post the daily stand-up to Webex")
    group.add_argument("--backlog", action="store_true",
                       help="print the backlog in the terminal")
    group.add_argument("--menu", action="store_true",
                       help="open the interactive menu")
    return parser.parse_args(argv)


def main(argv=None):
    """Run the option the user picked. Return 0 on success, 1 on error."""
    args = parse_args(argv)
    try:
        config = load_config()
        if args.standup:
            message_id = run_standup(config)
            print(f"Stand-up posted to Webex. Message ID: {message_id}")
        elif args.backlog:
            print(format_backlog(fetch_backlog(config)))
        else:
            run_menu(config)
    except (ConfigError, TrelloError, WebexError) as error:
        print(f"Error: {error}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
