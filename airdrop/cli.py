"""CLI functionality for our Airdrop utility."""

from typing import Optional
from typer  import Option, Typer, Exit, echo

init_cli = Typer()

from airdrop import __app_version__, __app_name__

def get_version(value: bool) -> None:
    if value:
        echo(f"{__app_name__} v{ __app_version__ }")
        raise Exit()

def enable_mainnet(value: bool) -> None:
	pass

@init_cli.callback()
def main(
    version: Optional[bool] = Option(
    	None,
        "--version",
        "-v",
        help="Show Airdrop's version before exiting the program.",
        callback=get_version,
        is_eager=True
	),
    mainnet: bool = Option(
		False,
        "--main-net",
        "-m",
        help="Disables dry running, enabling mainnet functionality."
	),
    csv: Optional[bool] = Option(
		True,
        "--csv",
        "-c",
        help="Outputs CSV file containing calculated airdrop ratios and values."
	)
) -> None:
    return
