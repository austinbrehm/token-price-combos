"""Main module to calculate token price combinations reaching a target portfolio value.

Can be run as a script with optional CLI arguments. If any argument is omitted,
interactive prompts are used instead.

Example (all args from command line):
    python src/main.py --first-symbol BTC --first-holdings 1 --second-symbol ETH --second-holdings 10 --target 50000

Example (interactive):
    python src/main.py
"""

import argparse
import sys
from typing import Optional

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
    symbol = input("📋 Enter the token symbol: ").upper()

    # Verify the symbol is in the CoinMarketCap ID map.
    while symbol not in id_map:
        print(
            colorama.Fore.RED
            + "❌ Error: "
            + colorama.Style.RESET_ALL
            + f"Token symbol '{symbol}' not found in CoinMarketCap ID map. "
        )
        symbol = input("📋 Enter the token symbol: ").upper()

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
    goal = input("📋 Enter the target portfolio value in USD: ")

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
            goal = input("📋 Enter the target portfolio value in USD: ")

    return goal


def generate_plot_bytes(
    first_symbol: str,
    first_holdings: float,
    second_symbol: str,
    second_holdings: float,
    target: int,
    env_dir: Optional[str] = None,
) -> bytes:
    """Generate the price-combos plot as PNG bytes (for web/Django).

    Args:
        first_symbol: First token symbol (e.g. BTC).
        first_holdings: First token quantity held.
        second_symbol: Second token symbol (e.g. ETH).
        second_holdings: Second token quantity held.
        target: Target portfolio value in USD.
        env_dir: Directory containing .env (for API key). If None, uses current directory.

    Returns:
        Tuple of (PNG image bytes, token_prices dict {symbol: price}).

    Raises:
        ValueError: On validation error (unknown symbol, same symbol, goal already met).
    """
    import os

    util = Utils()
    env_file = os.path.join(env_dir, ".env") if env_dir else None
    api = CoinMarketCapAPI(api_key=util.get_api_key(env_file))

    current_ids = api.get_id_map()
    id_map = {item["symbol"]: item["id"] for item in current_ids["data"]}

    first_symbol = first_symbol.strip().upper()
    second_symbol = second_symbol.strip().upper()

    if not first_symbol or not second_symbol:
        raise ValueError("Both token symbols are required.")
    if first_symbol not in id_map or second_symbol not in id_map:
        raise ValueError("One or both token symbols not found in CoinMarketCap ID map.")
    if first_symbol == second_symbol:
        raise ValueError("First and second token symbols must be different.")
    if first_holdings <= 0 or second_holdings <= 0 or target <= 0:
        raise ValueError("Holdings and target must be positive.")

    token_prices = {first_symbol: 0, second_symbol: 0}
    for token in token_prices:
        quotes = api.get_crypto_quotes(symbol=token)
        price = round(quotes["data"][token][0]["quote"]["USD"]["price"], 10)
        token_prices[token] = price

    current_value = (
        first_holdings * token_prices[first_symbol]
        + second_holdings * token_prices[second_symbol]
    )
    if current_value >= target:
        raise ValueError("Target portfolio value already met.")

    ratio = token_prices[first_symbol] / token_prices[second_symbol]
    first_prices = [token_prices[first_symbol]]
    second_prices = [token_prices[second_symbol]]
    for r in np.arange(ratio / 10, ratio, ratio / 10):
        future = solver.calculate_prices(
            target, first_holdings, second_holdings, r
        )
        first_prices.append(future[0])
        second_prices.append(future[1])

    title = (
        f"Token price combos to reach ${target:,} with "
        f"{first_holdings:,} {first_symbol} and "
        f"{second_holdings:,} {second_symbol}"
    )
    png_bytes = util.plot_to_buffer(
        first_prices,
        second_prices,
        title,
        f"Price of {first_symbol} ($)",
        f"Price of {second_symbol} ($)",
    )
    return png_bytes, token_prices


