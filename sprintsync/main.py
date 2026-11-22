"""SprintSync command-line entry point.

Owner: Verrill M. Bargola
Branch: feature/cli

Usage:
    python -m sprintsync.main --standup    post the stand-up to Webex
    python -m sprintsync.main --backlog    print the backlog in the terminal
    python -m sprintsync.main --menu       open the interactive menu
"""

import argparse


def parse_args(argv=None):
    """Parse command-line options."""
    parser = argparse.ArgumentParser(description="SprintSync bot")
    parser.add_argument("--standup", action="store_true",
                        help="post the daily stand-up to Webex")
    parser.add_argument("--backlog", action="store_true",
                        help="print the backlog in the terminal")
    parser.add_argument("--menu", action="store_true",
                        help="open the interactive menu")
    return parser.parse_args(argv)


def main(argv=None):
    """Run the option the user picked."""
    args = parse_args(argv)
    print("SprintSync is set up. Features coming in Sprint 1 and 2.")
    return args


if __name__ == "__main__":
    main()
