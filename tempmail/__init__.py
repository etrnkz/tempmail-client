"""
TempMail Unofficial Python SDK & TUI
Reverse-engineered from TempMail Android App (com.tempmail)
"""

from .config import TempMailConfig
from .client import TempMailClient
from .tui import TempMailTUI

__version__ = "0.1.0"
__author__ = "etrnzk"
__license__ = "MIT"

__all__ = ["TempMailClient", "TempMailConfig", "TempMailTUI", "__version__"]
