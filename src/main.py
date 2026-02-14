"""Main module to calculate token price combinations reaching a target portfolio value.

This is meant to run as a script.
"""

import numpy as np
import colorama

import solver
from utils import Utils
from cmc_api import CoinMarketCapAPI


def get_token_info(id_map: dict) -> tuple[str, float]:
    """Get token symbol and quantity from user input.

    Args:
        id_map (dict): Dictionary mapping token symbols to CoinMarketCap IDs.
    """
    symbol = input("📋 Enter the symbol for the first token: ").upper()

    # Verify the symbol is in the CoinMarketCap ID map.
    while symbol not in id_map:
        print(
            colorama.Fore.RED
            + "❌ Error: "
            + colorama.Style.RESET_ALL
            + f"Token symbol '{symbol}' not found in CoinMarketCap ID map. "
        )
        symbol = input("📋 Enter the symbol for the first token: ").upper()

    quantity = input(f"📋 Enter the amount of {symbol} held: ")

    # Verify the quantity is a positive number.
    while True:
        try:
            quantity = float(quantity)
            if quantity <= 0:
                raise ValueError
            break
        except ValueError:
            print(
                colorama.Fore.RED
                + "❌ Error: "
                + colorama.Style.RESET_ALL
                + "Amount held must be a positive number."
            )
            quantity = input(f"📋 Enter the amount of {symbol} held: ")

    return symbol, quantity


def get_goal() -> int:
    """Get target portfolio value from user input."""
    goal = input("📋 Enter the target portfolio value in USD (e.g., 10000): ")

    # Verify the goal is a positive integer.
    while True:
        try:
            goal = int(goal)
            if goal <= 0:
                raise ValueError
            break
        except ValueError:
            print(
                colorama.Fore.RED
                + "❌ Error: "
                + colorama.Style.RESET_ALL
                + "Target portfolio value must be a positive integer."
            )
            goal = input("📋 Enter the target portfolio value in USD (e.g., 10000): ")

    return goal


if __name__ == "__main__":
    util = Utils()
    api = CoinMarketCapAPI(api_key=util.get_api_key())
    colorama.init(autoreset=True)

    # Get current token symbols and their corresponding CoinMarketCap IDs.
    current_ids = api.get_id_map()
    current_ids = {item["symbol"]: item["id"] for item in current_ids["data"]}

    # Get token information from user input.
    FIRST_TOKEN, FIRST_TOKEN_QUANTITY = get_token_info(current_ids)
    SECOND_TOKEN, SECOND_TOKEN_QUANTITY = get_token_info(current_ids)

    # Verify the two token symbols are different.
    while SECOND_TOKEN == FIRST_TOKEN:
        print(
            colorama.Fore.RED
            + "❌ Error: "
            + colorama.Style.RESET_ALL
            + "Second token symbol must be different from the first token symbol."
        )
        SECOND_TOKEN, SECOND_TOKEN_QUANTITY = get_token_info(current_ids)

    HOLDINGS = {FIRST_TOKEN: FIRST_TOKEN_QUANTITY, SECOND_TOKEN: SECOND_TOKEN_QUANTITY}

    # Get target portfolio value from user input.
    GOAL = get_goal()

    # TODO: search by ID instead of symbol
    # Get current prices from CoinMarketCap API.
    token_prices = {FIRST_TOKEN: 0, SECOND_TOKEN: 0}
    for token in token_prices:
        quotes = api.get_crypto_quotes(symbol=token)
        price = round(quotes["data"][token][0]["quote"]["USD"]["price"], 10)
        token_prices[token] = price

    # Check if target portfolio value is already met.
    while (
        HOLDINGS[FIRST_TOKEN] * token_prices[FIRST_TOKEN]
        + HOLDINGS[SECOND_TOKEN] * token_prices[SECOND_TOKEN]
        >= GOAL
    ):
        print(
            colorama.Fore.RED
            + "❌ Error: "
            + colorama.Style.RESET_ALL
            + "Target portfolio value already met."
        )
        GOAL = get_goal()

    # Print current token prices.
    print(
        colorama.Fore.GREEN
        + "\nCurrent Prices\n"
        + colorama.Style.RESET_ALL
        + f"💰 {FIRST_TOKEN}: ${token_prices[FIRST_TOKEN]:,}\n"
        f"💰 {SECOND_TOKEN}: ${token_prices[SECOND_TOKEN]:,}\n"
    )

    # Calculate required token prices to reach target portfolio value.
    ratio = token_prices[FIRST_TOKEN] / token_prices[SECOND_TOKEN]
    future_token_prices = solver.calculate_prices(
        GOAL, HOLDINGS[SECOND_TOKEN], HOLDINGS[FIRST_TOKEN], ratio
    )

    first_prices = [token_prices[FIRST_TOKEN]]
    second_prices = [token_prices[SECOND_TOKEN]]
    for ratio in np.arange(ratio / 10, ratio, ratio / 10):
        future_token_prices = solver.calculate_prices(
            GOAL, HOLDINGS[SECOND_TOKEN], HOLDINGS[FIRST_TOKEN], ratio
        )

        first_price = future_token_prices[0]
        first_prices.append(first_price)

        second_price = future_token_prices[1]
        second_prices.append(second_price)

    # Plot the price combinations.
    print("Plotting token price combinations...")

    filename = util.plot(
        first_prices,
        second_prices,
        f"Token price combos to reach ${GOAL:,} with "
        f"{HOLDINGS[FIRST_TOKEN]:,} {FIRST_TOKEN} and "
        f"{HOLDINGS[SECOND_TOKEN]:,} {SECOND_TOKEN}",
        f"Future Price of {FIRST_TOKEN} ($)",
        f"Future Price of {SECOND_TOKEN} ($)",
    )

    print(
        colorama.Fore.GREEN
        + "✅ Done! "
        + colorama.Style.RESET_ALL
        + "Plot saved to "
        + colorama.Fore.BLUE
        + f"{filename}"
    )
