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

    # Rendered banner title
    banner_subtitle    = "Made using XRP, Python, and a LOT of coffee by XNET."
    banner_description = "Thank you for using XNET Airdrop! Airdrop is a small utility program built to make the most tedious aspect of initial token distribution (Commonly known as airdropping) easier — The calculation aspect of it. Airdrop will automatically fetch all trustlines set against the desired currency so it can then calculate the total yield per trustline token, which is then finally filtered and organized into a table for you to use as the total distribution table for the distribution itself.\n\n"
    banner_note        = "Airdrop does NOT require or send any token of any kind. It is just an utility that does the required math for you, and formats the resulting data into an easy-to-use format.\n\n"
    banner_disclaimer  = "DISCLAIMER: We (XNET and all XNET affiliated entities) are not responsible for any loss of funds, or any damages of any kind that result in the use of this program. We also ask all users to double check all generated output for validity and correctness. We do not guarantee the resulting data of any kind being factually correct. By using this software you agree to these terms.\n"

    # Metadata fetch
    metadata_fetch     = "[[info]WORKING[/info]] Fetching prequisite metadata..."
    error_fetch_failed = "[[error]FAIL[/error]] Failed fetching prequisite metadata. Make sure you have an active internet connection, and that XRPLMeta services are available."

    # Input yielding address
    enter_yielding           = Template('[prominent](${step}/${maximum})[/prominent] Enter yield token issuing address or "XRP" for XRP yield')
    error_yielding_voerwrite = Template('[[error]FAIL[/error]] Yielding issuing address "${address}" cannot be set, as overwriting the yielding issuing address is forbidden')

    # Input issuing address
    choose_token           = Template('We detected [prominent]${total}[/prominent] tokens issued by address [prominentb}${address}[/prominent}:\n\n${tokens}\n\nPlease enter the number of one from the list above')
    enter_issuer           = Template('[prominent](${step}/${maximum})[/prominent] Enter source token issuing address')
    error_issuer_invalid   = Template('[[error]FAIL[/error]] Issuing address "${address}" isn\'t a known token issuing address. Please make sure you have entered the address correctly, and that one or more tokens issued by this address has a trust level of 1 or greater on the XRPL')
    error_issuer_overwrite = Template('[[error]FAIL[/error]] Source issuing address "${address}" cannot be set, as overwriting the source issuing address is forbidden')

    # Input budget validation
    enter_balance    = Template('[prominent](${step}/${maximum})[/prominent] Enter the total airdrop budget')
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
