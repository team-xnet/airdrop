"""Operations, otherwise known as steps that the airdrop program has to take to complete it's task."""
"""Author: spunk-developer <xspunk.developer@gmail.com>                                            """

from cache_to_disk import delete_disk_caches_for_function, delete_old_disk_caches
from rich.prompt   import IntPrompt, Confirm, Prompt
from rich.layout   import Layout
from rich.align    import Align
from rich.panel    import Panel
from rich.text     import Text
from typing        import Union
from typer         import Exit
from os            import path

from airdrop.cache import accept_terms_of_use, get_terms_of_use
from airdrop.calc  import set_airdrop_budget, get_budget
from airdrop.xrpl  import update_issuing_metadata, fetch_xrpl_metadata, update_yielding_token, get_yielding, get_issuer
from airdrop.csv   import set_output_path, is_path_valid, get_csv
from airdrop       import console, i18n, t

CSV_PATH:      Union[None, str]                 = None

XRPL_METADATA: dict[str, list[tuple[str, str]]] = { }

REQUIRED_PARAMS_MISSING                         = 0

REQUIRED_PARAMS_VISITED                         = 0

def get_layout_with_renderable(renderable) -> Layout:

    rendered_banner = Text.assemble(
        ("__   ___   _ ______ _______            _         _                 \n", "#902EF4"),
        ("\ \ / / \ | |  ____|__   __|     /\   (_)       | |                \n", "#1B6AFF"),
        (" \ V /|  \| | |__     | |       /  \   _ _ __ __| |_ __ ___  _ __  \n", "#008EFF"),
        ("  > < | . ` |  __|    | |      / /\ \ | | '__/ _` | '__/ _ \| '_ \ \n", "#00AAFF"),
        (" / . \| |\  | |____   | |     / ____ \| | | | (_| | | | (_) | |_) |\n", "#00ACFF"),
        ("/_/ \_\_| \_|______|  |_|    /_/    \_\_|_|  \__,_|_|  \___/| .__/ \n", "#00D5FF"),
        ("                                                            | |    \n", "#00E7FD"),
        ("                                                            |_|    \n", "#57F6F0"),

        overflow="crop",
        no_wrap=True
    )

    layout = Layout()

    layout.split_column(
        Layout(Align(Panel(rendered_banner, expand=False, subtitle=i18n.preflight.banner_subtitle, subtitle_align="left", border_style="#1B6AFF", padding=(0, 5)), "center", vertical="middle"), name="top"),
        Layout(Align(renderable, vertical="bottom"), name="bottom")
    )

    return layout


def preflight_check_cache() -> None:
    """Confirms with user if they want to use pre-existing cache or not."""
    delete_old_disk_caches()

    if not isinstance(fetch_xrpl_metadata.cache_size(), type(None)):

        user_input = console.input(i18n.rehydrate.metadata_cache)

        while True:

            if len(user_input) == 0 or user_input.lower() == "yes" or user_input.lower() == "y":
                break

            if user_input.lower() == "no" or user_input.lower() == "n":

                delete_disk_caches_for_function("fetch_xrpl_metadata")
                break

            user_input = console.input(i18n.rehydrate.metadata_error)

        console.clear()


def preflight_print_banner() -> None:
    """Generates and prints the Airdrop application banner.

    Raises:
        Exit: If for some reason the banner generation fails, or console environment is messed up.
    """

    try:

        if not get_terms_of_use():
            console.print(get_layout_with_renderable(Text.assemble(i18n.preflight.banner_description, i18n.preflight.banner_note, i18n.preflight.banner_disclaimer)))

            user_input = console.input(i18n.preflight.terms_message)

            while True:

                if user_input == "N" or user_input.lower() == "no":
                    raise Exit()

                if user_input == "Y" or user_input.lower() == "yes":
                    accept_terms_of_use()
                    break

                user_input = console.input(i18n.preflight.terms_error)

            console.clear()

        console.print(get_layout_with_renderable(""))

    # If an error happened for *any* reason, we can safely assume the console environment is completely fucked and unusable.
    except:
        raise Exit()


