"""Utils class for common functions."""

import matplotlib.pyplot as plt


class Utils:
    """Class for common utility functions."""

    @staticmethod
    def get_api_key() -> str:
        """Get the CoinMarketCap API key from .env file.

        The key should be stored in the .env file in the format:
        COINMARKETCAP_KEY="your_api_key_here"

        Returns:
            key (str): CoinMarketCap API key, stored in .env file.
        """
        key = ""
        with open("./.env", "r", encoding="utf8") as file:
            for line in file:
                if line.startswith("COINMARKETCAP_KEY="):
                    key = line.split("=")[1].strip().strip('"')

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
        plt.legend()
        plt.grid(
            visible=True, which="both", color="gray", linestyle="--", linewidth=0.5
        )
        fig_manager = plt.get_current_fig_manager()
        fig_manager.full_screen_toggle()
        plt.savefig("images/price_combos.png")
        plt.show()
        # TODO: figure out how to show plot when running in Docker container
