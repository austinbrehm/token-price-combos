import base64
import logging
import subprocess
import sys
import tempfile
from pathlib import Path

import matplotlib
matplotlib.use("agg")  # Non-interactive backend for worker threads (no GUI)
import matplotlib.pyplot as plt
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from io import BytesIO


logger = logging.getLogger(__name__)

# Project root (parent of django/) for running src/main.py
PROJECT_ROOT = Path(settings.BASE_DIR).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
MAIN_SCRIPT = SRC_DIR / "main.py"


def index(request):
    return render(request, 'tokens/index.html')


def _validate_and_get_plot(form_data):
    """Run same validation as src/main.py; return (form_errors, plot_data_url, current_prices, first_prices, second_prices, first_symbol, second_symbol).

    form_errors: list of error messages (from ValueError in generate_plot_bytes).
    plot_data_url: data URL for PNG when valid, else None.
    current_prices: dict {symbol: price} when valid, else None.
    first_prices, second_prices: lists of price combos when valid, else None.
    first_symbol, second_symbol: token symbols (from form_data).
    """
    first_symbol = (form_data.get('first_token_symbol') or '').strip()
    second_symbol = (form_data.get('second_token_symbol') or '').strip()
    first_holdings = form_data.get('first_token_holdings')
    second_holdings = form_data.get('second_token_holdings')
    target = form_data.get('target_portfolio_value')

    # Basic parsing (mirror token_plot)
    try:
        first_holdings = float(first_holdings) if first_holdings else None
        second_holdings = float(second_holdings) if second_holdings else None
        target = int(float(target)) if target else None
    except (TypeError, ValueError):
        first_holdings = second_holdings = target = None

    first_symbol = first_symbol.strip().upper() if first_symbol else ''
    second_symbol = second_symbol.strip().upper() if second_symbol else ''

    # Require all fields
    if not all([first_symbol, first_holdings is not None, second_symbol,
                second_holdings is not None, target is not None]):
        return (['Please fill in all fields: both token symbols, both holdings, and target portfolio value.'], None, None, None, None, first_symbol or '', second_symbol or '')

    # Same rules as main.py: positive values, different symbols
    if first_holdings <= 0 or second_holdings <= 0 or target <= 0:
        return (['Holdings and target must be positive.'], None, None, None, None, first_symbol, second_symbol)
    if first_symbol == second_symbol:
        return (['First and second token symbols must be different.'], None, None, None, None, first_symbol, second_symbol)

    # Run full validation and plot generation (same as main.py generate_plot_bytes)
    if str(SRC_DIR) not in sys.path:
        sys.path.insert(0, str(SRC_DIR))
    try:
        from main import generate_plot_bytes
        png_bytes, token_prices, first_prices, second_prices = generate_plot_bytes(
            first_symbol,
            first_holdings,
            second_symbol,
            second_holdings,
            target,
            env_dir=str(PROJECT_ROOT),
        )
        data_url = 'data:image/png;base64,' + base64.b64encode(png_bytes).decode('ascii')
        return ([], data_url, token_prices, first_prices, second_prices, first_symbol, second_symbol)
    except ValueError as e:
        return ([str(e)], None, None, None, None, first_symbol, second_symbol)
    except Exception as e:
        logger.warning("Validation/plot failed: %s", e)
        return ([f'Something went wrong: {e}'], None, None, None, None, first_symbol, second_symbol)


def token_list(request):
    plot_query = request.GET.urlencode()
    form_data = {
        'first_token_symbol': request.GET.get('first_token_symbol', ''),
        'first_token_holdings': request.GET.get('first_token_holdings', ''),
        'second_token_symbol': request.GET.get('second_token_symbol', ''),
        'second_token_holdings': request.GET.get('second_token_holdings', ''),
        'target_portfolio_value': request.GET.get('target_portfolio_value', ''),
    }

    form_errors = []
    plot_data_url = None
    current_prices = None
    first_prices = None
    second_prices = None
    first_symbol = ''
    second_symbol = ''
    if any(form_data.values()):
        form_errors, plot_data_url, current_prices, first_prices, second_prices, first_symbol, second_symbol = _validate_and_get_plot(form_data)

    price_rows = None
    ideal_prices = None
    price_difference = None
    if first_prices is not None and second_prices is not None:
        price_rows = [
            (f"{p1:,.2f}", f"{p2:,.2f}")
            for p1, p2 in zip(first_prices[1:], second_prices[1:])
        ]
        ideal_prices = {first_symbol: first_prices[5], second_symbol: second_prices[5]}
        first_diff = (ideal_prices[first_symbol] - current_prices[first_symbol]) / current_prices[first_symbol] * 100
        second_diff = (ideal_prices[second_symbol] - current_prices[second_symbol]) / current_prices[second_symbol] * 100
        price_difference = {first_symbol: first_diff, second_symbol: second_diff}

    return render(request, 'tokens/token_list.html', {
        'plot_query': plot_query,
        'form_data': form_data,
        'form_errors': form_errors,
        'plot_data_url': plot_data_url,
        'current_prices': current_prices,
        'price_rows': price_rows,
        'ideal_prices': ideal_prices,
        'price_difference': price_difference,
        'target_value': form_data['target_portfolio_value'],
        'first_symbol': first_symbol,
        'second_symbol': second_symbol,
    })


