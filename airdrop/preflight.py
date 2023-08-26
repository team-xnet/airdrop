"""Operations, otherwise known as steps that the airdrop program has to take to complete it's task."""
"""Author: spunk-developer <xspunk.developer@gmail.com>                                            """

from xrpl.core.addresscodec import XRPLAddressCodecException, decode_seed
from cache_to_disk          import delete_disk_caches_for_function, delete_old_disk_caches
from rich.prompt            import IntPrompt, Confirm, Prompt
from rich.text              import Text
from pathlib                import Path
from typing                 import Union
from typer                  import Exit
from os                     import path

from airdrop.cache import accept_terms_of_use, get_terms_of_use
from airdrop.calc  import set_airdrop_budget, get_budget
from airdrop.data  import set_data, set_meta, set_path, get_path
from airdrop.dist  import register_wallet, get_wallet
from airdrop.xrpl  import update_issuing_metadata, fetch_xrpl_metadata, update_yielding_token, get_yielding, get_issuer
from airdrop.util  import get_layout_with_renderable
from airdrop.csv   import set_output_path, is_path_valid, get_csv
from airdrop       import console, i18n, t

CSV_PATH:      Union[None, str]                 = None

XRPL_METADATA: dict[str, list[tuple[str, str]]] = { }

REQUIRED_PARAMS_MISSING                         = 0

REQUIRED_PARAMS_VISITED                         = 0


def preflight_calculate_remaining_steps(*args) -> None:
    """Calculates the steps required to complete preflight based on the arguments given.
    """

    global REQUIRED_PARAMS_MISSING

    for argument in args:
        if isinstance(argument, type(None)):
            REQUIRED_PARAMS_MISSING += 1


def preflight_check_cache() -> None:
    """Confirms with user if they want to use pre-existing cache or not.
    """

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


def preflight_fetch_metadata() -> None:
    """Firstly sets internal flags for required input variables, then fetches ALL token metadata from XRPLMeta.

    Args:
        issuing_address (str): CLI input issuing address.
        yielding_address (str): CLI input yelding address.
        budget (int): CLI input airdrop budget.
        csv (Path): CLI input CSV file output path.

    Raises:
        Exit: Whenever requests to XRPLMeta fail due to connection issues.
    """

    global XRPL_METADATA

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

    if isinstance(address, type(None)):

        REQUIRED_PARAMS_VISITED += 1

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

    token = None

    if isinstance(address, type(None)):

        REQUIRED_PARAMS_VISITED += 1

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

    # In the case that balance wasn't passed into the CLI as a parameter, we ask the user directly.
    if isinstance(input, type(None)):
        REQUIRED_PARAMS_VISITED += 1

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

    if isinstance(output_path, type(None)):

        REQUIRED_PARAMS_VISITED += 1

        if Confirm.ask(t(i18n.preflight.confirm_csv, step=REQUIRED_PARAMS_VISITED, maximum=REQUIRED_PARAMS_MISSING), default=True) is False:
            return

        choice = int(IntPrompt.ask(i18n.preflight.choose_path, choices=[ "1", "2", "3" ]))

        if choice == 1:
            output_path = path.expanduser(f'~{ path.sep }Desktop')

        elif choice == 2:
            output_path = path.expanduser(f'~{ path.sep }Documents')

        elif choice == 3:
            user_path = Prompt.ask(i18n.preflight.custom_path, default="", show_default=False)

            if type(user_path) is str and len(user_path) >= 1:
                output_path = user_path

    try:
        if output_path.startswith("~"):
            output_path = path.expanduser(output_path)

        output_path = path.abspath(path.normpath(output_path))

        # We kill the whole thing if the path can't be validated.
        if not is_path_valid(output_path):
            raise RuntimeError()

        set_output_path(output_path)

    except:
        console.print(t(i18n.preflight.error_empty_path, path=output_path))
        raise Exit()


def preflight_confirm_calculate() -> None:
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

    confirm = Confirm.ask(t(i18n.preflight.confirm_preflight_calculate, issuing=final_issuing, yielding=final_yielding, budget=final_budget, csv=csv), default=True)

    if confirm is not True:
        raise Exit()
    else:
        console.clear()


