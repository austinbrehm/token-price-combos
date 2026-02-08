# Token Price Combinations
Generate and plot price combinations for two cryptocurrency tokens to reach a target portfolio value
with specific token quantities.

![Output](images/plot.png)

Built with Python, CoinMarketCap API, and linear algebra.

## Setup
### CoinMarketCap
1. Create a [CoinMarketCap](https://pro.coinmarketcap.com/) account
1. Login and retrieve API key

### Environment File
> Note: use .env.example as a template.
1. Create an .env file in the root directory
1. Open the .env file and type the following, using your CoinMarketCap API key: 
`COINMARKETCAP_KEY="type your key here"`
1. Save the file

## Usage
### Directly Run the Script
Run the main.py script from root directory: `python3 src/main.py`

### Run in Docker Container
1. Create the image from root directory: `docker build -t token-price-combos .` 
    > Note: to verify image was created, run `docker images`
1. Create the container using the image: `docker create -i --env-file .env --name token-price-combos token-price-combos`
    > Note: to verify container was created, run `docker ps -a`
1. Start the container using the container id: `docker start -i token-price-combos`