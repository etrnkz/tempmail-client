"""
TempMail Core API Client
"""

import json
import time
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional
from .config import TempMailConfig, DEFAULT_BASE_URL, DEFAULT_USER_AGENT


class TempMailClient:
    """High-level Python API client for Temp-Mail."""

    def __init__(self, config: Optional[TempMailConfig] = None):
        self.config = config or TempMailConfig()
        self.email: str = self.config.get("current_email", "")
        self.token: str = self.config.get("current_token", "")

    def _headers(self, require_auth: bool = False) -> Dict[str, str]:
        headers = {
            "User-Agent": self.config.get("user_agent", DEFAULT_USER_AGENT),
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        if require_auth and self.token:
            headers["Authorization"] = self.token
        return headers

    def _request(self, endpoint: str, method: str = "GET", data: Optional[bytes] = None, require_auth: bool = False) -> Dict[str, Any]:
        if self.config.get("mock_mode"):
            if endpoint == "/mailbox" and method == "POST":
                self.email = f"mock_{int(time.time())}@tempmail.org"
                self.token = "mock_token_jwt"
                return {"mailbox": self.email, "token": self.token}
            elif endpoint == "/mailbox" and method == "GET":
                return {"mailbox": self.email or "mock_user@tempmail.org"}
            elif "/messages" in endpoint:
                return {
                    "mailbox": self.email,
                    "messages": [
                        {
                            "_id": "mock_msg_1",
                            "from": "service@verify.com",
                            "subject": "Your verification code is 492019",
                            "receivedAt": time.time(),
                            "bodyPreview": "Welcome! Use code 492019 to verify your account.",
                            "bodyHtml": "<h1>Welcome</h1><p>Your code is <b>492019</b></p>",
                            "attachmentsCount": 0
                        }
                    ]
                }
            return {"status": "SUCCESS"}

        url = f"{self.config.get('base_url', DEFAULT_BASE_URL)}{endpoint}"
        headers = self._headers(require_auth=require_auth)
        req = urllib.request.Request(url, data=data, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                content = resp.read().decode("utf-8", "replace")
                return json.loads(content)
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", "replace")
            try:
                return {"error": True, "http_code": e.code, "details": json.loads(err_body)}
            except Exception:
                return {"error": True, "http_code": e.code, "message": err_body}
        except Exception as e:
            return {"error": True, "message": str(e)}

    # ------------------ Core API Methods ------------------

    def new_mailbox(self) -> Dict[str, Any]:
        """Generate a new temporary mailbox address and save session credentials."""
        res = self._request("/mailbox", method="POST", data=b"{}")
        if "mailbox" in res and "token" in res:
            self.email = res["mailbox"]
            self.token = res["token"]
            self.config.set("current_email", self.email)
            self.config.set("current_token", self.token)
            self.config.save()
        return res

    def get_mailbox(self) -> Dict[str, Any]:
        """Fetch status and verify current mailbox."""
        return self._request("/mailbox", method="GET", require_auth=True)

    def get_messages(self, after_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch incoming emails in the inbox."""
        endpoint = "/messages"
        if after_id:
            endpoint += f"?after={after_id}"
        res = self._request(endpoint, method="GET", require_auth=True)
        if isinstance(res, dict) and "messages" in res:
            return res.get("messages", [])
        return []

    def get_message_detail(self, email_id: str) -> Dict[str, Any]:
        """Retrieve full details of a specific email, including HTML body."""
        return self._request(f"/messages/{email_id}/", method="GET", require_auth=True)

    def get_message_source(self, email_id: str) -> str:
        """Retrieve raw RFC822/EML message source."""
        url = f"{self.config.get('base_url', DEFAULT_BASE_URL)}/messages/{email_id}/source"
        headers = self._headers(require_auth=True)
        headers["Accept"] = "application/octet-stream"
        req = urllib.request.Request(url, headers=headers, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                return resp.read().decode("utf-8", "replace")
        except Exception as e:
            return f"Error fetching source: {e}"

    def wait_for_code(self, timeout_secs: int = 60, interval: int = 3) -> Optional[Dict[str, Any]]:
        """Poll the mailbox until an email is received, then return it."""
        start = time.time()
        while time.time() - start < timeout_secs:
            msgs = self.get_messages()
            if msgs:
                return msgs[0]
            time.sleep(interval)
        return None
