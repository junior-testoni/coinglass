# Coinglass BTC/ETH Data Pipeline – Plan & Implementation

## Overview and Plan

To reliably gather BTC and ETH derivatives data (open interest, long/short ratios, liquidations, funding rates) from the Coinglass Hobbyist API, we will build a structured Python pipeline. The solution will emphasize modular design, error handling, and easy maintenance, enabling future scheduling or real-time upgrades. Key steps include:

- **Authentication Setup:** Use the Coinglass API key from the Hobbyist plan in request headers for every call. Without the header, requests are rejected (HTTP 401).
- **Define Target Endpoints:** Identify and utilize the API endpoints available to Hobbyist users for each data type:
  - Open Interest – Aggregated open interest history across all exchanges.
  - Long/Short Ratio – Long versus short account ratio history for all accounts or top traders.
  - Liquidations – Aggregated long and short liquidation history across exchanges.
  - Funding Rates – Open-interest-weighted funding rate history.
- **Note:** Hobbyist plan supports these endpoints with a minimum interval of 4 hours, so we will use 4h or higher granularity for historical data.
- **Modular Design:** Create a reusable API client class (e.g., `CoinglassClient`) to handle HTTP requests, apply the API key, and implement methods for each data type. This keeps the code easy to extend.
- **Robust Error Handling:** Implement checks and retries for HTTP errors or API rate limits. Log failures with clear messages to troubleshoot issues without crashing the pipeline.
- **Local Storage:** Save data in an analysis-friendly format using an SQLite database with tables designed for easy queries.
- **Reusability and Scheduling:** Fetching for multiple symbols (BTC, ETH) and multiple endpoints should be straightforward. Functions can be called in loops or scheduled jobs (e.g., via cron) to update data regularly.
- **Documentation:** Use descriptive function names, docstrings, and comments to explain each component’s role.

Next, we present the Python implementation following this plan, with inline documentation explaining each part's role.
Implementation Structure
Below is a well-documented Python script for the pipeline. It can be treated as a single script or organized into modules (e.g., coinglass_client.py and main.py) as needed. Comments and docstrings describe how each piece contributes to the overall functionality:
python
Copy
Edit
import requests
import sqlite3
import logging
import time

# ------------------------
# Configuration & Constants
# ------------------------

API_KEY = "<YOUR_COINGLASS_API_KEY>"  # TODO: Set your Coinglass API key here.
BASE_URL = "https://open-api-v4.coinglass.com"  # Base URL for Coinglass API (v4).

# Define endpoints for each data type. Endpoints are chosen for Hobbyist availability.
ENDPOINTS = {
    # ^ Using top accounts ratio; alternatively, could use global accounts ratio endpoint (requires exchange param).
}

# Database file (SQLite) for storing fetched data
DB_FILE = "coinglass_data.db"

# Set up logging to console and file for debugging and audit trail.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),               # log to console
        logging.FileHandler("pipeline.log")    # log to file
    ]
)


# --------------
# Helper Classes
# --------------

