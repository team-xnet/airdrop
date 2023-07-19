"""XNET & XSPUNKS airdrop utility."""
"""Author: spunk-developer <xspunk.developer@gmail.com>"""

from string import Template

from rich.console import Console
from dataclasses  import dataclass
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

@dataclass(frozen=True)
class I18NPreflight():

    # Input budget validation strings
    enter_balance    = "Enter the total airdrop budget"
    error_conversion = Template('[[error]FAIL[/error]] Could not converty input "${value}" into a number')
    error_overwrite  = "[[error]FAIL[/error]] Cannot overwrite supply budget, as it has already been defined"
    error_minimum    = Template('[[error]FAIL[/error]] Input "${value}" must be larger than 0')
    error_maximum    = Template('[[error]FAIL[/error]] Input "${value}" cannot be larger than maximum allowed integer 100000000000000000')

@dataclass(frozen=True)
class I18NBase():
    preflight = I18NPreflight()

console = Console(color_system="auto", theme=CONSOLE_THEME)
i18n    = I18NBase()

def t(str: Template, **kwargs) -> str:
    return str.substitute(kwargs)
