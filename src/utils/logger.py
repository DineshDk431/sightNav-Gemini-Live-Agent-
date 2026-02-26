"""
SightNav — Terminal Logger
==========================
Provides coloured, structured console output with distinct prefixes
for every subsystem so you can follow the Perception → Plan → Act
→ Verify → Reflect loop at a glance.
"""

import sys
from datetime import datetime


class Colors:
    """ANSI escape codes for terminal colouring."""
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"

    # Foreground
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"

    # Backgrounds (used sparingly for critical banners)
    BG_RED    = "\033[41m"
    BG_GREEN  = "\033[42m"
    BG_BLUE   = "\033[44m"
    BG_CYAN   = "\033[46m"
    BG_YELLOW = "\033[43m"


class Logger:
    """
    Centralised, colour-coded terminal logger for SightNav.

    Usage
    -----
    >>> from src.utils.logger import Logger
    >>> Logger.info("System booted")
    >>> Logger.agent("VisionAgent", "Detected login button at (450, 600)")
    >>> Logger.success("Mouse click executed")
    >>> Logger.warn("Coordinate near screen edge — may miss target")
    >>> Logger.error("JSON parse failed — retrying")
    """

    # ── Private helpers ────────────────────────────────────────────
    @staticmethod
    def _timestamp() -> str:
        return datetime.now().strftime("%H:%M:%S")

    @staticmethod
    def _print(color: str, prefix: str, message: str, bold: bool = False) -> None:
        ts = Logger._timestamp()
        b = Colors.BOLD if bold else ""
        line = (
            f"{Colors.DIM}[{ts}]{Colors.RESET} "
            f"{b}{color}{prefix}{Colors.RESET} "
            f"{message}"
        )
        print(line, flush=True)

    # ── Public API ─────────────────────────────────────────────────

    @staticmethod
    def info(message: str) -> None:
        """General informational message."""
        Logger._print(Colors.CYAN, "ℹ  INFO  ", message)

    @staticmethod
    def success(message: str) -> None:
        """Something worked as expected."""
        Logger._print(Colors.GREEN, "✔  OK    ", message, bold=True)

    @staticmethod
    def warn(message: str) -> None:
        """Non-fatal warning."""
        Logger._print(Colors.YELLOW, "⚠  WARN  ", message)

    @staticmethod
    def error(message: str) -> None:
        """Error that may need attention."""
        Logger._print(Colors.RED, "✖  ERROR ", message, bold=True)

    @staticmethod
    def agent(agent_name: str, message: str) -> None:
        """Log from a named sub-agent (Vision, Reflection, Audio)."""
        tag = f"🤖 {agent_name.upper():<12}"
        Logger._print(Colors.MAGENTA, tag, message)

    @staticmethod
    def action(message: str) -> None:
        """Physical action about to be executed (mouse / keyboard)."""
        Logger._print(Colors.BLUE, "⚡ ACTION", message, bold=True)

    @staticmethod
    def memory(message: str) -> None:
        """Read / write to the long-term memory file."""
        Logger._print(Colors.YELLOW, "🧠 MEMORY", message)

    @staticmethod
    def user(message: str) -> None:
        """Echo of what the user said / typed."""
        Logger._print(Colors.WHITE, "👤 USER  ", message, bold=True)

    @staticmethod
    def divider(label: str = "") -> None:
        """Visual separator for the terminal."""
        width = 60
        if label:
            pad = (width - len(label) - 2) // 2
            line = f"{'─' * pad} {label} {'─' * pad}"
        else:
            line = "─" * width
        print(f"{Colors.DIM}{line}{Colors.RESET}", flush=True)

    @staticmethod
    def banner() -> None:
        """Startup ASCII banner."""
        art = rf"""
{Colors.CYAN}{Colors.BOLD}
  ███████╗██╗ ██████╗ ██╗  ██╗████████╗███╗   ██╗ █████╗ ██╗   ██╗
  ██╔════╝██║██╔════╝ ██║  ██║╚══██╔══╝████╗  ██║██╔══██╗██║   ██║
  ███████╗██║██║  ███╗███████║   ██║   ██╔██╗ ██║███████║██║   ██║
  ╚════██║██║██║   ██║██╔══██║   ██║   ██║╚██╗██║██╔══██║╚██╗ ██╔╝
  ███████║██║╚██████╔╝██║  ██║   ██║   ██║ ╚████║██║  ██║ ╚████╔╝
  ╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═══╝╚═╝  ╚═╝  ╚═══╝
{Colors.RESET}
{Colors.DIM}  Visual AI Desktop Navigator · Powered by Gemini{Colors.RESET}
{Colors.DIM}  ─────────────────────────────────────────────────{Colors.RESET}
"""
        print(art, flush=True)