class CoinglassClient:
    """Client for Coinglass API requests, handling authentication and basic error logic."""
    def __init__(self, api_key: str, base_url: str = BASE_URL):
        self.api_key = api_key
        self.base_url = base_url
        # Use a requests.Session for connection reuse (efficiency)
        self.session = requests.Session()
        # Attach API key to headers for all requests
        self.session.headers.update({
            "accept": "application/json",
        })
    
    def get(self, endpoint: str, params: dict) -> dict:
        """
        Send a GET request to the given Coinglass API endpoint with provided params.
        Returns parsed JSON on success, or raises an exception on failure.
        Implements basic retry logic for robustness.
        """
        url = self.base_url + endpoint
        max_retries = 3
        for attempt in range(1, max_retries+1):
            try:
                logging.debug(f"Requesting {url} with params {params} (Attempt {attempt})")
                response = self.session.get(url, params=params, timeout=10)
            except requests.RequestException as e:
                logging.error(f"Network error on attempt {attempt} for {endpoint}: {e}")
                if attempt < max_retries:
                    time.sleep(2)  # wait and retry
                    continue
                else:
                    raise  # Give up after max retries
            # If HTTP status not OK, consider retrying or error out
            if response.status_code != 200:
                logging.warning(f"Received HTTP {response.status_code} for {endpoint}: {response.text}")
                if attempt < max_retries:
                    time.sleep(1)
                    continue
                else:
                    response.raise_for_status()  # Will raise HTTPError
            # Parse JSON
            try:
                data = response.json()
            except ValueError:
                logging.error(f"Invalid JSON response for {endpoint}: {response.text[:200]}")
                raise
            # Coinglass API returns a "code" field for success/failure in JSON
            if data.get("code") != "0":
                # API-level error (e.g., invalid params). Log and raise.
                msg = data.get("msg", "Unknown API error")
                logging.error(f"API error for {endpoint}: code={data.get('code')}, msg={msg}")
                raise RuntimeError(f"Coinglass API error: {msg}")
            # On success, return the 'data' portion of the response
            return data.get("data", [])
        # If loop exits without return, raise an error (shouldn't happen due to returns/breaks above)
        raise RuntimeError(f"Failed to get data from {endpoint} after {max_retries} attempts.")
    
    # High-level methods for each data category:
    def fetch_open_interest_history(self, symbol: str, interval: str = "4h", start_time: int = None, end_time: int = None):
        """
        Fetch aggregated open interest history for a given symbol.
        """
        params = {"symbol": symbol, "interval": interval}
        if start_time: 
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time
        logging.info(f"Fetching open interest history for {symbol} (interval={interval})")
        return self.get(ENDPOINTS["open_interest"], params)
    
    def fetch_funding_rate_history(self, symbol: str, interval: str = "4h", start_time: int = None, end_time: int = None):
        """
        Interval must be >=4h for Hobbyist. Returns funding rates as list of OHLC values.
        """
        params = {"symbol": symbol, "interval": interval}
        if start_time: 
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time
        logging.info(f"Fetching funding rate history (OI-weighted) for {symbol} (interval={interval})")
        return self.get(ENDPOINTS["funding_rate"], params)
    
    def fetch_long_short_ratio_history(self, symbol: str, interval: str = "4h", exchange: str = "Binance", top_accounts: bool = True):
        """
        If top_accounts=False, you could use the global accounts ratio endpoint (requires exchange).
        Coinglass requires specifying exchange for long/short ratios on futures.
        """
        if top_accounts:
            endpoint = ENDPOINTS["long_short_ratio"]  # Top accounts ratio history
        else:
            endpoint = "/futures/global-long-short-account-ratio/history"  # (If using global ratio per exchange)
        params = {"symbol": symbol, "interval": interval, "exchangeName": exchange}
        label = "top accounts" if top_accounts else "global accounts"
        logging.info(f"Fetching {label} long/short ratio for {symbol} on {exchange} (interval={interval})")
        return self.get(endpoint, params)
    
    def fetch_liquidation_history(self, symbol: str, interval: str = "4h", start_time: int = None, end_time: int = None):
        """
        Returns list of data points with long and short liquidation USD amounts.
        """
        params = {"symbol": symbol, "interval": interval}
        if start_time: 
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time
        logging.info(f"Fetching liquidation history for {symbol} (interval={interval})")
        return self.get(ENDPOINTS["liquidations"], params)


