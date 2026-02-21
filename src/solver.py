"""Solve for token price combinations to reach a target portfolio value."""

import numpy as np


def calculate_prices(
    target: int, token_1: float, token_2: float, price_ratio: float
) -> np.ndarray:
    """
    Calculate the required prices for two token quantities to reach a target portfolio value.

    This function uses linear algebra to solve the system of equations.

    Args:
        target (int): Target portfolio value in dollars.
        token_1 (float): Amount of first token held.
        token_2 (float): Amount of second token held.
        price_ratio (float): Ratio of first token price to second token price.

    Returns:
        prices (np.array): Array containing the required price for both tokens.
    """
    a = np.array([[token_1, token_2], [-1, price_ratio]])
    b = np.array([target, 0])
    prices = np.linalg.solve(a, b)

    return prices
