"""Operations, otherwise known as steps that the airdrop program has to take to complete it's task."""
"""Author: spunk-developer <xspunk.developer@gmail.com>"""

from rich.prompt import Prompt
from rich.panel  import Panel
from rich.text   import Text
from typer       import Exit

from rich.align import Align

from airdrop.calc import update_budget
from airdrop      import console, i18n, t

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

        console.print(Panel(Align(rendered_banner, "center"), subtitle=i18n.preflight.banner_subtitle, subtitle_align="left", border_style="#1b6aff"))

    # If an error happened for *any* reason, we can safely assume the console environment is completely fucked and unusable.
    except:
        raise Exit()

def preflight_validate_supply_balance(input) -> None:
    """Validates any arbitrary `input` value to see if it is a number that is greater than 0.

    Args:
        input (Any): Arbitrary input object which gets validated as a number and cast to a float.

    Raises:
        RuntimeError: If `input` value cannot be converted into a number, is not within range of `0` to `100000000000000000` or if the budget variable has already been defined.
    """

    # In the case that balance wasn't passed into the CLI as a parameter, we ask the user directly.
    input = Prompt.ask(i18n.preflight.enter_balance, default=0)

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
