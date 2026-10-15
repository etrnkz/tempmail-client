"""
TempMail Textual TUI Application
"""

import re
import time
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import (
    Header, Footer, Button, Input, Static, Label, TabbedContent, TabPane,
    DataTable, Switch, Log
)
from textual.binding import Binding
from .client import TempMailClient
from .config import TempMailConfig


class TempMailTUI(App):
    """Modern Terminal User Interface for Disposable TempMail."""

    CSS = """
    Screen {
        background: #090d16;
        color: #f1f5f9;
    }

    Header {
        background: #2563eb;
        color: #ffffff;
        text-style: bold;
    }

    Footer {
        background: #111827;
        color: #94a3b8;
    }

    .card {
        background: #1e293b;
        border: solid #334155;
        border-radius: 1;
        padding: 1 2;
        margin: 1;
    }

    .card-title {
        text-style: bold;
        color: #60a5fa;
        margin-bottom: 1;
    }

    .email-banner {
        background: #1e1b4b;
        border: solid #3b82f6;
        padding: 1 2;
        margin: 1;
        text-align: center;
    }

    .email-text {
        color: #38bdf8;
        text-style: bold;
        font-size: 130%;
    }

    .otp-banner {
        background: #064e3b;
        border: solid #10b981;
        padding: 1;
        margin: 1;
        text-align: center;
    }

    .otp-val {
        color: #34d399;
        text-style: bold;
        font-size: 140%;
    }

    Button {
        margin-top: 1;
        width: 100%;
        background: #2563eb;
        color: white;
    }

    Button:hover {
        background: #3b82f6;
    }

    Button.success {
        background: #059669;
    }

    Button.success:hover {
        background: #10b981;
    }

    Input {
        margin-bottom: 1;
        border: solid #475569;
        background: #0f172a;
        color: #f8fafc;
    }

    DataTable {
        height: 14;
        border: solid #334155;
        background: #020617;
    }

    Log {
        height: 14;
        border: solid #334155;
        background: #020617;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("r", "refresh_inbox", "Refresh Inbox", show=True),
        Binding("n", "new_email", "New Mailbox", show=True),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config = TempMailConfig()
        self.client = TempMailClient(self.config)
        self.messages = []

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with TabbedContent(initial="tab-inbox"):

            # 1. INBOX & MAILBOX
            with TabPane("Inbox", id="tab-inbox"):
                with ScrollableContainer():
                    with Vertical(classes="email-banner"):
                        yield Label("Active Temporary Address:", classes="card-title")
                        yield Label(self.client.email or "No mailbox active (Click Generate)", id="lbl-active-email", classes="email-text")
                        with Horizontal():
                            yield Button("Generate New Email", id="btn-gen-email", classes="success")
                            yield Button("Refresh Messages", id="btn-refresh-inbox")

                    with Container(classes="card"):
                        yield Label("Incoming Messages (Inbox)", classes="card-title")
                        yield DataTable(id="tbl-messages")

            # 2. MESSAGE DETAIL
            with TabPane("Message Viewer", id="tab-viewer"):
                with ScrollableContainer():
                    with Container(classes="card"):
                        yield Label("Email Inspector", classes="card-title")
                        yield Label("Sender: -", id="lbl-msg-from")
                        yield Label("Subject: -", id="lbl-msg-subject")
                        yield Label("Date: -", id="lbl-msg-date")
                        yield Label("Preview / Body:", classes="card-title")
                        yield Static("Select a message from the Inbox to read content.", id="lbl-msg-body")
                        yield Button("View Raw EML Source", id="btn-view-source")

            # 3. OTP & CODE EXTRACTOR
            with TabPane("OTP Extractor", id="tab-otp"):
                with ScrollableContainer():
                    with Vertical(classes="otp-banner"):
                        yield Label("Latest Detected Verification Code / OTP:", classes="card-title")
                        yield Label("None Detected Yet", id="lbl-detected-otp", classes="otp-val")
                        yield Label("Automatically parses 4-8 digit OTP codes from incoming mail subject & body.", classes="card-title")

                    with Container(classes="card"):
                        yield Label("Extracted Code History", classes="card-title")
                        yield Log(id="log-otp-history")

            # 4. SETTINGS
            with TabPane("Settings", id="tab-settings"):
                with ScrollableContainer():
                    with Container(classes="card"):
                        yield Label("API Configuration", classes="card-title")
                        yield Label("Base URL:")
                        yield Input(value=self.config.get("base_url"), id="inp-cfg-url")
                        yield Label("User Agent:")
                        yield Input(value=self.config.get("user_agent"), id="inp-cfg-ua")
                        yield Label("Active Session Token (JWT):")
                        yield Input(value=self.client.token, id="inp-cfg-token", password=True)
                        with Horizontal():
                            yield Label("Mock Mode: ")
                            yield Switch(value=self.config.get("mock_mode"), id="sw-mock")
                        yield Button("Save Configuration", id="btn-save-cfg")

            # 5. ACTIVITY LOG
            with TabPane("Activity Log", id="tab-log"):
                with Container(classes="card"):
                    yield Label("Live Request Log", classes="card-title")
                    yield Log(id="log-main")

        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#tbl-messages", DataTable)
        table.add_columns("ID", "From", "Subject", "Date / Time")
        self.log_action("TempMail TUI initialized.")

        # If no email is set, generate one automatically
        if not self.client.email:
            self.action_new_email()
        else:
            self.action_refresh_inbox()

    def log_action(self, msg: str) -> None:
        try:
            log = self.query_one("#log-main", Log)
            log.write_line(f"[{time.strftime('%H:%M:%S')}] {msg}")
        except Exception:
            pass

    def action_new_email(self) -> None:
        self.log_action("Requesting new temporary mailbox from mob2.temp-mail.org...")
        res = self.client.new_mailbox()
        if "mailbox" in res:
            email = res["mailbox"]
            self.query_one("#lbl-active-email", Label).update(email)
            self.query_one("#inp-cfg-token", Input).value = self.client.token
            self.log_action(f"Generated new mailbox: {email}")
            self.action_refresh_inbox()
        else:
            self.log_action(f"Failed to generate mailbox: {res}")

    def action_refresh_inbox(self) -> None:
        self.log_action("Checking for incoming messages...")
        msgs = self.client.get_messages()
        self.messages = msgs
        table = self.query_one("#tbl-messages", DataTable)
        table.clear()

        for m in msgs:
            mid = m.get("_id", "N/A")
            mfrom = m.get("from", "Unknown")
            msubject = m.get("subject", "(No Subject)")
            ts = m.get("receivedAt", 0)
            date_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts)) if ts else "-"
            table.add_row(mid, mfrom, msubject, date_str, key=mid)

            # Check for OTP in subject or preview
            full_txt = f"{msubject} {m.get('bodyPreview', '')}"
            matches = re.findall(r"\b\d{4,8}\b", full_txt)
            if matches:
                otp = matches[0]
                self.query_one("#lbl-detected-otp", Label).update(f"CODE: {otp}")
                self.query_one("#log-otp-history", Log).write_line(f"[{date_str}] {otp} from {mfrom} ({msubject})")
                self.log_action(f"Extracted OTP code: {otp}")

        self.log_action(f"Inbox refreshed: {len(msgs)} messages found.")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "btn-gen-email":
            self.action_new_email()
        elif bid == "btn-refresh-inbox":
            self.action_refresh_inbox()
        elif bid == "btn-save-cfg":
            self.config.set("base_url", self.query_one("#inp-cfg-url", Input).value)
            self.config.set("user_agent", self.query_one("#inp-cfg-ua", Input).value)
            self.config.set("mock_mode", self.query_one("#sw-mock", Switch).value)
            self.config.save()
            self.log_action("Settings saved successfully.")

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        row_key = event.row_key.value
        for m in self.messages:
            if m.get("_id") == row_key:
                self.query_one("#lbl-msg-from", Label).update(f"Sender: {m.get('from')}")
                self.query_one("#lbl-msg-subject", Label).update(f"Subject: {m.get('subject')}")
                ts = m.get("receivedAt", 0)
                date_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts)) if ts else "-"
                self.query_one("#lbl-msg-date", Label).update(f"Date: {date_str}")
                body = m.get("bodyPreview") or m.get("bodyHtml") or "(Empty Body)"
                self.query_one("#lbl-msg-body", Static).update(body)
                self.log_action(f"Viewing message: {m.get('subject')}")
                break
