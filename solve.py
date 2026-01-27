"""Solve for token price combinations to reach a target portfolio value."""

import numpy as np
import matplotlib.pyplot as plt


def calculate_prices(
    target: int, token_1: float, token_2: float, price_ratio: float
) -> np.ndarray:
    """
    Calculate the required prices for two token quantities to reach a target portfolio value.

    Args:
        target (int): Target portfolio value in dollars.
        token_1 (float): Amount of first token held.
        token_2 (float): Amount of second token held.
        price_ratio (float): Ratio of first token price to second token price.

    Returns:
        prices (np.array): Array containing the required price for both tokens.
    """
    a = np.array([[token_2, token_1], [-1, price_ratio]])
    b = np.array([target, 0])
    prices = np.linalg.solve(a, b)

    return prices


def plot(
    x: list,
    y: list,
    target: int,
    token_1: float,
    token_1_ticker: str,
    token_2: float,
    token_2_ticker: str,
):
    """
    Plot the price combinations for two tokens to reach a target portfolio value.

    Args:
        x (list): Array of prices for the first token.
        y (list): Array of prices for the second token.
        target (int): Target portfolio value in dollars.
        token_1 (float): Amount of first token held.
        token_1_ticker (str): Ticker symbol for the first token.
        token_2 (float): Amount of second token held.
        token_2_ticker (str): Ticker symbol for the second token.
    """
    plt.style.use("dark_background")
    plt.scatter(x, y, marker="o", c="lime")
    plt.title(
        f"Path to ${target:,}: {token_1} {token_1_ticker}, {token_2} {token_2_ticker}"
    )
    plt.xlabel(f"{token_1_ticker} Price ($)")
    plt.ylabel(f"{token_2_ticker} Price ($)")
    plt.show()


if __name__ == "__main__":
    # TODO: implement CLI to input parameters
    GOAL = 100_000
    ETH = 3
    BTC = 0.05

    eth_prices = []
    btc_prices = []
    for ratio in range(1, 101, 10):
        token_prices = calculate_prices(GOAL, ETH, BTC, ratio).round()
        btc_price = f"{int(token_prices[0]):,}"
        eth_price = f"{int(token_prices[1]):,}"
        eth_prices.append(eth_price)
        btc_prices.append(btc_price)

    plot(eth_prices, btc_prices, GOAL, ETH, "ETH", BTC, "BTC")
