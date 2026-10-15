# tempmail-client

[![PyPI version](https://img.shields.io/badge/pypi-v0.1.0-blue.svg)](https://pypi.org/project/tempmail-client/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

Fast, unofficial Python client library and interactive Terminal User Interface (TUI) for the **Temp-Mail** disposable email service (`com.tempmail`), reverse-engineered directly from the official Android mobile app.

---

## Features

- **Direct Mobile Gateway**: Leverages the official mobile endpoint (`https://mob2.temp-mail.org`) for fast, reliable inbox generation without API keys or browser automation.
- **Zero Credentials Needed**: Free, instant temporary mailbox creation with issued session JWTs.
- **Auto OTP / Verification Code Extractor**: Integrated regex parser to extract 4–8 digit verification codes from incoming message subjects and preview text.
- **Full Email Inspection**: Inspect senders, subjects, timestamps, rendered HTML, attachments, and raw RFC822 EML source.
- **Interactive TUI**: Built with [Textual](https://textual.textualize.io/) featuring real-time inbox polling, message reader, and OTP copy-paste stream.
- **Automation Ready**: Built-in CLI commands (`tempmail new`, `tempmail code`, `tempmail inbox`) and programmatic Python methods (`wait_for_code()`).

---

## Installation

```bash
pip install tempmail-client
```

Or from local source:

```bash
pip install .
```

---

## Interactive TUI

Launch the full terminal interface:

```bash
tempmail
# or
tempmail tui
```

### Keyboard Shortcuts
- `n` - Generate a brand new temporary mailbox address
- `r` - Refresh active inbox
- `q` - Quit the application

---

## Command Line Interface (CLI)

Generate a new temporary email and print to stdout:
```bash
tempmail new
```

View incoming messages:
```bash
tempmail inbox
```

Wait and output the next received verification code (great for CI/CD or automation scripts):
```bash
tempmail code --timeout 60
```

---

## Python SDK Usage

### Basic Usage

```python
from tempmail import TempMailClient

client = TempMailClient()

# 1. Generate new temporary mailbox
res = client.new_mailbox()
print("Mailbox:", res["mailbox"])
print("Token:", res["token"])

# 2. Check inbox
messages = client.get_messages()
for msg in messages:
    print(f"[{msg['_id']}] From: {msg['from']} - {msg['subject']}")

# 3. Wait for an incoming verification code
code_msg = client.wait_for_code(timeout_secs=60)
if code_msg:
    print("Received email:", code_msg["subject"])
```

### Inspecting Email Body & Source

```python
# Get detailed message body & attachments
details = client.get_message_detail(email_id="...")
print("HTML Body:", details.get("bodyHtml"))

# Fetch raw EML source
eml_source = client.get_message_source(email_id="...")
print("EML:\n", eml_source)
```

---

## Reverse-Engineered API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/mailbox` | Generate fresh mailbox + session JWT token |
| `GET` | `/mailbox` | Verify current active mailbox status |
| `GET` | `/messages` | List incoming inbox messages (`?after=<id>`) |
| `GET` | `/messages/{id}/` | Full email details and HTML payload |
| `GET` | `/messages/{id}/source` | Raw RFC822 / EML message source |
| `GET` | `/messages/{id}/attachment/{aid}/` | Download message attachment |

---

## License

MIT License. Built for security research and developer tooling.