def preflight_confirm_distribte() -> None:
    """Prints all chosen distribution options into console.

    Raises:
        Exit: If user didn't accept the choices.
    """

    issuer, currency = get_issuer()
    wallet           = get_wallet()
    filepaths        = get_path()

    token_id, token_name = currency

    final_filepaths = f'{ path.abspath(path.normpath(filepaths)) }'
    final_wallet    = f'{ wallet.classic_address } ({ "*" * len(wallet.seed) })'
    final_token     = f'{ token_id } ({ issuer })'

    if not isinstance(token_name, type(None)):
        final_token = f'{ token_id } ({ token_name })'


    user_input = console.input(get_layout_with_renderable(Text(t(i18n.preflight.confirm_preflight_distribute, token=final_token, wallet=final_wallet, filepaths=final_filepaths))))

    while True:

        if len(user_input) == 0 or user_input.lower() == "yes" or user_input.lower() == "y":
            break

        if user_input.lower() == "no" or user_input.lower() == "n":

            raise Exit()

        user_input = console.input(i18n.rehydrate.metadata_error)

    console.clear()

def preflight_validate_seed(seed: Union[str, None]) -> None:
    """Validates the input seed address which'll be used for getting the cold wallet.

    Args:
        seed (Union[str, None]): The input seed, or none.

    Raises:
        Exit: If the wallet cannot be established for any reason.
    """

    global REQUIRED_PARAMS_VISITED, REQUIRED_PARAMS_MISSING

    if isinstance(seed, type(None)):

        REQUIRED_PARAMS_VISITED += 1

        user_input = console.input(t(i18n.preflight.enter_seed, step=REQUIRED_PARAMS_VISITED, maximum=REQUIRED_PARAMS_MISSING))

        while True:
            if type(user_input) is str and len(user_input) >= 1:
                try:
                    decode_seed(user_input)

                    seed = user_input

                    break

                except XRPLAddressCodecException:
                    pass

                except ValueError:
                    pass

            user_input = console.input(t(i18n.preflight.enter_seed_invalid, seed=user_input))

        console.clear()

    try:
        decode_seed(seed)

        if not register_wallet(seed):

            raise XRPLAddressCodecException()

    except:
        console.print(t(i18n.preflight.error_seed, seed=seed))
        raise Exit()

def preflight_validate_data_path(input_path: Union[Path, None]) -> None:
    """Validates and sets the required datafile paths.

    Args:
        input_path (Union[Path, None]): The actual path itself.

    Raises:
        Exit: If either the meta or data file(s) don't exist.
    """

    global REQUIRED_PARAMS_VISITED, REQUIRED_PARAMS_MISSING

    if isinstance(input_path, type(None)):

        REQUIRED_PARAMS_VISITED += 1

        choice = int(IntPrompt.ask(t(i18n.preflight.choose_data, step=REQUIRED_PARAMS_VISITED, maximum=REQUIRED_PARAMS_MISSING), choices=[ "1", "2", "3" ]))

        if choice == 1:
            input_path = path.expanduser(f'~{ path.sep }Desktop')

        elif choice == 2:
            input_path = path.expanduser(f'~{ path.sep }Documents')

        elif choice == 3:
            while True:
                user_path = console.input(i18n.preflight.enter_data)

                if type(user_path) is str and len(user_path) >= 1:

                    if user_path.startswith('~'):
                        user_path = path.expanduser(user_path)

                    input_path = path.abspath(path.normpath(user_path))

                    break

                input_path = console.input(t(i18n.preflight.error_data_invalid, datapath=user_path))


    meta = Path(input_path, "airdrop_metadata.txt")
    data = Path(input_path, "airdrop_data.csv")

    if not set_meta(meta):
        console.print(t(i18n.preflight.error_filepaths, filetype="airdrop_metadata.txt", filepath=meta.absolute()))
        raise Exit()

    if not set_data(data):
        console.print(t(i18n.preflight.error_filepaths, filetype="airdrop_data.csv", filepath=data.absolute()))
        raise Exit()

    if not set_path(input_path):
        console.print(t(i18n.preflight.error_filepaths, filetype="", filepath=input_path.absolute()))
        raise Exit()

    console.clear()
