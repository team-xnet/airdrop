"""CLI functionality for our Airdrop utility."""
"""Author: spunk-developer <xspunk.developer@gmail.com>"""

from typing import Optional
from typer  import Option, Typer, Exit
from rich   import print

init_cli = Typer()

from airdrop import __app_version__, __app_name__
from airdrop.xrpl import fetch_trustlines, get_client

def get_version(value: bool) -> None:
	if value:
		print(f"{__app_name__} v{ __app_version__ }")
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
	address: str = Option(
		help="Specifies",
		prompt="Enter token issuing address",
		prompt_required=True
	),
	csv: Optional[str] = Option(
		None,
        "--csv",
        "-c",
        help="Outputs CSV file containing calculated airdrop ratios and values.",
	)
) -> None:
	with get_client(True) as client:
		trustlines = fetch_trustlines(address, client)

@init_cli.command(help="Executes program on TestNet for development and testing purpouses.")
def testnet(
	address: str = Option(
		help="Specifies",
		prompt="Enter token issuing address",
		prompt_required=True
	),
	csv: Optional[str] = Option(
		None,
        "--csv",
        "-c",
        help="Outputs CSV file containing calculated airdrop ratios and values.",
		prompt="Enter CSV file output path"
	)
) -> None:
	with get_client(False) as client:
		trustlines = fetch_trustlines(address, client)