def preflight_fetch_metadata(issuing_address, yielding_address, budget, csv) -> None:
    """Firstly sets internal flags for required input variables, then fetches ALL token metadata from XRPLMeta.

    Args:
        issuing_address (str): CLI input issuing address.
        yielding_address (str): CLI input yelding address.
        budget (int): CLI input airdrop budget.
        csv (Path): CLI input CSV file output path.

    Raises:
        Exit: Whenever requests to XRPLMeta fail due to connection issues.
    """

    global REQUIRED_PARAMS_MISSING, XRPL_METADATA

    if isinstance(issuing_address, type(None)):
        REQUIRED_PARAMS_MISSING += 1

    if isinstance(yielding_address, type(None)):
        REQUIRED_PARAMS_MISSING += 1

    if isinstance(budget, type(None)):
        REQUIRED_PARAMS_MISSING += 1

    if isinstance(csv, type(None)):
        REQUIRED_PARAMS_MISSING += 1

    try:
        with console.status(i18n.preflight.metadata_fetch, spinner="dots") as status:

            status.start()

            try:
                XRPL_METADATA = fetch_xrpl_metadata()
            except Exception as e:
                console.print(e)

            status.stop()

    except:
        console.print(i18n.preflight.error_fetch_failed)
        raise Exit()


def preflight_validate_issuing_address(address) -> None:
    """Validates & sets the source issuing address, allowing the user to pick which issued token they wish to use.

    Args:
        address (str): The source issuing address.

    Raises:
        Exit: Either due to an invalid source address, or whenever attempting to override a pre-existing source address.
    """

    global REQUIRED_PARAMS_MISSING, REQUIRED_PARAMS_VISITED, XRPL_METADATA

    REQUIRED_PARAMS_VISITED += 1

    if isinstance(address, type(None)):

        user_input = console.input(t(i18n.preflight.enter_issuer, address=address, step=REQUIRED_PARAMS_VISITED, maximum=REQUIRED_PARAMS_MISSING))

        while True:

            if user_input in XRPL_METADATA:
                break

            user_input = console.input(t(i18n.preflight.error_issuer_invalid, address=user_input))

        address = user_input
        console.clear()

    elif address not in XRPL_METADATA:
        console.print(t(i18n.preflight.error_issuer_missing, address=address))
        raise Exit()

    issued_tokens_len = len(XRPL_METADATA[address])
    target_token_id   = None

    if issued_tokens_len >= 2:

        choice_list = ""
        choice_idx  = [ ]
        choices     = [ ]
        idx         = 0

        for id, name in XRPL_METADATA[address]:

            newline = "\n"
            idx += 1

            choice_idx.append(f'{ idx }')
            choices.append(id)

            if idx == len(XRPL_METADATA[address]):
                newline = ""

            if type(name) is str:
                choice_list += f"{ idx }: { name }{ newline }"
                continue

            choice_list += f"{ idx }: { id }{ newline }"

        chosen_idx = IntPrompt.ask(t(i18n.preflight.choose_token, address=address, tokens=choice_list, total=issued_tokens_len), choices=choice_idx)
        target_token_id = choices[chosen_idx - 1]

    else:
        target_token_id = XRPL_METADATA[address][0]

    if not update_issuing_metadata(address, target_token_id):
        console.print(t(i18n.preflight.error_issuer_overwrite, address=address))
        raise Exit()


def preflight_validate_yielding_address(address) -> None:
    """Validates the "yield" address for the airdrop. Optionally allows user to specify the yield address as XRP.

    Args:
        address (str): Actual address, or just "XRP".

    Raises:
        Exit: If yielding address doesn't exist, or target token has already been set.
    """

    global REQUIRED_PARAMS_MISSING, REQUIRED_PARAMS_VISITED

    REQUIRED_PARAMS_VISITED += 1

    token = None

    if isinstance(address, type(None)):

        user_input = console.input(t(i18n.preflight.enter_yielding, step=REQUIRED_PARAMS_VISITED, maximum=REQUIRED_PARAMS_MISSING))

        while True:

            if user_input.lower() == "xrp":
                token = ("XRP", None)
                break

            if user_input in XRPL_METADATA:
                break

            user_input = console.input(t(i18n.preflight.error_issuer_invalid, address=address))

        address = user_input
        console.clear()

    else:
        if address not in XRPL_METADATA:

            if type(address) is str and address.lower() == "xrp":
                token = ("XRP", None)

            else:
                console.print(t(i18n.preflight.error_yielding_missing, address=address))
                raise Exit()

    if address.lower() != "xrp":
        issued_tokens = XRPL_METADATA[address]

        issued_tokens_len = len(issued_tokens)

        if issued_tokens_len >= 2:

            choice_list = ""
            choice_idx  = [ ]
            choices     = [ ]
            idx         = 0

            for id, name in XRPL_METADATA[address]:

                newline = "\n"
                idx    += 1

                choice_idx.append(f'{ idx }')
                choices.append((id, name))

                if idx == len(XRPL_METADATA[address]):
                    newline = ""

                if type(name) is str:
                    choice_list += f"{ idx }: { name }{ newline }"
                    continue

                choice_list += f"{ idx }: { id }{ newline }"

            chosen_idx = IntPrompt.ask(t(i18n.preflight.choose_token, address=str(address), tokens=choice_list, total=issued_tokens_len), choices=choice_idx)
            token      = choices[chosen_idx - 1]

        else:
            token = XRPL_METADATA[address][0]

    if not update_yielding_token(token[0], token[1]):
        console.print(t(i18n.preflight.error_yielding_overwrite, address=address))
        raise Exit()


