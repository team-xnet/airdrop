"""XNET & XSPUNKS airdrop utility."""
"""Author: spunk-developer <xspunk.developer@gmail.com>"""

from rich.console import Console
from rich.theme   import Theme

__app_version__ = "0.1.0+alpha.1"
__app_name__    = "airdrop"

CONSOLE_THEME = Theme(
    {
        "prominent": "bright_yellow",
        "success":   "bright_green bold",
        "error":     "bright_red bold",
        "info":      "bright_blue bold",
        "warn":      "bright_magenta bold"
	}
)

console = Console(color_system="auto", theme=CONSOLE_THEME)
