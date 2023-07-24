"""The actual procdere steps needed to finish the whole airdrop."""
"""Author: spunk-developer <xspunk.developer@gmail.com>"""

from rich.progress import Progress
from rich.padding  import Padding
from rich.table    import Table
from rich.panel    import Panel
from rich.text     import Text
from datetime      import timedelta
from typing        import Union
from typer         import Exit
from time          import time

from airdrop.xrpl import fetch_account_balance, fetch_trustlines, get_yielding, get_client, get_issuer
from airdrop.calc import get_budget
from airdrop.csv  import generate_csv, get_csv
from airdrop      import console, i18n, t

FETCHED_TRUSTLINE_BALANCES: Union[None, dict[str, float]] = None

FETCHED_TARGET_TRUSTLINES:  Union[None, list[str]]        = None

AIRDROP_START_TIME:         Union[None, float]            = None

RESULT_TRUSTLINES_YIELD:    Union[None, dict[str, float]] = None

RESULT_TRUSTLINES_TOTAL:    Union[None, float]            = None

RESULT_RATIO:               Union[None, float]            = None

def step_begin_airdrop_calculations():
    """Prints the beginning message and takes a time snapshot for future timings."""

    global AIRDROP_START_TIME

    AIRDROP_START_TIME = time()

    start_marker = Text.assemble(
        ("B" , "#902EF4"), ("e" , "#7F41FE"), ("g" , "#6C50FF"),
        ("i" , "#535CFF"), ("n" , "#2E67FF"), ("n" , "#0071FF"),
        ("i" , "#007AFF"), ("n" , "#0082FF"), ("g ", "#008AFF"),
                           ("a" , "#0091FF"), ("i" , "#0098FF"),
        ("r" , "#009EFF"), ("d" , "#00A5FF"), ("r" , "#00ABFF"),
        ("o" , "#00B0FF"), ("p ", "#00B6FF"),
        ("c" , "#00BBFF"), ("a" , "#00C0FF"), ("l" , "#00C5FF"),
        ("c" , "#00CAFF"), ("u" , "#00CFFF"), ("l" , "#00D3FF"),
        ("a" , "#00D7FF"), ("t" , "#00DCFF"), ("i" , "#00E0FF"),
        ("o" , "#00E4FF"), ("n" , "#00E8FC"), ("s" , "#00EbF9"),
        ("." , "#00EFF5"), ("." , "#39F3F2"), ("." , "#57F6F0")
    )

    console.print(Padding(start_marker, (1, 3)))


def step_fetch_issuer_trustlines():
    """Begins the initial part of the airdrop process - Fetching the trustlines set against a given token.

    Raises:
        Exit: If the request fails or returns un-validated data from the XRPL.
    """

    global FETCHED_TARGET_TRUSTLINES

    issuing_metadata = get_issuer()

    address = issuing_metadata[0]
    token   = issuing_metadata[1]

    start_time = time()

    with get_client() as client:
        with console.status(t(i18n.steps.trustlines_fetch, address=address), spinner="dots") as status:
            try:
                status.start()
                FETCHED_TARGET_TRUSTLINES = fetch_trustlines(address, token, client)
                status.stop()

            except Exception:
                status.stop()
                console.print(t(i18n.steps.error_trustline_fetch, address=address))
                raise Exit()

    console.print(t(i18n.steps.trustlines_fetch_success, count=len(FETCHED_TARGET_TRUSTLINES), address=address, delta=timedelta(seconds=int(time() - start_time))))


def step_fetch_trustline_balances():
    """Fetches all trustline balances required to do the final calculations.

    Raises:
        Exit: Most likely getting rate limited.
    """

    global FETCHED_TRUSTLINE_BALANCES, FETCHED_TARGET_TRUSTLINES

    FETCHED_TRUSTLINE_BALANCES = { }

    yielding_metadata = get_yielding()

    token = yielding_metadata[0]
    name  = yielding_metadata[1]

    if isinstance(name, type(None)):
        name = token

    start_time = time()

    with get_client() as client:
        with console.status(i18n.steps.balances_fetch, spinner="dots") as status:

            status.start()

            try:
                for trustline in FETCHED_TARGET_TRUSTLINES:

                    if trustline in FETCHED_TRUSTLINE_BALANCES:
                        continue

                    status.update(t(i18n.steps.balances_fetch_account, address=trustline, token=name))

                    FETCHED_TRUSTLINE_BALANCES[trustline] = fetch_account_balance(trustline, token, client)

                status.stop()
                console.print(t(i18n.steps.balances_fetch_success, count=len(FETCHED_TRUSTLINE_BALANCES), delta=timedelta(seconds=int(time() - start_time))))

            except:
                status.stop()
                console.print(i18n.steps.error_balances)
                raise Exit()


