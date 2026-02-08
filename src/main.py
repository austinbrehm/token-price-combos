"""Main module to calculate token price combinations reaching a target portfolio value.

This is meant to run as a script.
"""

import sys

import numpy as np
import colorama

import solver
from utils import Utils
from cmc_api import CoinMarketCapAPI

if __name__ == "__main__":
    util = Utils()
    api = CoinMarketCapAPI(api_key=util.get_api_key())
    colorama.init(autoreset=True)

    # Define parameters.
    current_ids = api.get_id_map()
    current_ids = {item["symbol"]: item["id"] for item in current_ids["data"]}

    #with open ("token_id_map.json", "w", encoding="utf8") as f:
    #    f.write(json.dumps(current_ids, indent=4))

    # TODO: write function for this
    FIRST_TOKEN = input("📋 Enter the symbol for the first token: ").upper()
    while FIRST_TOKEN not in current_ids:
        print(
            colorama.Fore.RED + "❌ Error: "
            + colorama.Style.RESET_ALL
            + f"Token symbol '{FIRST_TOKEN}' not found in CoinMarketCap ID map. "
        )
        FIRST_TOKEN = input("📋 Enter the symbol for the first token: ").upper()
    HOLDINGS = {FIRST_TOKEN: 0, }  # token amounts held
    HOLDINGS[FIRST_TOKEN] = float(input(f"📋 Enter the amount of {FIRST_TOKEN} held: "))
    while HOLDINGS[FIRST_TOKEN] <= 0:
        print(
            colorama.Fore.RED + "❌ Error: "
            + colorama.Style.RESET_ALL
            + "Amount held must be a positive number."
        )
        HOLDINGS[FIRST_TOKEN] = float(input(f"📋 Enter the amount of {FIRST_TOKEN} held: "))

    SECOND_TOKEN = input("📋 Enter the symbol for the second token: ").upper()
    while SECOND_TOKEN == FIRST_TOKEN:
        print(
            colorama.Fore.RED + "❌ Error: "
            + colorama.Style.RESET_ALL
            + "Second token symbol must be different from the first token symbol."
        )
        SECOND_TOKEN = input("📋 Enter the symbol for the second token: ").upper()
    HOLDINGS[SECOND_TOKEN] = float(input(f"📋 Enter the amount of {SECOND_TOKEN} held: "))
    while HOLDINGS[SECOND_TOKEN] <= 0:
        print(
            colorama.Fore.RED + "❌ Error: "
            + colorama.Style.RESET_ALL
            + "Amount held must be a positive number."
        )
        HOLDINGS[SECOND_TOKEN] = float(input(f"📋 Enter the amount of {SECOND_TOKEN} held: "))
    GOAL = int(input("📋 Enter the target portfolio value in USD (e.g., 10000): "))

    # Get current prices from CoinMarketCap API.
    # TODO: search by ID instead of symbol
    tokens = {FIRST_TOKEN: 0, SECOND_TOKEN: 0}
    for token in tokens:
        quotes = api.get_crypto_quotes(symbol=token)
        price = round(quotes["data"][token][0]["quote"]["USD"]["price"], 10)
        tokens[token] = price

    print(
        colorama.Fore.GREEN + "\nCurrent Prices\n" + colorama.Style.RESET_ALL +
        f"💰 {FIRST_TOKEN}: ${tokens[FIRST_TOKEN]:,}\n"
        f"💰 {SECOND_TOKEN}: ${tokens[SECOND_TOKEN]:,}\n"
    )

    # Check if target portfolio value is already met.
    if (
        HOLDINGS[FIRST_TOKEN] * tokens[FIRST_TOKEN]
        + HOLDINGS[SECOND_TOKEN] * tokens[SECOND_TOKEN]
        >= GOAL
    ):
        print("⚠️ Target portfolio value already met. Stopping execution.")
        sys.exit()

    # Calculate required token prices to reach target portfolio value.
    current_ratio = tokens[FIRST_TOKEN] / tokens[SECOND_TOKEN]
    token_prices = solver.calculate_prices(
        GOAL, HOLDINGS[SECOND_TOKEN], HOLDINGS[FIRST_TOKEN], current_ratio
    )

    first_prices = [tokens[FIRST_TOKEN]]
    second_prices = [tokens[SECOND_TOKEN]]
    for ratio in np.arange(current_ratio / 10, current_ratio, current_ratio / 10):
        token_prices = solver.calculate_prices(
            GOAL, HOLDINGS[SECOND_TOKEN], HOLDINGS[FIRST_TOKEN], ratio
        )

        first_price = token_prices[0]
        first_prices.append(first_price)

        second_price = token_prices[1]
        second_prices.append(second_price)

    # Plot the price combinations.
    print("Plotting token price combinations...")

    util.plot(
        first_prices,
        second_prices,
        f"Token price combos to reach ${GOAL:,} with "
        f"{HOLDINGS[FIRST_TOKEN]:,} {FIRST_TOKEN} and "
        f"{HOLDINGS[SECOND_TOKEN]:,} {SECOND_TOKEN}",
        f"Future Price of {FIRST_TOKEN} ($)",
        f"Future Price of {SECOND_TOKEN} ($)",
    )

    print(
        colorama.Fore.GREEN + "✅ Done! "
        + colorama.Style.RESET_ALL
        + "Plot saved to 'images/price_combos.png'."
    )
