"""Connect to CoinMarketCap API and retrieve data."""

import requests


class CoinMarketCapAPI:
    """Class to connect to and use the CoinMarketCap API."""

    BASE_URL = "https://pro-api.coinmarketcap.com"
    HEADER = "X-CMC_PRO_API_KEY"

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

        url = f"{self.BASE_URL}/v2/cryptocurrency/quotes/latest"
        headers = {self.HEADER: self.api_key}
        request = requests.get(
            url, headers=headers, params={"symbol": symbol, "convert": convert}, timeout=10
        )
        if request.status_code != 200:
            raise RuntimeError(
                "❌ Error fetching data from CoinMarketCap API: "
                f"{request.status_code} - {request.text}"
            )

        data = request.json()

        return data

    def get_id_map(self) -> dict:
        """Get cryptocurrency ID map from CoinMarketCap API.

        Returns:
            data (dict): Cryptocurrency ID map data.
        """

        url = f"{self.BASE_URL}/v1/cryptocurrency/map"
        headers = {self.HEADER: self.api_key}
        request = requests.get(
            url, headers=headers, timeout=10
        )
        if request.status_code != 200:
            raise RuntimeError(
                "❌ Error fetching data from CoinMarketCap API: "
                f"{request.status_code} - {request.text}"
            )

        data = request.json()

        return data