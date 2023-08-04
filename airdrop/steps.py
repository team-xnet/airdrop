"""The actual procdere steps needed to finish the whole airdrop."""
"""Author: spunk-developer <xspunk.developer@gmail.com>         """

from rich.progress import Progress
from rich.padding  import Padding
from rich.table    import Table
from rich.panel    import Panel
from rich.text     import Text
from datetime      import timedelta
from decimal       import Decimal
from typing        import Union
from typer         import Exit
from time          import sleep, time

from airdrop.xrpl import fetch_account_balance, fetch_trustlines, get_yielding, get_client, get_issuer
from airdrop.calc import calculate_airdrop_ratio, calculate_yield, increment_airdrop_sum, get_ratio, get_sum
from airdrop.csv  import generate_csv, get_csv
from airdrop      import console, i18n, t

AIRDROP_START_TIME:         Union[None, float] = None

FETCHED_TRUSTLINE_BALANCES: dict[str, Decimal] = { }

FETCHED_TARGET_TRUSTLINES:  list[str]          = [ ]

INDIVIDUAL_TRUSTILE_YIELD:  dict[str, Decimal] = { }

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

    console.print(Padding(start_marker, (1, 2)))


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
                FETCHED_TARGET_TRUSTLINES = fetch_trustlines(address, token[0], client)
                status.stop()

            except Exception as e:
                status.stop()
                console.print(e)
                console.print(t(i18n.steps.error_trustline_fetch, address=address))
                raise Exit()

    # @NOTE(spunk-developer): Add checkmark to the start of the message
    console.print(t(i18n.steps.trustlines_fetch_success, count=len(FETCHED_TARGET_TRUSTLINES), address=address, delta=timedelta(seconds=int(time() - start_time))))


def step_fetch_trustline_balances():
    """Fetches all trustline balances required to do the final calculations.

    Raises:
        Exit: Most likely getting rate limited.
    """

    global FETCHED_TRUSTLINE_BALANCES, FETCHED_TARGET_TRUSTLINES

    yielding_metadata = get_yielding()

    token = yielding_metadata[0]
    name  = yielding_metadata[1]

    if isinstance(name, type(None)):
        name = token

    start_time = time()

    with get_client() as client:
        with console.status(i18n.steps.balances_fetch, spinner="dots") as status:

            trustlines = FETCHED_TARGET_TRUSTLINES.copy()

            status.start()

            while True:

                trustline  = trustlines.pop()
                fail_timer = None

                try:

                    if trustline in FETCHED_TRUSTLINE_BALANCES:
                        trustline = trustlines.pop()
                        continue

                    if isinstance(fail_timer, type(None)):
                        status.update(t(i18n.steps.balances_fetch_account, address=trustline, token=name))

                    balance = fetch_account_balance(trustline, token, client)

                    if isinstance(balance, type(None)) or balance.is_zero():
                        continue

                    if not isinstance(fail_timer, type(None)):
                        fail_timer = None

                    FETCHED_TRUSTLINE_BALANCES[trustline] = balance

                    if len(trustlines) == 0:
                        break

                    trustline = trustlines.pop()

                except:

                    if isinstance(fail_timer, type(None)):
                        fail_timer = 10

                    else:

                        if fail_timer < 300:
                            fail_timer = fail_timer * 2

                        else:
                            fail_timer = 300

                        for delta in range(fail_timer):
                            status.update(t(i18n.steps.error_balances, address=trustline, delta=delta))

                            sleep(1)

            status.stop()
            console.print(t(i18n.steps.balances_fetch_success, count=len(FETCHED_TRUSTLINE_BALANCES), delta=timedelta(seconds=int(time() - start_time))))



def step_calculate_airdrop_yield():
    """Generates all user-facing text into console while calculating all airdrop related balances.
    """

    global FETCHED_TRUSTLINE_BALANCES, INDIVIDUAL_TRUSTILE_YIELD

    with console.status(i18n.steps.yield_sum, spinner="dots") as status:

        status.start()

        increment_airdrop_sum(FETCHED_TRUSTLINE_BALANCES.values())
        if not calculate_airdrop_ratio():
            # @TODO(spunk-developer): Do some fancy-ass error handling here.
            status.stop()

            raise Exit()

        status.stop()

    with Progress(console=console) as progress:

        task = progress.add_task(description=i18n.steps.yield_result, start=False, total=len(FETCHED_TRUSTLINE_BALANCES))

        for address, balance in FETCHED_TRUSTLINE_BALANCES.items():
            progress.update(task, description=t(i18n.steps.yield_result_account, address=address))

            resulting_yield = calculate_yield(balance)

            if isinstance(resulting_yield, type(None)):
                # @TODO(spunk-developer): More fancy error handling

                progress.remove_task(task)
                raise Exit()

            INDIVIDUAL_TRUSTILE_YIELD[address] = resulting_yield

            progress.advance(task)

        progress.remove_task(task)


