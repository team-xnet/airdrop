"""CLI functionality for our Airdrop utility."""
"""Author: spunk-developer <xspunk.developer@gmail.com>"""

from rich.progress import Progress
from datetime      import timedelta
from typing 	   import Optional, Union
from typer  	   import Option, Typer, Exit
from time          import time

from airdrop.operations import validate_supply_balance
from airdrop.xrpl       import fetch_account_balances, fetch_trustlines, get_client
from airdrop.calc       import calculate_total_yield, pick_balances_as_dict, increment_yield, update_budget
from airdrop            import __app_version__, __app_name__, console

init_cli = Typer()

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

# TODO(spunk-developer): Do pre-validation before the actual airdrop script starts. these would be:
#  - In the case that an issuing address has authored multiple tokens, allow the user to pick which token is the target airdropped token from a list
#  - Allow the user to set "rules", or perhaps pick a pre-defined algorithm? for the actual budget distribution calculation
#  - Redo all user-facing communication
def do_command_routine(mainnet: bool, address: str, csv: Union[None, str], token_id: str, amount: float):
	if amount == 0 or update_budget(amount) is not True:
		console.print('[[error]FAIL[/error]] Please set variable "amount" to a valid number that is higher than [prominent]0[/prominent]!')
		return
	with get_client(mainnet) as client:
		airdrop_start_time = time()
		trustlines         = None
		trustline_balances = []
		# Fetch trustline addresses. We fecth XRP & SOLO balances separately.
		with console.status(f'[[info]WORKING[/info]] Fetching trustlines from address [prominent]{address}[/prominent]...', spinner="dots") as status:
			start = time()
			try:
				status.start()
				result = fetch_trustlines(address, client)
				status.stop()
				if result is None:
					raise AssertionError
				console.print(f'[[success]SUCCESS[/success]] Successfully fetched [prominent]{len(result)}[/prominent] trustlines set for issuing address [prominent]{address}[/prominent] in [prominent]{timedelta(seconds=int(time() - start))}[/prominent]')
				trustlines = result
			except:
				status.stop()
				console.print(f'[[error]FAIL[/error]] Failed fetching trustlines from address [prominent]{address}[/prominent]!')
				return
		with Progress(console=console) as progress:
			task    = progress.add_task(description="[[info]WORKING[/info]] Fetching account balances...", start=False, total=len(trustlines))
			start   = time()
			success = 0
			failure = 0
			progress.start_task(task)
			for trustline in trustlines:
				# We don't care about the issuing address balance
				if trustline is address:
					progress.advance(task)
					continue
				try:
					balances_start = time()
					balances       = fetch_account_balances(trustline, client)
					trustline_balances.append(balances)
					progress.console.print(f'[[success]SUCCESS[/success]] Successfully fetched account balance(s) for [prominent]{trustline}[/prominent] in [prominent]{timedelta(seconds=int(time() - balances_start))}[/prominent]')
					progress.advance(task)
					success += 1
				except:
					progress.remove_task(task)
					progress.console.print(f'[[error]FAIL[/error]] Couldn\'t fetch balance(s) for account [prominent]{trustline}[/prominent]!')
					failure += 1
					continue
			progress.remove_task(task)
			if success > failure:
				progress.console.print(f'[[success]SUCCESS[/success]] Successfully fetched balances for [prominent]{success}[/prominent] trustlines, with [prominent]{failure}[/prominent] misses in [prominent]{timedelta(seconds=int(time() - start))}[/prominent]')
			else:
				progress.console.print(f'[[error]FAIL[/error]] Failed fetching balances for [prominent]{failure}[/prominent] trustlines, with [prominent]{success}[/prominent] successful fetches, aborting')
				return
		with console.status('[[info]WORKING[/info]] Calculating total airdrop yield...', spinner="dots") as status:
			start   = time()
			success = False
			status.start()
			for address, balances in trustline_balances:
				try:
					filtered_balances = pick_balances_as_dict(balances, token_id)
					if token_id in filtered_balances:
						increment_yield(token_id, filtered_balances[token_id])
						if trustline_balances.index((address, balances)) == (len(trustline_balances) - 1):
							success = True
				except:
					status.stop()
					success = False
					break
			if success is True:
				status.stop()
				calculate_total_yield(token_id)
				console.print(f'[[success]SUCCESS[/success]] Successfully calculated total airdrop yield in [prominent]{ timedelta(seconds=int(time() - start)) }[/prominent]')
			else:
				console.print(f'[[error]FAIL[/error]] Failed calculating total airdrop yield, aborting')
				return
		console.print(f'[[success]SUCCESS[/success]] Successfully computed airdrop in [prominent]{ timedelta(seconds=int(time() - airdrop_start_time)) }[/prominent]')

@init_cli.command(help="Executes program on live XRP ledger.")
def mainnet(
	address: str = Option(
		help="Specifies the issuing address for the token to be airdropped.",
		prompt="(1/3) Enter token issuing address",
		prompt_required=True
	),
	token: str = Option(
		help="Specifies the currency code for the token that airdrop recipients are required to hold to recieve airdrop yield.",
		prompt="(2/3) Enter airdrop calculation currency code",
		prompt_required=True
	),
	amount: str = Option(
		help="Specifies the total budget for the airdrop.",
		prompt="(3/3) Enter total amount of tokens that would be airdropped"
	),
	csv: Optional[str] = Option(
		None,
        "--csv",
        "-c",
        help="Outputs CSV file containing calculated airdrop ratios and values.",
	)
) -> None:

	# Supply balance validation
	try:
		validate_supply_balance(amount)
	except TypeError as err:
		console.print(f'[[error]FAIL[/error]] { err }')
		return
	except ValueError:
		console.print(f'[[error]FAIL[/error]] Cannot convert value [prominent]"{ amount }"[/prominent] into a number, aborting')
		return
	do_command_routine(True, address, csv, token, amount)
