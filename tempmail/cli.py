"""
CLI Entry Point for TempMail
"""

import sys
import argparse
from .client import TempMailClient
from .config import TempMailConfig
from .tui import TempMailTUI


def main():
    parser = argparse.ArgumentParser(
        prog="tempmail",
        description="TempMail CLI & TUI - Instant disposable emails from your terminal"
    )
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # tui command
    subparsers.add_parser("tui", help="Launch interactive Textual TUI")

    # new command
    subparsers.add_parser("new", help="Generate a new temporary email address")

    # inbox command
    subparsers.add_parser("inbox", help="View messages in the active mailbox")

    # code command
    code_p = subparsers.add_parser("code", help="Wait for incoming email and extract verification code")
    code_p.add_argument("-t", "--timeout", type=int, default=60, help="Polling timeout in seconds (default: 60)")

    args = parser.parse_args()

    if args.command == "tui" or args.command is None:
        # Launch TUI by default
        app = TempMailTUI()
        app.run()

    elif args.command == "new":
        client = TempMailClient()
        res = client.new_mailbox()
        email = res.get("mailbox")
        if email:
            print(f"Mailbox: {email}")
            print(f"Token: {res.get('token')}")
        else:
            print(f"Error: {res}", file=sys.stderr)

    elif args.command == "inbox":
        client = TempMailClient()
        if not client.email:
            print("No active mailbox. Run 'tempmail new' first.", file=sys.stderr)
            sys.exit(1)
        print(f"Active Mailbox: {client.email}")
        msgs = client.get_messages()
        print(f"Messages ({len(msgs)}):")
        for m in msgs:
            print(f"  [{m.get('_id')}] From: {m.get('from')} | Subject: {m.get('subject')}")

    elif args.command == "code":
        client = TempMailClient()
        if not client.email:
            client.new_mailbox()
            print(f"Created mailbox: {client.email}")
        print(f"Waiting up to {args.timeout}s for incoming email to {client.email}...")
        msg = client.wait_for_code(timeout_secs=args.timeout)
        if msg:
            import re
            txt = f"{msg.get('subject', '')} {msg.get('bodyPreview', '')}"
            matches = re.findall(r"\b\d{4,8}\b", txt)
            if matches:
                print(f"Extracted OTP: {matches[0]}")
            else:
                print(f"Received message: {msg.get('subject')} (No OTP parsed)")
        else:
            print("Timed out waiting for message.", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
