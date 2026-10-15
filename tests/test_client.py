#!/usr/bin/env python3
"""
Verification smoke tests for TempMail Client & TUI.
"""
from tempmail import TempMailConfig, TempMailClient, TempMailTUI

def main():
    print("[1] Testing TempMailConfig...")
    cfg = TempMailConfig()
    print("    Base URL:", cfg.get("base_url"))
    print("    User Agent:", cfg.get("user_agent"))

    print("\n[2] Testing TempMailClient Live Creation...")
    client = TempMailClient(cfg)
    mb = client.new_mailbox()
    email = mb.get("mailbox")
    token = mb.get("token")
    assert email and token, "Failed to create live mailbox!"
    print(f"    Live Mailbox Created: {email}")
    print(f"    JWT Token issued: {token[:30]}...")

    print("\n[3] Testing Mailbox Status Verification...")
    status = client.get_mailbox()
    assert status.get("mailbox") == email, "Verification failed!"
    print(f"    Mailbox verified: {status.get('mailbox')}")

    print("\n[4] Testing Inbox Query...")
    msgs = client.get_messages()
    print(f"    Inbox queried: {len(msgs)} messages found.")

    print("\n[5] Testing TempMailTUI Initialization...")
    tui = TempMailTUI()
    print(f"    TUI Class '{type(tui).__name__}' initialized successfully.")

    print("\n" + "=" * 50)
    print("ALL TEMPMAIL TESTS PASSED SUCCESSFULLY! (100% LIVE VERIFIED)")
    print("=" * 50)

if __name__ == "__main__":
    main()
