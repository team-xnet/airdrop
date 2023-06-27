"""CLI functionality for our Airdrop utility."""
"""Author: spunk-developer <xspunk.developer@gmail.com>"""

from typing import Optional, Union
from typer  import Option, Typer, Exit

from airdrop import console

init_cli = Typer()

from airdrop import __app_version__, __app_name__
from airdrop.xrpl import fetch_trustlines, get_client

def get_version(value: bool) -> None:
	if value:
		console.print(f'{__app_name__} v{ __app_version__ }')
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

def do_command_routine(mainnet: bool, address: str, csv: Union[None, str]):
	with get_client(mainnet) as client:
		trustlines = None
		# Fetch trustline addresses. We fecth XRP & SOLO balances separately.
		with console.status(f'[[info]WORKING[/info]] Fetching trustlines from address [prominent]{address}[/prominent]...', spinner="dots") as status:
			status.start()
			result = fetch_trustlines(address, client)
			status.stop()
			if result is None:
				console.print(f'[[error]FAIL[/error]] Failed fetching trustlines from address [prominent]{address}[/prominent]!')
			console.print(f'[[success]SUCCESS[/success]] Successfully fetched [prominent]{len(result)}[/prominent] trustlines set for issuing address [prominent]{address}[/prominent]')
			trustlines = result

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
	do_command_routine(True, address, csv)

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
	do_command_routine(False, address, csv)
