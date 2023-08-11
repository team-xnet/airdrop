"""CLI functionality for our Airdrop utility.          """
"""Author: spunk-developer <xspunk.developer@gmail.com>"""

from pathlib       import Path
from typing        import Optional
from typer         import Option, Typer, Exit

from airdrop.preflight import preflight_validate_yielding_address, preflight_validate_issuing_address, preflight_validate_supply_balance, preflight_fetch_metadata, preflight_validate_output, preflight_print_banner, preflight_check_cache, preflight_confirm
from airdrop.steps     import step_begin_airdrop_calculations, step_fetch_trustline_balances, step_calculate_airdrop_yield, step_end_airdrop_calculations, step_fetch_issuer_trustlines
from airdrop.cache     import rehydrate_terms_of_use
from airdrop           import __app_version__, __app_name__, console

cli = Typer()


def get_version(value: bool) -> None:
    if value:
        console.print(f'{__app_name__} v{ __app_version__ }')
        raise Exit()


@cli.command(help="Parses and distributes calculated airdrop yield to given trustline addresses.")
def distribute(
    budget: Optional[float] = Option(
        None,
        "--budget",
        "-b",
        help="Specifies the total airdrop supply budget that was used previously."
    ),
    ratio: Optional[float] = Option(
        None,
        "--ratio",
        "-r",
        help="Final calculated ratio for the airdrop."
    ),
    csv: Optional[Path] = Option(
        None,
        "--csv",
        "-c",
        help="Specifies the input CSV file path.",
        resolve_path=True,
        file_okay=True
    )
):
    # Pre-preflight stuff
    console.clear()
    rehydrate_terms_of_use()


@cli.command(help="Runs airdrop calculations for given issuing address trustline holders.")
def calculate(
    issuing_address: Optional[str] = Option(
        None,
        "--issuing-address",
        "-i",
        help="Specifies the issuing address for the token to be airdropped. This address is also used to fetch a list of all trustlines set against the airdropped token, which is then used to calculate the total yield per token.",
    ),
    yielding_address: Optional[str] = Option(
        None,
        "--yielding-address",
        "-y",
        help="Specifies the the issuing address for the token that is used to calculate the actual airdrop distribution (Issuing token per yield token) itself.",
    ),
    budget: Optional[float] = Option(
        None,
        "--budget",
        "-b",
        help="Specifies the total airdrop supply budget."
    ),
    csv: Optional[Path] = Option(
        None,
        "--csv",
        "-c",
        help="Specifies the output CSV file path.",
        resolve_path=True,
        file_okay=True,
        dir_okay=False,
        writable=True
    )
):
    # Pre-preflight stuff
    console.clear()
    rehydrate_terms_of_use()

    # Preflight stuff
    preflight_check_cache()
    preflight_print_banner()
    preflight_fetch_metadata(issuing_address, yielding_address, budget, csv)
    preflight_validate_issuing_address(issuing_address)
    preflight_validate_yielding_address(yielding_address)
    preflight_validate_supply_balance(budget)
    preflight_validate_output(csv)
    preflight_confirm()

    # Main procedure
    step_begin_airdrop_calculations()
    step_fetch_issuer_trustlines()
    step_fetch_trustline_balances()
    step_calculate_airdrop_yield()
    step_end_airdrop_calculations()


@cli.callback()
def main(
    version: Optional[bool] = Option(
        None,
        "--version",
        "-v",
        help="Show Airdrop's version and exit.",
        callback=get_version,
        is_eager=True
    )
) -> None:
    return
