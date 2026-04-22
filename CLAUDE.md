# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Structure

Two independent sub-projects share this root:

- **`tradingview-mcp/`** — MCP server that exposes TradingView market data as Claude tools. This is the active, maintained project.
- **`crypto-trading-system/`** — Standalone Python trading analysis system that consumes the MCP server's data (analysis only, no live order execution).

## tradingview-mcp

### Setup & Run

```bash
cd tradingview-mcp
uv sync                                        # install dependencies into .venv
uv run python src/tradingview_mcp/server.py    # run MCP server (stdio transport)
uv run mcp dev src/tradingview_mcp/server.py  # run with MCP Inspector for debugging
uv run python test_api.py                      # smoke-test individual functions
```

### MCP Configuration (Claude Code)

`.mcp.json` at the repo root already points to the correct path:
```json
{
  "mcpServers": {
    "tradingview-mcp-local": {
      "command": "uv",
      "args": ["run", "python", "src/tradingview_mcp/server.py"],
      "cwd": "/Users/will208/Desktop/Desktop - WillのMacBook Air/MCP Trading /tradingview-mcp"
    }
  }
}
```

### Architecture

`server.py` is the single entry point. It creates a `FastMCP` instance and registers all tools directly as decorated functions. There is no router or tool registry — adding a new tool means adding a new `@mcp.tool()` function in `server.py`.

Data flow for most tools:
1. `sanitize_exchange` / `sanitize_timeframe` validate inputs (`core/utils/validators.py`)
2. `load_symbols(exchange)` reads symbol lists from `coinlist/<exchange>.txt`
3. `get_multiple_analysis()` (from `tradingview-ta`) fetches live data in batches of 200
4. `compute_metrics()` (`core/services/indicators.py`) calculates BBW, BB rating (-3→+3), and price change

Two data backends are used and both are optional-import guarded:
- **`tradingview-ta`** — used by most tools; fetches per-symbol indicator snapshots
- **`tradingview-screener`** — used by `multi_changes` and the advanced pattern fallback; runs SQL-like screener queries

### Bollinger Band Rating System

Implemented in `core/services/indicators.py:compute_bb_rating_signal`. Rating is -3 to +3 based on price position relative to BB upper/middle/lower bands. BBW (band width) = `(upper - lower) / SMA20` — lower values signal a squeeze.

### Exchanges & Timeframes

Valid exchanges are the keys of `EXCHANGE_SCREENER` in `validators.py` (lowercase): `kucoin`, `binance`, `bybit`, `okx`, `coinbase`, `gateio`, `huobi`, `bitfinex`, `bist`, `nasdaq`, `nyse`, `all`.

Valid timeframes: `5m`, `15m`, `1h`, `4h`, `1D`, `1W`, `1M`.

### Rate Limiting

TradingView has undocumented rate limits. If tools return empty arrays, wait 5–10 minutes. KuCoin and BIST are the most reliable data sources.

## crypto-trading-system

### Setup & Run

```bash
cd crypto-trading-system
pip install -r requirements.txt

python main.py --mode scan
python main.py --mode trade --strategy breakout
python main.py --mode backtest --strategy breakout --days 30
python dashboard.py
```

### Architecture

`main.py` dispatches to modes (`scan`, `trade`, `backtest`). Strategies live in `strategies/` and extend `BaseStrategy`. Analyzers in `analyzers/` are independent modules for technical analysis, pattern recognition, and volume. `risk_manager.py` enforces position sizing and drawdown limits. Configuration is read from `config/settings.json`.

This system performs **analysis and signal generation only** — it does not execute live trades automatically.
