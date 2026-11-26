"""Post the Jenkins build result to Webex. Called from the Jenkinsfile.

Owner: John Reymond G. Pascual
Branch: feature/notify

Usage: python -m sprintsync.notify --status SUCCESS
"""

import argparse
import os
import subprocess
import sys

from dotenv import load_dotenv

from sprintsync.formatter import build_build_notice
from sprintsync.webex_client import WebexError, send_message


def git_value(pretty_format):
    """Return a value from the latest commit, such as %an (author) or %H (hash)."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", f"--pretty={pretty_format}"],
            capture_output=True, text=True, check=True,
        )
        return result.stdout.strip() or "unknown"
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def build_message(status, author, commit, build_url=None):
    """Return the notice text, with a link to the Jenkins build if one is given."""
    message = build_build_notice(status, author, commit)
    if build_url:
        message += f"\n\n[View build in Jenkins]({build_url})"
    return message


def parse_args(argv=None):
    """Parse command-line options."""
    parser = argparse.ArgumentParser(description="Post a Jenkins build result to Webex")
    parser.add_argument("--status", required=True, choices=["SUCCESS", "FAILURE"],
                        help="the build result")
    return parser.parse_args(argv)


def main(argv=None):
    """Post the build notice. Always return 0 so a Webex problem never changes the build result."""
    args = parse_args(argv)
    load_dotenv()
    token = os.getenv("WEBEX_BOT_TOKEN", "").strip()
    room = os.getenv("WEBEX_ROOM_ID", "").strip()
    if not token or not room:
        print("Warning: WEBEX_BOT_TOKEN or WEBEX_ROOM_ID is not set. Build notice not sent.")
        return 0

    message = build_message(
        args.status,
        git_value("%an"),
        git_value("%H"),
        os.getenv("BUILD_URL"),
    )
    try:
        message_id = send_message(message, token, room)
        print(f"Build notice posted to Webex. Message ID: {message_id}")
    except WebexError as error:
        print(f"Warning: build notice not sent. {error}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
