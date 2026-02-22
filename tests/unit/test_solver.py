"""Tests for the solver module."""

import pytest
import numpy as np

from src import solver


class TestCalculatePrices:
    """Tests for the calculate_prices function in the solver module."""

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
    def test_target_met(self, target, token_1, token_2, price_ratio):
        """Test the target is met with the prices returned."""
        result = solver.calculate_prices(target, token_1, token_2, price_ratio)

        assert target == (float(result[0]) * token_1) + (float(result[1]) * token_2)

    @pytest.mark.parametrize(
        "target, token_1, token_2, price_ratio",
        [
            (0, 0, 0, 0),
            (100, 0, 1.0, 0.5),
            (100, 1.0, 0, 0.5),
            (100, 1.0, 1.0, 0),
            (-100, 1.0, 1.0, 0.5),
            (100, -1.0, 1.0, 0.5),
            (100, 1.0, -1.0, 0.5),
            (100, 1.0, 1.0, -0.5),
            (-100, -1.0, -1.0, -0.5),
        ],
    )
    def test_invalid_args(self, target, token_1, token_2, price_ratio):
        """Test an error is raised for invalid arguments."""
        with pytest.raises(ValueError):
            solver.calculate_prices(target, token_1, token_2, price_ratio)

    def test_return_type(self):
        """Test a numpy array is returned."""
        result = solver.calculate_prices(100, 1.0, 1.0, 0.5)

        assert isinstance(result, np.ndarray)
