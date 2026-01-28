# Token Price Combinations
Generate and plot price combinations for two cryptocurrency tokens to reach a target portfolio value
with specific token quantities.

![Output](images/plot.png)

Built with Python, CoinMarketCap API, and linear algebra.

## Setup
### CoinMarketCap
1. Create a [CoinMarketCap](https://pro.coinmarketcap.com/) account
1. Login and retrieve API key

### GitBash
1. Open Git Bash, then run the following command: `code ~/.bashrc`
1. In the bashrc file, type the following: `export COINMARKETCAP_KEY="<API key from CoinMarketCap>"`
1. Save the bashrc file

## Usage
Run the main.py script from root directory: `python3 src/main.py`