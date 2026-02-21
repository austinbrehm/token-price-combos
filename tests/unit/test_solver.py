"""Tests for the solver module."""

import pytest
import numpy as np

from src import solver


@pytest.mark.parametrize(
    "target, token_1, token_2, price_ratio, expected_prices",
    [
        (100, 1.0, 1.0, 0.5, np.array([33.33, 66.67])),
        (100, 2.0, 1.0, 0.5, np.array([25.0, 50.0])),
        (100, 10.0, 1.0, 0.1, np.array([5.0, 50.0])),
    ],
)
def test_calculate_prices(target, token_1, token_2, price_ratio, expected_prices):
    """Tests the calculate_prices function with various inputs."""
    result = solver.calculate_prices(target, token_1, token_2, price_ratio)

    np.testing.assert_equal(np.round(result, decimals=2), expected_prices)