def parse_args():
    """Parse optional CLI arguments for non-interactive use (e.g. from Django)."""
    parser = argparse.ArgumentParser(
        description="Calculate token price combinations to reach a target portfolio value."
    )
    parser.add_argument("--first-symbol", type=str, help="First token symbol (e.g. BTC)")
    parser.add_argument("--first-holdings", type=float, help="First token quantity held")
    parser.add_argument("--second-symbol", type=str, help="Second token symbol (e.g. ETH)")
    parser.add_argument("--second-holdings", type=float, help="Second token quantity held")
    parser.add_argument("--target", type=int, help="Target portfolio value in USD")
    parser.add_argument(
        "--output",
        type=str,
        help="Write plot PNG to this path and exit (for web/Django).",
    )
    parser.add_argument(
        "--env-dir",
        type=str,
        default=None,
        help="Directory containing .env for API key (default: current directory).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    util = Utils()
    api = CoinMarketCapAPI(api_key=util.get_api_key())
    colorama.init(autoreset=True)

    # Get current token symbols and their corresponding CoinMarketCap IDs.
    current_ids = api.get_id_map()
    current_ids = {item["symbol"]: item["id"] for item in current_ids["data"]}

    args = parse_args()
    use_cli = all(
        [
            args.first_symbol,
            args.first_holdings is not None and args.first_holdings > 0,
            args.second_symbol,
            args.second_holdings is not None and args.second_holdings > 0,
            args.target is not None and args.target > 0,
        ]
    )

    if use_cli:
        FIRST_TOKEN = args.first_symbol.upper()
        FIRST_TOKEN_QUANTITY = args.first_holdings
        SECOND_TOKEN = args.second_symbol.upper()
        SECOND_TOKEN_QUANTITY = args.second_holdings
        GOAL = args.target
        if FIRST_TOKEN not in current_ids or SECOND_TOKEN not in current_ids:
            print(
                colorama.Fore.RED + "❌ Error: " + colorama.Style.RESET_ALL
                + "One or both token symbols not found in CoinMarketCap ID map.",
                file=sys.stderr,
            )
            sys.exit(1)
        if FIRST_TOKEN == SECOND_TOKEN:
            print(
                colorama.Fore.RED + "❌ Error: " + colorama.Style.RESET_ALL
                + "First and second token symbols must be different.",
                file=sys.stderr,
            )
            sys.exit(1)
        # Web/Django: write plot to file and exit (no terminal output).
        if args.output:
            png_bytes, _ = generate_plot_bytes(
                FIRST_TOKEN,
                FIRST_TOKEN_QUANTITY,
                SECOND_TOKEN,
                SECOND_TOKEN_QUANTITY,
                GOAL,
                env_dir=args.env_dir,
            )
            with open(args.output, "wb") as f:
                f.write(png_bytes)
            sys.exit(0)
    else:
        # Get token information from user input.
        print(colorama.Fore.BLUE + "FIRST TOKEN")
        FIRST_TOKEN, FIRST_TOKEN_QUANTITY = get_token_info(current_ids)
        print(colorama.Fore.BLUE + "\nSECOND TOKEN")
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

        # Get target portfolio value from user input.
        GOAL = get_goal()

    HOLDINGS = {FIRST_TOKEN: FIRST_TOKEN_QUANTITY, SECOND_TOKEN: SECOND_TOKEN_QUANTITY}

    # TODO: search by ID instead of symbol
    # Get current prices from CoinMarketCap API.
    token_prices = {FIRST_TOKEN: 0, SECOND_TOKEN: 0}
    for token in token_prices:
        quotes = api.get_crypto_quotes(symbol=token)
        price = round(quotes["data"][token][0]["quote"]["USD"]["price"], 10)
        token_prices[token] = price

    # Check if target portfolio value is already met.
    current_value = (
        HOLDINGS[FIRST_TOKEN] * token_prices[FIRST_TOKEN]
        + HOLDINGS[SECOND_TOKEN] * token_prices[SECOND_TOKEN]
    )
    if current_value >= GOAL:
        print(
            colorama.Fore.RED
            + "❌ Error: "
            + colorama.Style.RESET_ALL
            + "Target portfolio value already met."
        )
        if use_cli:
            sys.exit(1)
        while current_value >= GOAL:
            GOAL = get_goal()
            current_value = (
                HOLDINGS[FIRST_TOKEN] * token_prices[FIRST_TOKEN]
                + HOLDINGS[SECOND_TOKEN] * token_prices[SECOND_TOKEN]
            )

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
        GOAL, HOLDINGS[FIRST_TOKEN], HOLDINGS[SECOND_TOKEN], ratio
    )

    first_prices = [token_prices[FIRST_TOKEN]]
    second_prices = [token_prices[SECOND_TOKEN]]
    for ratio in np.arange(ratio / 10, ratio, ratio / 10):
        future_token_prices = solver.calculate_prices(
            GOAL, HOLDINGS[FIRST_TOKEN], HOLDINGS[SECOND_TOKEN], ratio
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
        f"Price of {FIRST_TOKEN} (USD)",
        f"Price of {SECOND_TOKEN} (USD)",
    )

    print(
        colorama.Fore.GREEN
        + "✅ Done! "
        + colorama.Style.RESET_ALL
        + "Plot saved to "
        + colorama.Fore.BLUE
        + f"{filename}"
    )
