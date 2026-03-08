"""Utils class for common functions."""

from datetime import datetime
from io import BytesIO
from typing import Optional

import matplotlib.pyplot as plt


class Utils:
    """Class for common utility functions."""

    @staticmethod
    def get_api_key(env_file: Optional[str] = None) -> str:
        """Get the CoinMarketCap API key from .env file.

        The key should be stored in the .env file in the format:
        COINMARKETCAP_KEY="your_api_key_here"

        Args:
            env_file: Path to .env file. If None, uses ./.env

        Returns:
            key (str): CoinMarketCap API key, stored in .env file.
        """
        path = env_file or "./.env"
        key = ""
        with open(path, "r", encoding="utf8") as file:
            for line in file:
                if line.startswith("COINMARKETCAP_KEY="):
                    key = line.split("=")[1].strip().strip('"')

        return key

    @staticmethod
    def plot(x: list, y: list, title: str, xlabel: str, ylabel: str) -> str:
        """
        Plot x-y data using Matplotlib.

        Args:
            x (list): Data for x-axis.
            y (list): Data for y-axis.
            title (str): Title of the plot.
            xlabel (str): Label for x-axis.
            ylabel (str): Label for y-axis.

        Returns:
            filename (str): Name of the exported .png file.
        """
        plt.style.use("dark_background")
        plt.figure(figsize=(10, 6))
        plt.scatter(x[0], y[0], marker="x", c="coral", label="Current Price")
        plt.scatter(x[1:], y[1:], marker="o", c="skyblue", label="Potential Price")
        plt.title(title, loc="left", fontsize=14, style="italic", color="white")
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.legend()
        plt.grid(
            visible=True, which="both", color="gray", linestyle="--", linewidth=0.5
        )
        # fig_manager = plt.get_current_fig_manager()
        # fig_manager.full_screen_toggle()
        # plt.show()
        filename = f"price_combos_{datetime.now().isoformat()}.png"
        plt.savefig(f"images/{filename}")
        plt.close()

        return filename

    @staticmethod
    def plot_to_buffer(
        x: list, y: list, title: str, xlabel: str, ylabel: str
    ) -> bytes:
        """Plot x-y data to an in-memory buffer and return PNG bytes.

        Same styling as plot() but returns bytes for web/serving.
        """
        plt.style.use("dark_background")
        plt.figure(figsize=(10, 6))
        plt.scatter(x[0], y[0], marker="x", c="coral", label="Current Price")
        plt.scatter(x[1:], y[1:], marker="o", c="skyblue", label="Future Price")
        plt.title(title, loc="left", fontsize=14, style="italic", color="white")
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.legend()
        plt.grid(
            visible=True, which="both", color="gray", linestyle="--", linewidth=0.5
        )
        buf = BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        plt.close()
        return buf.read()
