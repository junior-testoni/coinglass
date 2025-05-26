# List of additional Coinglass API endpoints for data gathering.
# Each key is a descriptive name used in the pipeline.
ADDITIONAL_ENDPOINTS = {
    # Market
    "futures_supported_coins": "/futures/supported-coins",
    "futures_supported_exchange_pairs": "/futures/supported-exchange-pairs",
    "futures_pairs_markets": "/api/futures/pairs-markets",
    "futures_coins_markets": "/api/futures/coins-markets",
    "futures_price_change_list": "/futures/price-change-list",
    "price_ohlc_history": "/api/price/ohlc-history",
    # Open Interest
    "oi_ohlc_history": "/api/futures/openInterest/ohlc-history",
    "oi_ohlc_aggregated_history": "/api/futures/openInterest/ohlc-aggregated-history",
    "oi_ohlc_aggregated_stablecoin": "/api/futures/openInterest/ohlc-aggregated-stablecoin",
    "oi_ohlc_aggregated_coin_margin": "/api/futures/openInterest/ohlc-aggregated-coin-margin-history",
    "oi_exchange_list": "/api/futures/openInterest/exchange-list",
    "oi_exchange_history_chart": "/api/futures/openInterest/exchange-history-chart",
    # Funding Rate
    "funding_rate_ohlc_history": "/api/futures/fundingRate/ohlc-history",
    "funding_rate_oi_weighted": "/api/futures/fundingRate/oi-weight-ohlc-history",
    "funding_rate_vol_weighted": "/api/futures/fundingRate/vol-weight-ohlc-history",
    "funding_rate_exchange_list": "/api/futures/fundingRate/exchange-list",
    "funding_rate_accumulated_exchange_list": "/api/futures/fundingRate/accumulated-exchange-list",
    "funding_rate_arbitrage": "/api/futures/fundingRate/arbitrage",
    # Long/Short Ratio
    "global_long_short_account_ratio": "/api/futures/global-long-short-account-ratio/history",
    "top_long_short_account_ratio": "/api/futures/top-long-short-account-ratio/history",
    "top_long_short_position_ratio": "/api/futures/top-long-short-position-ratio/history",
    "taker_buy_sell_volume_exchange_list": "/api/futures/taker-buy-sell-volume/exchange-list",
    # Liquidation
    "liquidation_history": "/api/futures/liquidation/history",
    "liquidation_aggregated_history": "/api/futures/liquidation/aggregated-history",
    "liquidation_coin_list": "/api/futures/liquidation/coin-list",
    "liquidation_exchange_list": "/api/futures/liquidation/exchange-list",
    "liquidation_order": "/api/futures/liquidation/order",
    "liquidation_heatmap_model1": "/api/futures/liquidation/heatmap/model1",
    "liquidation_heatmap_model2": "/api/futures/liquidation/heatmap/model2",
    "liquidation_heatmap_model3": "/api/futures/liquidation/heatmap/model3",
    "liquidation_aggregated_heatmap_model1": "/api/futures/liquidation/aggregated-heatmap/model1",
    "liquidation_aggregated_heatmap_model2": "/api/futures/liquidation/aggregated-heatmap/model2",
    "liquidation_aggregated_heatmap_model3": "/api/futures/liquidation/aggregated-heatmap/model3",
    "liquidation_map": "/api/futures/liquidation/map",
    "liquidation_aggregated_map": "/api/futures/liquidation/aggregated-map",
    # Order Book
    "orderbook_ask_bids_history": "/api/futures/orderbook/ask-bids-history",
    "orderbook_aggregated_ask_bids_history": "/api/futures/orderbook/aggregated-ask-bids-history",
    "orderbook_history": "/api/futures/orderbook/history",
    "orderbook_large_limit_order": "/api/futures/orderbook/large-limit-order",
    "orderbook_large_limit_order_history": "/api/futures/orderbook/large-limit-order-history",
    # Whale Positions
    "hyperliquid_whale_alert": "/api/hyperliquid/whale-alert",
    "hyperliquid_whale_position": "/api/hyperliquid/whale-position",
    # Taker Buy/Sell
    "taker_buy_sell_volume_history": "/api/futures/taker-buy-sell-volume/history",
    "aggregated_taker_buy_sell_volume_history": "/api/futures/aggregated-taker-buy-sell-volume/history",
    # Spots
    "spot_supported_coins": "/api/spot/supported-coins",
    "spot_supported_exchange_pairs": "/api/spot/supported-exchange-pairs",
    "spot_coins_markets": "/api/spot/coins-markets",
    "spot_pairs_markets": "/api/spot/pairs-markets",
    "spot_price_history": "/api/spot/price/history",
    # Spot Order Book
    "spot_orderbook_ask_bids_history": "/api/spot/orderbook/ask-bids-history",
    "spot_orderbook_aggregated_ask_bids_history": "/api/spot/orderbook/aggregated-ask-bids-history",
    "spot_orderbook_history": "/api/spot/orderbook/history",
    "spot_orderbook_large_limit_order": "/api/spot/orderbook/large-limit-order",
    "spot_orderbook_large_limit_order_history": "/api/spot/orderbook/large-limit-order-history",
    # Spot Taker Buy/Sell
    "spot_taker_buy_sell_volume_history": "/api/spot/taker-buy-sell-volume/history",
    "spot_aggregated_taker_buy_sell_volume_history": "/api/spot/aggregated-taker-buy-sell-volume/history",
    # Options
    "option_max_pain": "/api/option/max-pain",
    "option_info": "/api/option/info",
    "option_exchange_oi_history": "/api/option/exchange-oi-history",
    "option_exchange_vol_history": "/api/option/exchange-vol-history",
    # On-Chain
    "exchange_assets": "/api/exchange/assets",
    "exchange_balance_list": "/api/exchange/balance/list",
    "exchange_balance_chart": "/api/exchange/balance/chart",
    "exchange_chain_tx_list": "/api/exchange/chain/tx/list",
    # ETF
    "etf_bitcoin_list": "/api/etf/bitcoin/list",
    "hk_etf_bitcoin_flow_history": "/api/hk-etf/bitcoin/flow-history",
    "etf_bitcoin_net_assets_history": "/api/etf/bitcoin/net-assets/history",
    "etf_bitcoin_flow_history": "/api/etf/bitcoin/flow-history",
    "etf_bitcoin_premium_discount_history": "/api/etf/bitcoin/premium-discount/history",
    "etf_bitcoin_history": "/api/etf/bitcoin/history",
    "etf_bitcoin_price_history": "/api/etf/bitcoin/price/history",
    "etf_bitcoin_detail": "/api/etf/bitcoin/detail",
    "etf_ethereum_net_assets_history": "/api/etf/ethereum/net-assets-history",
    "etf_ethereum_list": "/api/etf/ethereum/list",
    "etf_ethereum_flow_history": "/api/etf/ethereum/flow-history",
    "grayscale_holdings_list": "/api/grayscale/holdings-list",
    "grayscale_premium_history": "/api/grayscale/premium-history",
    # Indic
    "rsi_list": "/api/futures/rsi/list",
    "basis_history": "/api/futures/basis/history",
    "coinbase_premium_index": "/api/coinbase-premium-index",
    "bitfinex_margin_long_short": "/api/bitfinex-margin-long-short",
    "index_ahr999": "/api/index/ahr999",
    "index_puell_multiple": "/api/index/puell-multiple",
    "index_stock_flow": "/api/index/stock-flow",
    "index_pi_cycle_indicator": "/api/index/pi-cycle-indicator",
    "index_golden_ratio_multiplier": "/api/index/golden-ratio-multiplier",
    "bitcoin_profitable_days": "/api/index/bitcoin/profitable-days",
    "bitcoin_rainbow_chart": "/api/index/bitcoin/rainbow-chart",
    "fear_greed_history": "/api/index/fear-greed-history",
    "stablecoin_marketcap_history": "/api/index/stableCoin-marketCap-history",
    "bitcoin_bubble_index": "/api/index/bitcoin/bubble-index",
    "bull_market_peak_indicator": "/api/bull-market-peak-indicator",
    "two_year_ma_multiplier": "/api/index/2-year-ma-multiplier",
    "two_hundred_week_ma_heatmap": "/api/index/200-week-moving-average-heatmap",
"borrow_interest_rate_history": "/api/borrow-interest-rate/history",
}

# A small subset of the above endpoints works without extra parameters and
# is accessible with the free Hobbyist plan. The pipeline uses this subset
# by default so it doesn't hit endpoints that require paid access or
# additional query arguments.
DEFAULT_ADDITIONAL_ENDPOINTS = {
    name: ADDITIONAL_ENDPOINTS[name]
    for name in [
        "liquidation_coin_list",
        "hyperliquid_whale_alert",
        "spot_supported_coins",
        "spot_supported_exchange_pairs",
        "option_exchange_vol_history",
    ]
}
