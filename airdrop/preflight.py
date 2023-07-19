"""Operations, otherwise known as steps that the airdrop program has to take to complete it's task."""
"""Author: spunk-developer <xspunk.developer@gmail.com>"""

from rich.console import Group
from rich.prompt  import Prompt
from rich.align   import Align
from rich.panel   import Panel
from rich.text    import Text
from requests     import get
from typer        import Exit

from airdrop.calc import update_budget
from airdrop      import console, i18n, t

REQUIRED_PARAMS_MISSING = 0

REQUIRED_PARAMS_VISITED = 0

XRPL_METADATA: dict[str, list[tuple[str, str]]] = { }

def preflight_print_banner() -> None:
    """Generates and prints the Airdrop application banner.

    Raises:
        Exit: If for some reason the banner generation fails, or console environment is messed up.
    """

    try:
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

        # My god, this render statement gives me PTSD.
        console.print(Panel(Group(Align(rendered_banner, "center"), Align(Text.assemble(i18n.preflight.banner_description, i18n.preflight.banner_note, i18n.preflight.banner_disclaimer), "left")), subtitle=i18n.preflight.banner_subtitle, subtitle_align="left", border_style="#1B6AFF"), "\n")

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

    global REQUIRED_PARAMS_MISSING

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

            global XRPL_METADATA
            status.start()

            iter_step  = 100
            iterations = 0

            response = get("https://s1.xrplmeta.org/tokens", params={ "limit": iter_step, "trust_level": [ 1, 2, 3 ] }).json()

            while True:

                for token in response["tokens"]:

                    metadata = token["meta"]["token"]
                    issuer   = token["issuer"]

                    if token["issuer"] not in XRPL_METADATA:
                        XRPL_METADATA[issuer] = [ ]

                    id   = token["currency"]
                    name = None

                    if "name" in metadata:
                        name = metadata["name"]

                    XRPL_METADATA[issuer].append((id, name))

                if response["count"] <= iterations:
                    break

                response = get("https://s1.xrplmeta.org/tokens", params={ "limit": iter_step, "trust_level": [ 1, 2, 3 ], "offset": iterations }).json()
                iterations += iter_step

            status.stop()

    except:
        console.print(i18n.preflight.error_fetch_failed)
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

    if not update_budget(validated_input):
        console.print(i18n.preflight.error_overwrite)
        raise Exit()
