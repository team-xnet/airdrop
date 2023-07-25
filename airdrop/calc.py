"""Calculation functions.                              """
"""Author: spunk-developer <xspunk.developer@gmail.com>"""

from typing import Union

AIRDROP_TOTAL_BUDGET: Union[None, float] = None

AIRDROP_RATIO:        Union[None, float] = None

AIRDROP_TOTAL_SUM:    float              = 0.0

def get_budget() -> Union[None, float]:
    """Returns the current airdrop budget state.

    Returns:
        Union[None, float]: The airdrop budget.
    """

    global AIRDROP_TOTAL_BUDGET
    return AIRDROP_TOTAL_BUDGET


def get_ratio() -> Union[None, str]:
    """Returns the current airdrop ratio.

    Returns:
        Union[None, str]: The ratio, which is the budget divided by ratio.
    """


def get_sum() -> float:
    """Returns the current airdrop total sum state.

    Returns:
        float: The total sum of all trustline balances.
    """

    global AIRDROP_TOTAL_SUM
    return AIRDROP_TOTAL_SUM


def set_airdrop_budget(amount: Union[float, int]) -> bool:
    """Sets the total airdrop budget to given `amount`.

    Args:
        amount (float): The amount that the budget should be. Preferably represented as a float.

    Returns:
        bool: _description_
    """

    global AIRDROP_TOTAL_BUDGET

    if isinstance(amount, type(int)):
        amount = float(amount)

    if isinstance(AIRDROP_TOTAL_BUDGET, type(None)):
        AIRDROP_TOTAL_BUDGET = amount

        return True

    return False


def increment_airdrop_sum(amount: Union[float, list[float]]) -> None:
    """Increments the total airdrop sum, which is the total sum of all airdrop balances.

    Args:
        amount (Union[float, list[float]]): The amount which to increment with.
    """

    global AIRDROP_TOTAL_SUM

    try:
        for balance in amount:
            AIRDROP_TOTAL_SUM += balance

    except TypeError:
        AIRDROP_TOTAL_SUM += amount


def calculate_airdrop_ratio() -> bool:
    """Calculates the total airdrop ratio if the prequisites are set.

    Returns:
        bool: Returns `True` if all prequisites are present, returns `False` otherwise.
    """

    global AIRDROP_TOTAL_BUDGET, AIRDROP_TOTAL_SUM, AIRDROP_RATIO

    if isinstance(AIRDROP_TOTAL_BUDGET, type(None)) or AIRDROP_TOTAL_SUM == 0.0:
        return False

    AIRDROP_RATIO = AIRDROP_TOTAL_BUDGET / AIRDROP_TOTAL_SUM

    return True


def calculate_yield(balance: float) -> Union[float, None]:
    """Calculates the yield for any given anonymous balance.

    Args:
        balance (float): The balance which to multiply.

    Returns:
        Union[float, None]: `None` if the ratio hasn't been set, otherwise correct yield.
    """

    global AIRDROP_RATIO

    if isinstance(AIRDROP_RATIO, type(None)):
        return None

    return balance * AIRDROP_RATIO
