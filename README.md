# tempmail-client

> Simple, fast Python client & interactive Terminal UI for disposable Temp-Mail (`com.tempmail`).

Looking for the high-performance Rust implementation? Check out [**tempmail-rs**](https://github.com/neurals-et/tempmail-rs).

---

## Features

- **No API Key Required**: Directly interfaces with the official mobile gateway (`mob2.temp-mail.org`).
- **Interactive TUI**: Built with Textual for viewing inboxes, inspecting emails, and copying OTPs.
- **Auto OTP Parser**: Automatically extracts 4–8 digit verification codes from incoming mail.
- **CLI Utilities**: Generate addresses, check inboxes, or wait for codes straight from terminal.

---

## Installation

```bash
pip install tempmail-client
```

---

## Quickstart

### Terminal UI
```bash
tempmail
```

### CLI
```bash
# Generate a new disposable email address
tempmail new

# Check inbox
tempmail inbox

# Wait for an incoming verification code
tempmail code --timeout 60
```

### Python SDK
```python
from tempmail import TempMailClient

client = TempMailClient()

# 1. Create a mailbox
box = client.new_mailbox()
print("Email:", box["mailbox"])

# 2. Check inbox
messages = client.get_messages()
for msg in messages:
    print(f"From: {msg['from']} | Subject: {msg['subject']}")

# 3. Wait for OTP
code_msg = client.wait_for_code(timeout_secs=60)
```

---

## Related Projects

- [**tempmail-rs**](https://github.com/neurals-et/tempmail-rs) — Native asynchronous Rust client and CLI.

---

## License

MIT