def step_end_airdrop_calculations():
    """Prints total ratio into console while saving OR printing results as well.

    Raises:
        Exit: If CSV saving was chosen, being unable to save to chosen path.
    """

    global FETCHED_TRUSTLINE_BALANCES, INDIVIDUAL_TRUSTILE_YIELD, FETCHED_TARGET_TRUSTLINES, AIRDROP_START_TIME

    console.clear()

    yielding_metadata = get_yielding()
    ratio             = get_ratio()
    path              = get_csv()
    sum               = get_sum()

    token = yielding_metadata[0]
    name  = yielding_metadata[1]

    if isinstance(name, type(None)):
        name = token

    if isinstance(path, type(None)):

        table = Table(title=i18n.steps.print_header)

        table.add_column("Address", justify="left", style="#902EF4")
        table.add_column(name,      justify="left", style="#0098FF")
        table.add_column("Yield",   justify="left", style="#00CFFF")

        if sum >= 1:
            table.add_column("Split",   justify="left", style="#57F6F0")

        for address in FETCHED_TARGET_TRUSTLINES:

            if address not in FETCHED_TARGET_TRUSTLINES or address not in INDIVIDUAL_TRUSTILE_YIELD:
                continue

            balance = f'{ FETCHED_TRUSTLINE_BALANCES[address] }'
            result  = f'{ INDIVIDUAL_TRUSTILE_YIELD[address] }'

            if sum >= 1:
                split   = f'{ (INDIVIDUAL_TRUSTILE_YIELD[address] / sum) * 100 }'
                table.add_row(address, balance, result, split)

            else:
                table.add_row(address, balance, result)

        console.print(table)

    else:

        headers = [ "Address", f'{ name }', "Yield" ]
        data    = [ ]

        if sum >= 1:
            headers = [ "Address", f'{ name }', "Yield", "Split" ]

        for address in FETCHED_TARGET_TRUSTLINES:

            if address not in FETCHED_TARGET_TRUSTLINES or address not in INDIVIDUAL_TRUSTILE_YIELD:
                continue

            balance = FETCHED_TRUSTLINE_BALANCES[address]
            result  = INDIVIDUAL_TRUSTILE_YIELD[address]

            if sum >= 1:
                split   = ( result / sum ) * 100

                data.append(
                    {
                        "Address"  : address,
                        f'{ name }': balance,
                        "Yield"    : result,
                        "Split"    : f'{ split }%'
                    }
                )

            else:
                data.append(
                    {
                        "Address"  : address,
                        f'{ name }': balance,
                        "Yield"    : result
                    }
                )

        if not generate_csv(path, headers, data):
            console.print(t(i18n.steps.error_saving_csv, path=path))
            raise Exit()

    # @NOTE(spunk-developer): Redo this WHOLE THING

    results = Table(box=None, show_header=False, show_edge=False, padding=(1, 1))

    results.add_column(justify="left")
    results.add_column(justify="center")

    results.add_row(
        Text("Trustlines", "#902EF4"),
        Text(f'{ len(FETCHED_TARGET_TRUSTLINES) }', "#902EF4")
    )

    results.add_row(
        Text("Trustline sum", "#0098FF"),
        Text(f'{ sum }', "#0098FF")
    )

    results.add_row(
        Text("Airdrop ratio", "#00CFFF"),
        Text(f'{ ratio }', "#00CFFF")
    )

    results.add_row(
        Text("Total elapsed time", "#57F6F0"),
        Text(str(timedelta(seconds=int(time() - AIRDROP_START_TIME))), "#57F6F0")
    )

    console.print(Panel(results, padding=(1, 3), subtitle=i18n.steps.print_subtitle, subtitle_align="left", border_style="#1B6AFF"))
