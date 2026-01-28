"""Connect to CoinMarketCap API and retrieve data."""

import requests


class CoinMarketCapAPI:
    """Class to connect to and use the CoinMarketCap API."""

    BASE_URL = "https://pro-api.coinmarketcap.com/v2"

    def __init__(self, api_key: str):
        """Initialize CoinMarketCapAPI class.

        Args:
            api_key (str): CoinMarketCap API key.
        """
        self.api_key = api_key

    def get_crypto_quotes(self, symbol: str, convert: str = "USD") -> dict:
        """Get latest cryptocurrency quotes from CoinMarketCap API.

        Args:
            symbol (str): Cryptocurrency ticker symbol.
            convert (str, optional): Convert quotes to specified currency. Defaults to "USD".

        Returns:
            data (dict): Latest cryptocurrency quotes data.
        """

        url = f"{self.BASE_URL}/cryptocurrency/quotes/latest"
        headers = {"X-CMC_PRO_API_KEY": self.api_key}
        request = requests.get(
            url, headers=headers, params={"symbol": symbol, "convert": convert}, timeout=10
        )
        if request.status_code != 200:
            raise RuntimeError(
                "Error fetching data from CoinMarketCap API: "
                f"{request.status_code} - {request.text}"
            )

        data = request.json()

        return data
