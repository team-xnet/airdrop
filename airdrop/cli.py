"""CLI functionality for our Airdrop utility."""
"""Author: spunk-developer <xspunk.developer@gmail.com>"""

from rich.progress import Progress
from typing 	   import Optional, Union
from typer  	   import Option, Typer, Exit

from airdrop import console

init_cli = Typer()

from airdrop import __app_version__, __app_name__
from airdrop.xrpl import fetch_account_balances, fetch_trustlines, get_client

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
		trustlines         = None
		trustline_balances = []
		# Fetch trustline addresses. We fecth XRP & SOLO balances separately.
		with console.status(f'[[info]WORKING[/info]] Fetching trustlines from address [prominent]{address}[/prominent]...', spinner="dots") as status:
			try:
				status.start()
				result = fetch_trustlines(address, client)
				status.stop()
				if result is None:
					raise AssertionError
				console.print(f'[[success]SUCCESS[/success]] Successfully fetched [prominent]{len(result)}[/prominent] trustlines set for issuing address [prominent]{address}[/prominent]')
				trustlines = result
			except:
				status.stop()
				console.print(f'[[error]FAIL[/error]] Failed fetching trustlines from address [prominent]{address}[/prominent]!')
				return
		if (trustlines is None):
			return
		with Progress(console=console) as progress:
			task = progress.add_task(description="[[info]WORKING[/info]] Fetching account balances...", start=False, total=len(trustlines))
			success = 0
			failure = 0
			progress.start_task(task)
			for trustline in trustlines:
				# We don't care about the issuing address balance
				if trustline is address:
					progress.advance(task)
					continue
				try:
					balances = fetch_account_balances(trustline, client)
					trustline_balances.append(balances)
					progress.console.print(f'[[success]SUCCESS[/success]] Successfully fetched account balance(s) for [prominent]{trustline}[/prominent]')
					progress.advance(task)
					success += 1
				except:
					progress.remove_task(task)
					progress.console.print(f'[[error]FAIL[/error]] Couldn\'t fetch balance(s) for account [prominent]{trustline}[/prominent]!')
					failure += 1
					continue
			progress.remove_task(task)
			if success > failure:
				progress.console.print(f'[[success]SUCCESS[/success]] Successfully fetched balances for [prominent]{success}[/prominent] trustlines, with [prominent]{failure}[/prominent] misses')
			else:
				progress.console.print(f'[[error]FAIL[/error]] Failed fetching balances for [prominent]{failure}[/prominent] trustlines, with [prominent]{success}[/prominent] successful fetches')


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
