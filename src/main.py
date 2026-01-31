"""Main module to calculate token price combinations reaching a target portfolio value.

This is meant to run as a script.
"""

import sys

import numpy as np

import solver
from utils import Utils
from cmc_api import CoinMarketCapAPI

if __name__ == "__main__":
    # Get current token prices using the CoinMarketCap API
    util = Utils()
    key = util.get_api_key()
    api = CoinMarketCapAPI(api_key=key)

    # TODO: add logic to check for valid token symbols
    # TODO: implement CLI to input parameters
    FIRST_TOKEN = "BTC"
    SECOND_TOKEN = "ETH"
    HOLDINGS = {FIRST_TOKEN: 0.1, SECOND_TOKEN: 3}  # token amounts held
    GOAL = 100_000  # in dollars

    tokens = {FIRST_TOKEN: 0, SECOND_TOKEN: 0}
    for token in tokens:
        quotes = api.get_crypto_quotes(symbol=token)
        price = round(quotes["data"][token][0]["quote"]["USD"]["price"], 10)
        tokens[token] = price

    if (
        HOLDINGS[FIRST_TOKEN] * tokens[FIRST_TOKEN]
        + HOLDINGS[SECOND_TOKEN] * tokens[SECOND_TOKEN]
        >= GOAL
    ):
        print("✅ Target portfolio value already met. Stopping execution.")
        sys.exit()

    print(
        f"Current Prices: {FIRST_TOKEN}: ${tokens[FIRST_TOKEN]:,}, "
        f"{SECOND_TOKEN}: ${tokens[SECOND_TOKEN]:,}"
    )
    current_ratio = tokens[FIRST_TOKEN] / tokens[SECOND_TOKEN]
    #print(f"Current Price Ratio: {current_ratio:,} {SECOND_TOKEN} per {FIRST_TOKEN}")
    token_prices = solver.calculate_prices(
        GOAL, HOLDINGS[SECOND_TOKEN], HOLDINGS[FIRST_TOKEN], current_ratio
    )
    #print(
    #    f"Prices Needed to Reach ${GOAL:,} at Current Ratio: "
    #    f"{FIRST_TOKEN} = ${token_prices[0]:,}, {SECOND_TOKEN} = ${token_prices[1]:}"
    #)

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

        #print(
        #    f"Price Ratio: {ratio:,}, {FIRST_TOKEN} = "
        #    f"${first_price:,}, {SECOND_TOKEN} = ${second_price:,}"
        #)

    # Plot the price combinations
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