def _placeholder_plot_bytes():
    """Return a small placeholder PNG when form params are missing or invalid."""
    fig, ax = plt.subplots(figsize=(6, 3))
    fig.patch.set_facecolor('#2b2b2b')
    ax.set_facecolor('#2b2b2b')
    ax.set_axis_off()
    ax.text(0.5, 0.5, 'Fill in the form above and click Update\nto see the price combo plot.', ha='center', va='center', fontsize=12, color='#ccc', transform=ax.transAxes)
    buf = BytesIO()
    fig.savefig(buf, format='png', facecolor=fig.get_facecolor(), edgecolor='none')
    buf.seek(0)
    plt.close(fig)
    return buf.read()


def token_plot(request):
    first_symbol = (request.GET.get('first_token_symbol') or '').strip()
    first_holdings = request.GET.get('first_token_holdings')
    second_symbol = (request.GET.get('second_token_symbol') or '').strip()
    second_holdings = request.GET.get('second_token_holdings')
    target = request.GET.get('target_portfolio_value')

    try:
        first_holdings = float(first_holdings) if first_holdings else None
        second_holdings = float(second_holdings) if second_holdings else None
        target = int(float(target)) if target else None
    except (TypeError, ValueError):
        first_holdings = second_holdings = target = None

    if not all([first_symbol, first_holdings, second_symbol, second_holdings, target]):
        return HttpResponse(_placeholder_plot_bytes(), content_type='image/png')

    # Run src/main.py with form params as CLI args and serve the generated plot
    png_bytes = _run_script_plot(
        first_symbol, first_holdings, second_symbol, second_holdings, target
    )
    if png_bytes is not None:
        return HttpResponse(png_bytes, content_type='image/png')
    return HttpResponse(_placeholder_plot_bytes(), content_type='image/png')


def _run_script_plot(
    first_symbol, first_holdings, second_symbol, second_holdings, target
):
    """Run src/main.py with CLI args; return PNG bytes or None on failure."""
    if not MAIN_SCRIPT.is_file():
        logger.warning("Script not found: %s", MAIN_SCRIPT)
        return _fallback_plot_bytes(
            first_symbol, first_holdings, second_symbol, second_holdings, target
        )
    with tempfile.NamedTemporaryFile(
        suffix=".png", delete=False, dir=PROJECT_ROOT
    ) as tmp:
        out_path = tmp.name
    try:
        result = subprocess.run(
            [
                sys.executable,
                str(MAIN_SCRIPT),
                "--first-symbol", first_symbol.strip(),
                "--first-holdings", str(first_holdings),
                "--second-symbol", second_symbol.strip(),
                "--second-holdings", str(second_holdings),
                "--target", str(int(target)),
                "--output", out_path,
                "--env-dir", str(PROJECT_ROOT),
            ],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            logger.warning(
                "main.py exited %s: %s", result.returncode, result.stderr or result.stdout
            )
            return _fallback_plot_bytes(
                first_symbol, first_holdings, second_symbol, second_holdings, target
            )
        png_bytes = Path(out_path).read_bytes()
        return png_bytes
    except (subprocess.TimeoutExpired, OSError, Exception) as e:
        logger.warning("Subprocess run failed: %s", e)
        return _fallback_plot_bytes(
            first_symbol, first_holdings, second_symbol, second_holdings, target
        )
    finally:
        Path(out_path).unlink(missing_ok=True)


def _fallback_plot_bytes(
    first_symbol, first_holdings, second_symbol, second_holdings, target
):
    """Generate plot via generate_plot_bytes (same logic as script) when subprocess fails."""
    if str(SRC_DIR) not in sys.path:
        sys.path.insert(0, str(SRC_DIR))
    try:
        from main import generate_plot_bytes
        png_bytes, *_ = generate_plot_bytes(
            first_symbol,
            first_holdings,
            second_symbol,
            second_holdings,
            target,
            env_dir=str(PROJECT_ROOT),
        )
        return png_bytes
    except Exception as e:
        logger.warning("Fallback generate_plot_bytes failed: %s", e)
        return None
