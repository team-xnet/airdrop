"""Operations, otherwise known as steps that the airdrop program has to take to complete it's task."""
"""Author: spunk-developer <xspunk.developer@gmail.com>"""

from rich.prompt import Prompt
from typer       import Exit

from airdrop.calc import update_budget
from airdrop      import console, i18n, t

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
