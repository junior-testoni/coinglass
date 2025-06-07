"""Fetch BTC derivatives data from Coinglass and save to CSV files.

This script demonstrates how to use the Coinglass API client provided in
``coinglass_pipeline.py`` to download a few datasets for Bitcoin. It keeps the
requests below 30 per minute using the built-in rate limiter.

Results are stored in separate CSV files so you can open them in Excel or other
spreadsheet tools.

Before running the script, set the ``COINGLASS_API_KEY`` environment variable to
your API key. Example:
    export COINGLASS_API_KEY=your_key_here

Run the script with:
    python fetch_btc_data_csv.py
"""

import os
import logging
import pandas as pd

from coinglass_pipeline import CoinglassClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

API_KEY = os.getenv("COINGLASS_API_KEY", "<YOUR_COINGLASS_API_KEY>")

if API_KEY == "<YOUR_COINGLASS_API_KEY>":
    logging.warning(
        "Please set your Coinglass API key via the COINGLASS_API_KEY environment variable"
    )

client = CoinglassClient(API_KEY)

SYMBOL = "BTC"
EXCHANGE = "Binance"  # used for the long/short ratio endpoint

# --- Open Interest ---
logging.info("Fetching open interest history for %s", SYMBOL)
open_interest = client.fetch_open_interest_history(SYMBOL)

pd.DataFrame(open_interest).to_csv("btc_open_interest.csv", index=False)
logging.info("Saved btc_open_interest.csv with %d records", len(open_interest))

# --- Long/Short Ratio ---
logging.info("Fetching long/short ratio for %s", SYMBOL)
long_short = client.fetch_long_short_ratio_history(SYMBOL, exchange=EXCHANGE)

pd.DataFrame(long_short).to_csv("btc_long_short_ratio.csv", index=False)
logging.info("Saved btc_long_short_ratio.csv with %d records", len(long_short))

# --- Liquidation Map ---
logging.info("Fetching liquidation map for %s", SYMBOL)
liquidation_map = client.fetch_generic(
    "/api/futures/liquidation/aggregated-map", {"symbol": SYMBOL}
)

pd.DataFrame(liquidation_map).to_csv("btc_liquidation_map.csv", index=False)
logging.info("Saved btc_liquidation_map.csv with %d records", len(liquidation_map))

# --- Options Data ---
option_endpoints = {
    "option_max_pain": "/api/option/max-pain",
    "option_info": "/api/option/info",
    "option_exchange_oi_history": "/api/option/exchange-oi-history",
    "option_exchange_vol_history": "/api/option/exchange-vol-history",
}

for name, endpoint in option_endpoints.items():
    logging.info("Fetching %s", name)
    try:
        data = client.fetch_generic(endpoint, {"symbol": SYMBOL})
    except Exception as exc:
        logging.error("Could not fetch %s: %s", name, exc)
        continue
    pd.DataFrame(data).to_csv(f"{name}.csv", index=False)
    logging.info("Saved %s.csv with %d records", name, len(data))