class DataStorage:
    """Handles local data storage (SQLite DB) for the pipeline."""
    def __init__(self, db_path=DB_FILE):
        self.conn = sqlite3.connect(db_path)
        self.cur = self.conn.cursor()
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Create tables for each data type if they do not exist."""
        # Using symbol+time as a composite primary key to prevent duplicate inserts on re-run.
        # Time stored as integer (milliseconds since epoch).
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS open_interest (
                symbol TEXT,
                time   INTEGER,
                open   REAL,
                high   REAL,
                low    REAL,
                close  REAL,
                PRIMARY KEY(symbol, time)
            )
        """)
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS funding_rate (
                symbol TEXT,
                time   INTEGER,
                open   REAL,
                high   REAL,
                low    REAL,
                close  REAL,
                PRIMARY KEY(symbol, time)
            )
        """)
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS long_short_ratio (
                symbol TEXT,
                exchange TEXT,
                time   INTEGER,
                long_percent  REAL,
                short_percent REAL,
                long_short_ratio REAL,
                category TEXT,  -- 'global' or 'top' accounts
                PRIMARY KEY(symbol, exchange, time, category)
            )
        """)
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS liquidations (
                symbol TEXT,
                time   INTEGER,
                long_liquidation_usd  REAL,
                short_liquidation_usd REAL,
                PRIMARY KEY(symbol, time)
            )
        """)
        self.conn.commit()
    
    def insert_open_interest(self, symbol: str, data_points: list):
        """Insert multiple open interest records for a symbol."""
        # Each data_point is expected to have keys: time, open, high, low, close (as strings or numeric)
        rows = [(symbol, int(dp["time"]), float(dp["open"]), float(dp["high"]), 
                 float(dp["low"]), float(dp["close"])) for dp in data_points]
        self.cur.executemany(
            "INSERT OR IGNORE INTO open_interest (symbol, time, open, high, low, close) VALUES (?, ?, ?, ?, ?, ?)",
            rows
        )
        self.conn.commit()
        logging.info(f"Stored {len(rows)} open interest records for {symbol}.")
    
    def insert_funding_rate(self, symbol: str, data_points: list):
        """Insert multiple funding rate records for a symbol."""
        # data_point keys: time, open, high, low, close
        rows = [(symbol, int(dp["time"]), float(dp["open"]), float(dp["high"]), 
                 float(dp["low"]), float(dp["close"])) for dp in data_points]
        self.cur.executemany(
            "INSERT OR IGNORE INTO funding_rate (symbol, time, open, high, low, close) VALUES (?, ?, ?, ?, ?, ?)",
            rows
        )
        self.conn.commit()
        logging.info(f"Stored {len(rows)} funding rate records for {symbol}.")
    
    def insert_long_short_ratio(self, symbol: str, exchange: str, data_points: list, category: str):
        """Insert long/short ratio records (global or top accounts) for a symbol on a given exchange."""
        # data_point keys: time, and depending on endpoint:
        rows = []
        for dp in data_points:
            if "global_account_long_percent" in dp:
                long_pct = float(dp["global_account_long_percent"])
                short_pct = float(dp["global_account_short_percent"])
                ratio = float(dp["global_account_long_short_ratio"])
            else:
                long_pct = float(dp.get("top_account_long_percent", 0.0))
                short_pct = float(dp.get("top_account_short_percent", 0.0))
                ratio = float(dp.get("top_account_long_short_ratio", 0.0))
            rows.append((symbol, exchange, int(dp["time"]), long_pct, short_pct, ratio, category))
        self.cur.executemany(
            "INSERT OR IGNORE INTO long_short_ratio (symbol, exchange, time, long_percent, short_percent, long_short_ratio, category) VALUES (?, ?, ?, ?, ?, ?, ?)",
            rows
        )
        self.conn.commit()
        logging.info(f"Stored {len(rows)} {category} long/short ratio records for {symbol} on {exchange}.")
    
    def insert_liquidations(self, symbol: str, data_points: list):
        """Insert liquidation records for a symbol."""
        rows = [(symbol, int(dp["time"]), float(dp["aggregated_long_liquidation_usd"]), 
                 float(dp["aggregated_short_liquidation_usd"])) for dp in data_points]
        self.cur.executemany(
            "INSERT OR IGNORE INTO liquidations (symbol, time, long_liquidation_usd, short_liquidation_usd) VALUES (?, ?, ?, ?)",
            rows
        )
        self.conn.commit()
        logging.info(f"Stored {len(rows)} liquidation records for {symbol}.")
    
    def close(self):
        """Close the database connection."""
        self.cur.close()
        self.conn.close()


# -----------------
# Main Pipeline Run
# -----------------

if __name__ == "__main__":
    symbols = ["BTC", "ETH"]  # Target symbols to fetch
    interval = "4h"           # Data interval (Hobbyist allowed >= 4h)
    exchange_name = "Binance" # Exchange for long/short ratio (can be parameterized)
    
    client = CoinglassClient(API_KEY)
    storage = DataStorage(DB_FILE)
    
    for symbol in symbols:
        try:
            # 1. Fetch and store Open Interest data
            oi_data = client.fetch_open_interest_history(symbol, interval=interval)
            storage.insert_open_interest(symbol, oi_data)
            
            # 2. Fetch and store Funding Rate data
            fr_data = client.fetch_funding_rate_history(symbol, interval=interval)
            storage.insert_funding_rate(symbol, fr_data)
            
            # 3. Fetch and store Long/Short Ratio data (top accounts by default)
            ls_top_data = client.fetch_long_short_ratio_history(symbol, interval=interval, exchange=exchange_name, top_accounts=True)
            storage.insert_long_short_ratio(symbol, exchange_name, ls_top_data, category="top")
            # (Optional) Fetch global account ratio as well, if needed:
            # ls_global_data = client.fetch_long_short_ratio_history(symbol, interval=interval, exchange=exchange_name, top_accounts=False)
            # storage.insert_long_short_ratio(symbol, exchange_name, ls_global_data, category="global")
            
            # 4. Fetch and store Liquidation data
            liq_data = client.fetch_liquidation_history(symbol, interval=interval)
            storage.insert_liquidations(symbol, liq_data)
        
        except Exception as e:
            logging.error(f"Error fetching data for {symbol}: {e}")
            # Continue to next symbol if one fails, to not block the entire pipeline
            continue
    
    # Close DB connection
    storage.close()
    logging.info("Data pipeline run completed.")
Explanation of the Code Structure
Configuration Section: Sets the API key, base URL, endpoints, and logging configuration. The ENDPOINTS dict maps logical names to the API paths we need. For example, "open_interest" uses the aggregated open interest history path (available to Hobbyist)
docs.coinglass.com
. The logging is configured to output both to console and a file (pipeline.log) for audit and debugging.
CoinglassClient Class: Encapsulates the logic for making authenticated requests to Coinglass. The constructor creates a requests.Session and sets the CG-API-KEY header with the provided API key
docs.coinglass.com
 for all requests. The get method handles the HTTP GET call with retries and error checking:
It logs debug info, attempts the request up to 3 times on failure, and backs off briefly between attempts.
On a successful HTTP response, it parses JSON and then checks the "code" field in the JSON. Coinglass returns "code": "0" for success
docs.coinglass.com
, so any non-zero code is treated as an API error (logged and raised as an exception).
Each specific fetch_* method (open interest, funding, etc.) builds the required query parameters (symbol, interval, etc.) and calls get with the appropriate endpoint. We default to a 4-hour interval for all, respecting Hobbyist limits. If needed, the methods accept optional start_time and end_time (Unix timestamps in ms) to constrain the historical range.
The fetch_long_short_ratio_history method deserves special note: it by default uses the Top Accounts Long/Short Ratio endpoint
docs.coinglass.com
 with a specified exchange (default "Binance"). We include a parameter top_accounts to switch between top accounts vs. global accounts endpoints. (The Global Accounts Ratio endpoint
docs.coinglass.com
 also requires an exchange, so either way an exchange is specified. In our example, we only fetch the top trader ratio to keep it concise.)
DataStorage Class: Manages the SQLite database operations. In the constructor, it connects to the database file and ensures the required tables exist by calling _ensure_tables. Each table corresponds to a data category:
open_interest and funding_rate tables store time-series of OHLC values (with symbol and time as primary key).
long_short_ratio table stores percentage of long vs short and their ratio, with columns for symbol, exchange, time, and a category (either "global" or "top" to distinguish which kind of ratio data it is). The primary key includes symbol, exchange, time, and category to avoid duplicate entries if the pipeline is run repeatedly.
liquidations table stores the long and short liquidation volumes in USD for each symbol and time.
Each insert_* method takes the data list returned by the API client and inserts the records into the appropriate table. We use INSERT OR IGNORE so that if a record with the same primary key already exists (e.g., from a previous run), it won’t be duplicated. This way, the pipeline can be re-run or scheduled without accumulating duplicate data.
Data conversions: The API returns numeric values as strings in JSON
docs.coinglass.com
docs.coinglass.com
, so we convert them to float or int when inserting into the database.
Main Pipeline Run: Iterates over the target symbols (BTC and ETH). For each symbol, it sequentially:
Fetches open interest history and stores it.
Fetches funding rate history and stores it.
Fetches long/short ratio history for top accounts (and optionally could fetch global ratio) and stores it.
Fetches liquidation history and stores it.
Each step is wrapped in a try-except so that if one symbol’s data fails (e.g., a network issue), it logs the error and continues with the next symbol, rather than aborting the entire run. After processing all symbols, the database connection is closed gracefully.
Usage and Next Steps
Running the Pipeline: To use the script, insert your Coinglass API key, then run the script (e.g., python coinglass_pipeline.py). It will create/append to coinglass_data.db in the current directory and log progress to both the console and pipeline.log. On first run, it fetches the full available history for each data type (with 4h granularity). On subsequent runs, thanks to primary keys and INSERT OR IGNORE, it will only add new records (if any). For scheduling, you can set up a cron job or task scheduler to run this script periodically (e.g., daily at midnight to get the latest 4h data points).
Data Verification: The SQLite database can be inspected using any SQL client or even Python itself to ensure data is collected as expected. For example, one can connect with sqlite3 and run queries like SELECT COUNT(*) FROM open_interest WHERE symbol='BTC'; to see the number of records, etc.
Real-Time and Expansion: The current pipeline pulls historical data at a fixed interval. It can be expanded for real-time analysis by integrating Coinglass WebSocket endpoints (the API provides real-time feeds for liquidations and trades) or by reducing the interval if the API plan is upgraded (e.g., higher-tier plans allow 1m or 1h intervals). The modular design (with separate client methods and storage functions) makes it straightforward to add new endpoints (e.g., options data, order book stats) or to adapt storage (e.g., to CSV or a cloud database) if requirements change.
Reliability Considerations: We’ve included basic retry logic and error handling. In a production setting, you might enhance this with exponential backoff for rate-limit errors
docs.coinglass.com
 or more sophisticated logging (including alerting on failures). However, the provided solution covers the essentials for a dependable data pipeline with minimal external dependencies, tailored to an experienced user’s analysis needs.
## Running Tests
To make sure everything works, you can run a simple test suite. After installing the requirements with `pip install -r requirements.txt`, run `pytest` from the command line. Pytest will load the tests in the `tests/` folder and report if the import succeeds.

## Additional Coinglass Endpoints

The Coinglass API provides many more endpoints than those used in the basic
pipeline. The file `coinglass_endpoints.py` lists these extra paths so you can
expand the data you collect. The table below summarizes the available
endpoints and what each one returns.

| Endpoints | Description |
| --- | --- |
| /futures/supported-coins | Get supported futures coins |
| /futures/supported-exchange-pairs | Get supported exchanges and pairs |
| /api/futures/pairs-markets | Futures pair markets |
| /api/futures/coins-markets | Futures coin markets |
| /futures/price-change-list | Price change list |
| /api/price/ohlc-history | Price OHLC history |
| /api/futures/openInterest/ohlc-history | Open interest OHLC history |
| /api/futures/openInterest/ohlc-aggregated-history | Aggregated OI OHLC history |
| /api/futures/openInterest/ohlc-aggregated-stablecoin | Aggregated stablecoin OI OHLC |
| /api/futures/openInterest/ohlc-aggregated-coin-margin-history | Aggregated coin margin OI OHLC |
| /api/futures/openInterest/exchange-list | OI by exchange list |
| /api/futures/openInterest/exchange-history-chart | OI chart by exchange |
| /api/futures/fundingRate/ohlc-history | Funding rate OHLC history |
| /api/futures/fundingRate/oi-weight-ohlc-history | OI-weighted funding rate OHLC |
| /api/futures/fundingRate/vol-weight-ohlc-history | Volume-weighted funding rate OHLC |
| /api/futures/fundingRate/exchange-list | Funding rate by exchange list |
| /api/futures/fundingRate/accumulated-exchange-list | Cumulative funding rate list |
| /api/futures/fundingRate/arbitrage | Funding arbitrage opportunities |
| /api/futures/global-long-short-account-ratio/history | Global long/short account ratio |
| /api/futures/top-long-short-account-ratio/history | Top trader long/short ratio |
| /api/futures/top-long-short-position-ratio/history | Top trader position ratio |
| /api/futures/taker-buy-sell-volume/exchange-list | Exchange Taker Buy/Sell Ratio |
| /api/futures/liquidation/history | Pair Liquidation History |
| /api/futures/liquidation/aggregated-history | Coin Liquidation History |
| /api/futures/liquidation/coin-list | Liquidation Coin List |
| /api/futures/liquidation/exchange-list | Liquidation Exchange List |
| /api/futures/liquidation/order | Liquidation Order |
| /api/futures/liquidation/heatmap/model1 | Pair Liquidation Heatmap Model1 |
| /api/futures/liquidation/heatmap/model2 | Pair Liquidation Heatmap Model2 |
| /api/futures/liquidation/heatmap/model3 | Pair Liquidation Heatmap Model3 |
| /api/futures/liquidation/aggregated-heatmap/model1 | Coin Liquidation Heatmap Model1 |
| /api/futures/liquidation/aggregated-heatmap/model2 | Coin Liquidation Heatmap Model2 |
| /api/futures/liquidation/aggregated-heatmap/model3 | Coin Liquidation Heatmap Model3 |
| /api/futures/liquidation/map | Pair Liquidation Map |
| /api/futures/liquidation/aggregated-map | Coin Liquidation Map |
| /api/futures/orderbook/ask-bids-history | Pair Orderbook Bid&Ask(±range) |
| /api/futures/orderbook/aggregated-ask-bids-history | Coin Orderbook Bid&Ask(±range) |
| /api/futures/orderbook/history | Orderbook Heatmap |
| /api/futures/orderbook/large-limit-order | Large Orderbook |
| /api/futures/orderbook/large-limit-order-history | Large Orderbook History |
| /api/hyperliquid/whale-alert | Hyperliquid Whale Alert |
| /api/hyperliquid/whale-position | Hyperliquid Whale Position |
| /api/futures/taker-buy-sell-volume/history | Pair Taker Buy/Sell History |
| /api/futures/aggregated-taker-buy-sell-volume/history | Coin Taker Buy/Sell History |
| /api/spot/supported-coins | Supported Coins |
| /api/spot/supported-exchange-pairs | Suported Exchange and Pairs |
| /api/spot/coins-markets | Coins Markets |
| /api/spot/pairs-markets | Pairs Markets |
| /api/spot/price/history | Price OHLC History |
| /api/spot/orderbook/ask-bids-history | Pair Orderbook Bid&Ask(±range) |
| /api/spot/orderbook/aggregated-ask-bids-history | Coin Orderbook Bid&Ask(±range) |
| /api/spot/orderbook/history | Orderbook Heatmap |
| /api/spot/orderbook/large-limit-order | Large Orderbook |
| /api/spot/orderbook/large-limit-order-history | Large Orderbook History |
| /api/spot/taker-buy-sell-volume/history | Pair Taker Buy/Sell History |
| /api/spot/aggregated-taker-buy-sell-volume/history | Coin Taker Buy/Sell History |
| /api/option/max-pain | Option Max Pain |
| /api/option/info | Options Info |
| /api/option/exchange-oi-history | Exchange Open Interest History |
| /api/option/exchange-vol-history | Exchange Volume History |
| /api/exchange/assets | Exchange Assets |
| /api/exchange/balance/list | Exchange Balance List |
| /api/exchange/balance/chart | Exchange Balance Chart |
| /api/exchange/chain/tx/list | Exchange On-chain Transfers (ERC-20) |
| /api/etf/bitcoin/list | Bitcoin ETF List |
| /api/hk-etf/bitcoin/flow-history | Hong Kong ETF Flows History |
| /api/etf/bitcoin/net-assets/history | ETF NetAssets History |
| /api/etf/bitcoin/flow-history | ETF Flows History |
| /api/etf/bitcoin/premium-discount/history | ETF Premium/Discount History |
| /api/etf/bitcoin/history | ETF History |
| /api/etf/bitcoin/price/history | ETF Price History |
| /api/etf/bitcoin/detail | ETF Detail |
| /api/etf/ethereum/net-assets-history | ETF NetAssets History |
| /api/etf/ethereum/list | Ethereum ETF List |
| /api/etf/ethereum/flow-history | ETF Flows History |
| /api/grayscale/holdings-list | Holdings List |
| /api/grayscale/premium-history | Premium History |
| /api/futures/rsi/list | RSI List |
| /api/futures/basis/history | Futures Basis |
| /api/coinbase-premium-index | Coinbase Premium Index |
| /api/bitfinex-margin-long-short | Bitfinex Margin Long/Short |
| /api/index/ahr999 | AHR999 |
| /api/index/puell-multiple | Puell-Multiple |
| /api/index/stock-flow | Stock-to-Flow Model |
| /api/index/pi-cycle-indicator | Pi Cycle Top Indicator |
| /api/index/golden-ratio-multiplier | Golden-Ratio-Multiplier |
| /api/index/bitcoin/profitable-days | Bitcoin Profitable Days |
| /api/index/bitcoin/rainbow-chart | Bitcoin-Rainbow-Chart |
| /api/index/fear-greed-history | Crypto Fear & Greed Index |
| /api/index/stableCoin-marketCap-history | StableCoin MarketCap History |
| /api/index/bitcoin/bubble-index | Bitcoin Bubble Index |
| /api/bull-market-peak-indicator | Bull Market Peak Indicators |
| /api/index/2-year-ma-multiplier | Tow Year Ma Multiplier |
| /api/index/200-week-moving-average-heatmap | 200-Week Moving Avg Heatmap |
| /api/borrow-interest-rate/history | Borrow Interest Rate |

These endpoints may have different parameters. Refer to the official
Coinglass documentation for full details before using them.
