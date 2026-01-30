"""Tests for cmc_api.py module."""

import pytest


class TestGetCryptoQuotes:
    """Tests the get_crypto_quotes() method of CoinMarketCapAPI class."""

    @pytest.mark.parametrize("symbol", ["BTC", "ETH", "POL"])
    def test_valid_symbols(self, symbol, cmc_api):
        """Test valid symbols."""

        data = cmc_api.get_crypto_quotes(symbol=symbol)

        assert symbol in data["data"]