def preflight_validate_supply_balance(input) -> None:
    """Validates any arbitrary `input` value to see if it is a number that is greater than 0.

    Args:
        input (Any): Arbitrary input object which gets validated as a number and cast to a float.

    Raises:
        RuntimeError: If `input` value cannot be converted into a number, is not within range of `0` to `100000000000000000` or if the budget variable has already been defined.
    """
    global REQUIRED_PARAMS_MISSING, REQUIRED_PARAMS_VISITED

    REQUIRED_PARAMS_VISITED += 1

    # In the case that balance wasn't passed into the CLI as a parameter, we ask the user directly.
    if isinstance(input, type(None)):
        input = Prompt.ask(t(i18n.preflight.enter_balance, step=REQUIRED_PARAMS_VISITED, maximum=REQUIRED_PARAMS_MISSING), default=0)

    # We parse the actual input into a float or an int. If this fails, the error is raised to the caller.
    try:
        if type(input) is not (float | int):
            validated_input = float(input)
    except:
        console.print(t(i18n.preflight.error_conversion, value=input))
        raise Exit()

    # XRP minimum and maximum number enforcement.
    if validated_input <= 0:
        console.print(t(i18n.preflight.error_minimum, value=input))
        raise Exit()
    elif validated_input > 100000000000000000:
        console.print(t(i18n.preflight.error_maximum, value=input))
        raise Exit()

    if not set_airdrop_budget(validated_input):
        console.print(i18n.preflight.error_overwrite)
        raise Exit()


def preflight_validate_output(output_path) -> None:
    """Validates the CSV output if it exists,

    Args:
        output_path (Union[str, None]): The path where to save the CSV file. May end with the CSV filename.

    Raises:
        Exit: If the path is invalid, or inaccessible for whatever reason.
    """

    global REQUIRED_PARAMS_MISSING, REQUIRED_PARAMS_VISITED

    REQUIRED_PARAMS_VISITED += 1

    if isinstance(output_path, type(None)):

        if Confirm.ask(t(i18n.preflight.confirm_csv, step=REQUIRED_PARAMS_VISITED, maximum=REQUIRED_PARAMS_MISSING), default=True) is False:
            return

        choice = int(IntPrompt.ask(i18n.preflight.choose_path, choices=[ "1", "2", "3" ]))

        if choice == 1:
            output_path = path.expanduser("~/Desktop")

        elif choice == 2:
            output_path = path.expanduser("~/Documents")

        elif choice == 3:
            user_path = Prompt.ask(i18n.preflight.custom_path, default="", show_default=False)

            if type(user_path) is str and len(user_path) >= 1:
                output_path = user_path

    try:
        if output_path.startswith("~"):
            output_path = path.expanduser(output_path)

        output_path = path.normpath(path.abspath(output_path))

        # We kill the whole thing if the path can't be validated.
        if not is_path_valid(output_path):
            raise RuntimeError()

    except:
        console.print(t(i18n.preflight.error_empty_path, path=output_path))
        raise Exit()

    if output_path.endswith(path.sep):
        set_output_path(f'{ output_path }airdrop.csv')
        return

    else:
        if output_path.endswith(".csv"):
            set_output_path(output_path)
            return

        set_output_path(f'{ output_path }/airdrop.csv')


def preflight_confirm():
    """Prints all the chosen options into terminal, allowing the user to double check their inputs being right.

    Raises:
        Exit: If the user exits.
    """

    yielding = get_yielding()
    issuing  = get_issuer()
    budget   = get_budget()
    csv      = get_csv()

    final_yielding = None
    final_issuing  = None
    final_budget   = None

    if not isinstance(issuing, type(None)):
        token = issuing[1]

        if type(token[1]) is str:
            final_issuing = f'{ token[0] } ({ token[1] })'

        else:
            final_issuing = token[0]

    if not isinstance(yielding, type(None)):

        if type(yielding[1]) is str:
            final_yielding = f'{ yielding[0] } ({ yielding[1] })'

        else:
            final_yielding = yielding[0]

    final_budget = f'{ budget }'

    confirm = Confirm.ask(t(i18n.preflight.confirm_preflight, issuing=final_issuing, yielding=final_yielding, budget=final_budget, csv=csv), default=True)

    if confirm is not True:
        raise Exit()
    else:
        console.clear()
