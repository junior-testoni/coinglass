"""Coinglass BTC/ETH Data Pipeline

This script fetches cryptocurrency derivatives data (open interest,
funding rate, long/short ratio, and liquidations) from the Coinglass API
and stores it locally in an SQLite database. Each section of the code is
commented so you can understand what is happening even if you are not
familiar with Python.

The pipeline also provides helpers to call many other Coinglass API
endpoints. Those extra endpoints are listed in ``coinglass_endpoints.py``
and results are stored as raw JSON for reference.
"""

import logging
import os
import time
import sqlite3
import json
from typing import List, Dict

import requests
from coinglass_endpoints import DEFAULT_ADDITIONAL_ENDPOINTS

# ------------------------
# Configuration
# ------------------------

# Replace the placeholder below with your actual API key from Coinglass.
# You can also set an environment variable named ``COINGLASS_API_KEY`` so
# you do not need to edit this file each time.
API_KEY = os.getenv("COINGLASS_API_KEY", "<YOUR_COINGLASS_API_KEY>")

if API_KEY == "<YOUR_COINGLASS_API_KEY>":
    logging.warning(
        "Please set your Coinglass API key. Either edit API_KEY in the script "
        "or set the COINGLASS_API_KEY environment variable."
    )

# Base URL for the Coinglass API. Most endpoint paths already contain
# the ``/api`` prefix from the official documentation, so the base URL
# is simply the domain.
BASE_URL = "https://open-api-v4.coinglass.com"

# Endpoints we will call for the core data types used in the pipeline.
# ENDPOINTS maps a short name to the actual API path.
ENDPOINTS = {
    # Aggregated open interest history across all exchanges
    "open_interest": "/api/futures/openInterest/ohlc-aggregated-history",
    # Open-interest-weighted funding rate history
    "funding_rate": "/api/futures/fundingRate/oi-weight-ohlc-history",
    # Top trader long/short ratio history for a given exchange
    "long_short_ratio": "/api/futures/top-long-short-account-ratio/history",
    # Aggregated liquidation history for a coin
    "liquidations": "/api/futures/liquidation/aggregated-history",
}

# DEFAULT_ADDITIONAL_ENDPOINTS (imported above) contains a few extra API paths
# that work without extra parameters. You can edit that list to call other
# endpoints if you have the required plan and parameters.

# SQLite database file
DB_FILE = "coinglass_data.db"

# Set up logging so we can see what the script is doing.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("pipeline.log")],
)


