"""Main module to calculate token price combinations reaching a target portfolio value.

This is meant to run as a script.
"""

import sys

import solver
from utils import Utils
from cmc_api import CoinMarketCapAPI

if __name__ == "__main__":
    # Get current token prices using the CoinMarketCap API
    util = Utils()
    key = util.get_api_key()
    api = CoinMarketCapAPI(api_key=key)

    # TODO: add logic to check for valid token symbols
    tokens = {"BTC": 0, "ETH": 0}
    for token in tokens:
        quotes = api.get_crypto_quotes(symbol=token)
        price = round(quotes["data"][token][0]["quote"]["USD"]["price"], 2)
        tokens[token] = price

    # TODO: implement CLI to input parameters
    GOAL = 100_000  # in dollars
    BTC = 0.1  # amount of BTC
    ETH = 3  # amount of ETH

    if BTC * tokens["BTC"] + ETH * tokens["ETH"] >= GOAL:
        print("Target portfolio value already met.")
        sys.exit()

    btc_prices = [tokens["BTC"]]
    eth_prices = [tokens["ETH"]]
    for ratio in range(1, 101, 10):
        token_prices = solver.calculate_prices(GOAL, ETH, BTC, ratio).round()
        btc_price = round(token_prices[0], 2)
        eth_price = round(token_prices[1], 2)
        btc_prices.append(btc_price)
        eth_prices.append(eth_price)

    # Plot the price combinations
    util.plot(
        btc_prices,
        eth_prices,
        f"Token price combos to reach ${GOAL:,} with {BTC} BTC and {ETH} ETH",
        "Future Price of BTC ($)",
        "Future Price of ETH ($)",
    )
