"""Tests for the solver module."""

import pytest

from src import solver


@pytest.mark.parametrize(
    "target, token_1, token_2, price_ratio",
    [
        (10, 10, 100, 0.1),
        (100, 1.0, 1.0, 0.5),
        (100, 2.0, 1.0, 0.5),
        (100, 10.0, 1.0, 0.1),
        (10_000, 1.0, 1.0, 1.0),
        (56_879, 22, 3, 0.43),
        (1_000_000, 2.0, 1.0, 0.5),
    ],
)
def test_calculate_prices(target, token_1, token_2, price_ratio):
    """Tests the calculate_prices function with various inputs."""
    result = solver.calculate_prices(target, token_1, token_2, price_ratio)

    assert target == (float(result[0]) * token_1) + (float(result[1]) * token_2)
