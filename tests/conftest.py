"""Module for pytest fixtures."""

import pytest

from src.cmc_api import CoinMarketCapAPI
from src.utils import Utils

@pytest.fixture()
def cmc_api() -> CoinMarketCapAPI:
    """Fixture to create a CoinMarketCapAPI object."""

    util = Utils()
    key = util.get_api_key()
    api = CoinMarketCapAPI(api_key=key)

    return api