def step_calculate_airdrop_yield():
    """Generates all user-facing text into console while calculating all airdrop related balances.
    """

    global FETCHED_TRUSTLINE_BALANCES, RESULT_TRUSTLINES_YIELD, RESULT_TRUSTLINES_TOTAL, RESULT_RATIO

    budget = get_budget()

    if isinstance(RESULT_TRUSTLINES_TOTAL, type(None)):
        RESULT_TRUSTLINES_TOTAL = float(0)

    if isinstance(RESULT_TRUSTLINES_YIELD, type(None)):
        RESULT_TRUSTLINES_YIELD = { }

    with console.status(i18n.steps.yield_sum, spinner="dots") as status:

        status.start()

        for balance in FETCHED_TRUSTLINE_BALANCES.values():
            RESULT_TRUSTLINES_TOTAL += balance

        RESULT_RATIO = budget / RESULT_TRUSTLINES_TOTAL

        status.stop()

    with Progress(console=console) as progress:

        task = progress.add_task(description=i18n.steps.yield_result, start=False, total=len(FETCHED_TRUSTLINE_BALANCES))

        for address, balance in FETCHED_TRUSTLINE_BALANCES.items():
            progress.update(task, description=t(i18n.steps.yield_result_account, address=address))

            RESULT_TRUSTLINES_YIELD[address] = balance * RESULT_RATIO

            progress.advance(task)

        progress.remove_task(task)


def step_end_airdrop_calculations():
    """Prints total ratio into console while saving OR printing results as well.

    Raises:
        Exit: If CSV saving was chosen, being unable to save to chosen path.
    """

    global FETCHED_TRUSTLINE_BALANCES, FETCHED_TARGET_TRUSTLINES, RESULT_TRUSTLINES_YIELD, RESULT_TRUSTLINES_TOTAL, AIRDROP_START_TIME, RESULT_RATIO

    yielding_metadata = get_yielding()
    path              = get_csv()

    token = yielding_metadata[0]
    name  = yielding_metadata[1]

    if isinstance(name, type(None)):
        name = token

    if isinstance(path, type(None)):

        table = Table(title=i18n.steps.print_header)

        table.add_column("Address", justify="left", style="#902EF4")
        table.add_column(name,      justify="left", style="#0098FF")
        table.add_column("Yield",   justify="left", style="#00CFFF")
        table.add_column("Split",   justify="left", style="#57F6F0")

        for address in FETCHED_TARGET_TRUSTLINES:

            balance = f'{ FETCHED_TRUSTLINE_BALANCES[address] }'
            result  = f'{ RESULT_TRUSTLINES_YIELD[address] }'
            split   = f'{ (RESULT_TRUSTLINES_YIELD[address] / RESULT_TRUSTLINES_TOTAL) * 100 }'

            table.add_row(address, balance, result, split)

        console.print(table)

    else:

        headers = [ "Address", f'{ name }', "Yield", "Split" ]
        data    = [ ]

        for address in FETCHED_TARGET_TRUSTLINES:

            balance = FETCHED_TRUSTLINE_BALANCES[address]
            result  = RESULT_TRUSTLINES_YIELD[address]
            split   = (result / RESULT_TRUSTLINES_TOTAL) * 100

            data.append(
                {
                    "Address"  : address,
                    f'{ name }': balance,
                    "Yield"    : result,
                    "Split"    : f'{ split }%'
                }
            )

        if not generate_csv(path, headers, data):
            console.print(t(i18n.steps.error_saving_csv, path=path))
            raise Exit()

    results = Table(box=None, show_header=False, show_edge=False, padding=(1, 1))

    results.add_column(justify="left")
    results.add_column(justify="center")

    results.add_row(
        Text("Trustlines", "#902EF4"),
        Text(f'{ len(FETCHED_TARGET_TRUSTLINES) }', "#902EF4")
    )

    results.add_row(
        Text("Trustline sum", "#0098FF"),
        Text(f'{ RESULT_TRUSTLINES_TOTAL }', "#0098FF")
    )

    results.add_row(
        Text("Airdrop ratio", "#00CFFF"),
        Text(f'{ RESULT_RATIO }', "#00CFFF")
    )

    results.add_row(
        Text("Total elapsed time", "#57F6F0"),
        Text(str(timedelta(seconds=int(time() - AIRDROP_START_TIME))), "#57F6F0")
    )

    console.print(Panel(results, padding=(1, 3), subtitle=i18n.steps.print_subtitle, subtitle_align="left", border_style="#1B6AFF"))
