#!/bin/bash

# Script để chạy trading system dễ dàng hơn

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MCP_DIR="$(cd "$SCRIPT_DIR/../tradingview-mcp" && pwd)"

echo "🚀 Crypto Trading System"
echo "========================"
echo ""

# Chạy với uv từ MCP directory
cd "$MCP_DIR"
uv run python "$SCRIPT_DIR/main.py" "$@"
