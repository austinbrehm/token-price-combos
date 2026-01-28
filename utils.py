"""Utils class for common functions."""

import subprocess
import matplotlib.pyplot as plt


class Utils:
    """Class for common utility functions."""

    @staticmethod
    def get_api_key() -> str:
        """Get the CoinMarketCap API key from .bashrc file.

        Returns:
            key (str): CoinMarketCap API key, stored in .bashrc file.
        """
        key = subprocess.run(
            "source ~/.bashrc && echo $COINMARKETCAP_KEY",
            shell=True,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.rstrip()

        return key

    @staticmethod
    def plot(x: list, y: list, title: str, xlabel: str, ylabel: str) -> None:
        """
        Plot x-y data using Matplotlib.

        Args:
            x (list): Data for x-axis.
            y (list): Data for y-axis.
            title (str): Title of the plot.
            xlabel (str): Label for x-axis.
            ylabel (str): Label for y-axis.
        """
        plt.style.use("dark_background")
        plt.scatter(x[0], y[0], marker="x", c="chocolate", label="Current Price")
        plt.scatter(x[1:], y[1:], marker="o", c="gold", label="Future Price")
        plt.title(title, loc="left", fontsize=14, style="italic", color="wheat")
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        fig_manager = plt.get_current_fig_manager()
        fig_manager.full_screen_toggle()
        plt.legend()
        plt.grid(
            visible=True, which="both", color="gray", linestyle="--", linewidth=0.5
        )
        plt.show()