class CoinglassClient:
    """Simple client for calling the Coinglass REST API.

    Parameters
    ----------
    api_key : str
        Your Coinglass API key.
    base_url : str, optional
        Base URL for all API requests.
    max_requests_per_minute : int, optional
        Limit on the number of requests we should send each minute.  The
        default of ``30`` matches the Hobbyist plan allowance.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = BASE_URL,
        max_requests_per_minute: int = 30,
    ) -> None:
        self.session = requests.Session()
        self.session.headers.update({
            "accept": "application/json",
            "CG-API-KEY": api_key,
        })
        self.base_url = base_url
        # Track time between requests so we do not exceed the rate limit.
        self.min_interval = 60.0 / float(max_requests_per_minute)
        self.last_request_time = 0.0

    def _respect_rate_limit(self) -> None:
        """Pause if the last request was sent too recently."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_interval:
            wait_time = self.min_interval - elapsed
            logging.debug("Sleeping %.2f seconds to respect rate limit", wait_time)
            time.sleep(wait_time)

    def _get(self, endpoint: str, params: Dict) -> List[Dict]:
        """Send a GET request and return the ``data`` field from the JSON response."""
        # Ensure endpoint does not have duplicate '/api' or missing '/'
        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint
        url = self.base_url.rstrip("/") + endpoint
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                logging.debug("Requesting %s", url)
                self._respect_rate_limit()
                resp = self.session.get(url, params=params, timeout=10)
                self.last_request_time = time.time()
            except requests.RequestException as exc:  # Network problem
                logging.warning("Network error: %s", exc)
                if attempt < max_retries:
                    time.sleep(2)
                    continue
                raise
            if resp.status_code != 200:
                logging.warning("HTTP %s: %s", resp.status_code, resp.text)
                if attempt < max_retries:
                    time.sleep(2)
                    continue
                resp.raise_for_status()
            try:
                data = resp.json()
            except ValueError:
                raise RuntimeError("Invalid JSON response")
            if data.get("code") != "0":
                raise RuntimeError(f"API error: {data.get('msg')}")
            return data.get("data", [])
        raise RuntimeError("Failed to get valid response after retries")

    def fetch_generic(self, endpoint: str, params: Dict | None = None) -> List[Dict]:
        """Fetch data from any Coinglass API endpoint.

        Parameters
        ----------
        endpoint : str
            The API path, e.g. ``"/api/spot/supported-coins"``.
        params : dict, optional
            Dictionary of query parameters. Many endpoints do not require any.
        """
        if params is None:
            params = {}
        return self._get(endpoint, params)

    # Convenience wrappers for each data category
    def fetch_open_interest_history(
        self,
        symbol: str,
        interval: str = "4h",
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> List[Dict]:
        """Fetch aggregated open interest history.

        Parameters
        ----------
        symbol : str
            Trading pair such as ``"BTC"`` or ``"ETH"``.
        interval : str, optional
            Timeframe of the data (default ``"4h"``). Hobbyist plans require
            4-hour or higher intervals.
        start_time, end_time : int, optional
            Unix timestamps in milliseconds to limit the date range.
        """

        params = {"symbol": symbol, "interval": interval}
        if start_time is not None:
            params["start_time"] = start_time
        if end_time is not None:
            params["end_time"] = end_time
        return self._get(ENDPOINTS["open_interest"], params)

    def fetch_funding_rate_history(
        self,
        symbol: str,
        interval: str = "4h",
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> List[Dict]:
        """Fetch funding rate history weighted by open interest."""

        params = {"symbol": symbol, "interval": interval}
        if start_time is not None:
            params["start_time"] = start_time
        if end_time is not None:
            params["end_time"] = end_time
        return self._get(ENDPOINTS["funding_rate"], params)

    def fetch_long_short_ratio_history(
        self,
        symbol: str,
        interval: str = "4h",
        exchange: str = "Binance",
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> List[Dict]:
        """Fetch the top trader long/short ratio for a given exchange."""

        params = {"symbol": symbol, "interval": interval, "exchangeName": exchange}
        if start_time is not None:
            params["start_time"] = start_time
        if end_time is not None:
            params["end_time"] = end_time
        return self._get(ENDPOINTS["long_short_ratio"], params)

    def fetch_liquidation_history(
        self,
        symbol: str,
        interval: str = "4h",
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> List[Dict]:
        """Fetch aggregated liquidation history."""

        params = {"symbol": symbol, "interval": interval}
        if start_time is not None:
            params["start_time"] = start_time
        if end_time is not None:
            params["end_time"] = end_time
        return self._get(ENDPOINTS["liquidations"], params)


class DataStorage:
    """Handles the SQLite database where we keep the downloaded data."""

    def __init__(self, db_path: str = DB_FILE) -> None:
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._ensure_tables()

    def _ensure_tables(self) -> None:
        """Create tables if they are missing."""
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS open_interest (
                symbol TEXT,
                time   INTEGER,
                open   REAL,
                high   REAL,
                low    REAL,
                close  REAL,
                PRIMARY KEY(symbol, time)
            )
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS funding_rate (
                symbol TEXT,
                time   INTEGER,
                open   REAL,
                high   REAL,
                low    REAL,
                close  REAL,
                PRIMARY KEY(symbol, time)
            )
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS long_short_ratio (
                symbol TEXT,
                exchange TEXT,
                time   INTEGER,
                long_percent  REAL,
                short_percent REAL,
                long_short_ratio REAL,
                category TEXT,
                PRIMARY KEY(symbol, exchange, time, category)
            )
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS liquidations (
                symbol TEXT,
                time   INTEGER,
                long_liquidation_usd  REAL,
                short_liquidation_usd REAL,
                PRIMARY KEY(symbol, time)
            )
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS raw_api_data (
                endpoint TEXT,
                params TEXT,
                retrieved_at INTEGER,
                data TEXT
            )
            """
        )
        self.conn.commit()

    def insert_open_interest(self, symbol: str, data: List[Dict]) -> None:
        rows = [
            (
                symbol,
                int(d["time"]),
                float(d["open"]),
                float(d["high"]),
                float(d["low"]),
                float(d["close"]),
            )
            for d in data
        ]
        self.cursor.executemany(
            "INSERT OR IGNORE INTO open_interest VALUES (?, ?, ?, ?, ?, ?)",
            rows,
        )
        self.conn.commit()
        logging.info("Stored %s open interest records for %s", len(rows), symbol)

    def insert_funding_rate(self, symbol: str, data: List[Dict]) -> None:
        rows = [
            (
                symbol,
                int(d["time"]),
                float(d["open"]),
                float(d["high"]),
                float(d["low"]),
                float(d["close"]),
            )
            for d in data
        ]
        self.cursor.executemany(
            "INSERT OR IGNORE INTO funding_rate VALUES (?, ?, ?, ?, ?, ?)",
            rows,
        )
        self.conn.commit()
        logging.info("Stored %s funding rate records for %s", len(rows), symbol)

    def insert_long_short_ratio(
        self, symbol: str, exchange: str, data: List[Dict], category: str
    ) -> None:
        rows = []
        for d in data:
            long_pct = float(d.get("top_account_long_percent", d.get("global_account_long_percent", 0)))
            short_pct = float(d.get("top_account_short_percent", d.get("global_account_short_percent", 0)))
            ratio = float(d.get("top_account_long_short_ratio", d.get("global_account_long_short_ratio", 0)))
            rows.append((symbol, exchange, int(d["time"]), long_pct, short_pct, ratio, category))
        self.cursor.executemany(
            "INSERT OR IGNORE INTO long_short_ratio VALUES (?, ?, ?, ?, ?, ?, ?)",
            rows,
        )
        self.conn.commit()
        logging.info(
            "Stored %s %s long/short ratio records for %s on %s",
            len(rows),
            category,
            symbol,
            exchange,
        )

    def insert_liquidations(self, symbol: str, data: List[Dict]) -> None:
        rows = [
            (
                symbol,
                int(d["time"]),
                float(d["aggregated_long_liquidation_usd"]),
                float(d["aggregated_short_liquidation_usd"]),
            )
            for d in data
        ]
        self.cursor.executemany(
            "INSERT OR IGNORE INTO liquidations VALUES (?, ?, ?, ?)",
            rows,
        )
        self.conn.commit()
        logging.info("Stored %s liquidation records for %s", len(rows), symbol)

    def insert_raw_data(self, endpoint: str, params: Dict, data: List[Dict]) -> None:
        """Store raw JSON results from any endpoint for future reference."""
        rows = [
            (
                endpoint,
                json.dumps(params),
                int(time.time()),
                json.dumps(record),
            )
            for record in data
        ]
        self.cursor.executemany(
            "INSERT INTO raw_api_data VALUES (?, ?, ?, ?)",
            rows,
        )
        self.conn.commit()
        logging.info("Stored %s raw records from %s", len(rows), endpoint)

    def close(self) -> None:
        self.conn.close()


if __name__ == "__main__":
    symbols = ["BTC", "ETH"]
    interval = "4h"  # Hobbyist plan allows minimum 4h interval
    exchange_name = "Binance"

    client = CoinglassClient(API_KEY)
    storage = DataStorage(DB_FILE)

    for sym in symbols:
        try:
            oi = client.fetch_open_interest_history(sym, interval)
            storage.insert_open_interest(sym, oi)

            fr = client.fetch_funding_rate_history(sym, interval)
            storage.insert_funding_rate(sym, fr)

            ls = client.fetch_long_short_ratio_history(sym, interval, exchange_name)
            storage.insert_long_short_ratio(sym, exchange_name, ls, "top")

            liq = client.fetch_liquidation_history(sym, interval)
            storage.insert_liquidations(sym, liq)
        except Exception as exc:
            logging.error("Error fetching data for %s: %s", sym, exc)
            continue

    # Fetch a few extra endpoints that do not require parameters. The list of
    # endpoints is defined in ``DEFAULT_ADDITIONAL_ENDPOINTS``. Feel free to
    # modify it if you want to retrieve more data.
    for ep_name, ep_path in DEFAULT_ADDITIONAL_ENDPOINTS.items():
        try:
            # ``fetch_generic`` expects just the endpoint path. It will
            # combine it with ``BASE_URL`` internally to build the full URL.
            data = client.fetch_generic(ep_path)
            storage.insert_raw_data(ep_name, {}, data)
        except Exception as exc:
            logging.error("Error fetching %s: %s", ep_name, exc)
            continue

    storage.close()
    logging.info("Data pipeline run completed.")
