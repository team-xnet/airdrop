"""CLI functionality for our Airdrop utility."""
"""Author: spunk-developer <xspunk.developer@gmail.com>"""

from typing import Optional
from typer  import  Option, Typer, Exit, echo

init_cli = Typer()

from airdrop import __app_version__, __app_name__

def get_version(value: bool) -> None:
	if value:
		echo(f"{__app_name__} v{ __app_version__ }")
		raise Exit()

@init_cli.callback()
def main(
    version: Optional[bool] = Option(
    	None,
        "--version",
        "-v",
        help="Show Airdrop's version before exiting the program.",
        callback=get_version,
        is_eager=True
	)
) -> None:
	return

@init_cli.command(help="Executes program on live XRP ledger.")
def mainnet(
	csv: Optional[bool] = Option(
		True,
        "--csv",
        "-c",
        help="Outputs CSV file containing calculated airdrop ratios and values."
	),
	path: Optional[str] = Option(
		None,
		"--path",
		"-p",
		help="Output CSV file relative path."
	)
) -> None:
	return

@init_cli.command(help="Executes program on TestNet for development and testing purpouses.")
def testnet(
	csv: Optional[bool] = Option(
		True,
        "--csv",
        "-c",
        help="Outputs CSV file containing calculated airdrop ratios and values."
	),
	path: Optional[str] = Option(
		None,
		"--path",
		"-p",
		help="Output CSV file relative path."
	)
) -> None:
	return
