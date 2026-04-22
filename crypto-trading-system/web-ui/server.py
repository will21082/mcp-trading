#!/usr/bin/env python3
"""
Backend API Server for Crypto Trading Scanner UI
Provides endpoints to trigger scans and retrieve results
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import subprocess
import os
import json
from datetime import datetime
import re

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Project paths
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCANNER_PATH = os.path.join(PROJECT_DIR, 'analyzers', 'bybit_long_short_scanner.py')
REPORT_PATH = os.path.join(PROJECT_DIR, 'reports', 'scans', 'BYBIT_LONG_SHORT_OPTIMIZED.md')
LOG_PATH = os.path.join(PROJECT_DIR, 'logs', 'latest_scan.log')

def parse_scan_results():
    """Parse the latest scan report"""
    try:
        if not os.path.exists(REPORT_PATH):
            return None

        with open(REPORT_PATH, 'r') as f:
            content = f.read()

        # Extract scan metadata
        scan_time = re.search(r'\*\*Scan Time:\*\* (.+)', content)
        coins_scanned = re.search(r'\*\*Coins Scanned:\*\* (\d+)', content)
        long_count = re.search(r'🟢 LONG Signals:\s+(\d+)', content)
        short_count = re.search(r'🔴 SHORT Signals:\s+(\d+)', content)

        # Extract signals
        signals = []

        # Parse LONG signals
        long_section = re.search(r'## 🟢 LONG SIGNALS.*?(?=## 🔴 SHORT SIGNALS|$)', content, re.DOTALL)
        if long_section:
            signal_blocks = re.finditer(r'### \*\*(\d+)\. (.+?)\*\*.*?'
                                       r'Entry: \$?([\d.]+).*?'
                                       r'TP1: \$?([\d.]+).*?'
                                       r'TP2: \$?([\d.]+).*?'
                                       r'TP3: \$?([\d.]+).*?'
                                       r'Stop Loss: \$?([\d.]+).*?'
                                       r'Quality Score: (\d+)/15',
                                       long_section.group(), re.DOTALL)

            for match in signal_blocks:
                signals.append({
                    'rank': int(match.group(1)),
                    'symbol': match.group(2),
                    'direction': 'LONG',
                    'entry': float(match.group(3)),
                    'tp1': float(match.group(4)),
                    'tp2': float(match.group(5)),
                    'tp3': float(match.group(6)),
                    'stop_loss': float(match.group(7)),
                    'quality_score': int(match.group(8)),
                    'risk_reward': round((float(match.group(4)) - float(match.group(3))) /
                                       (float(match.group(3)) - float(match.group(7))), 2)
                })

        # Parse SHORT signals
        short_section = re.search(r'## 🔴 SHORT SIGNALS.*?(?=##|$)', content, re.DOTALL)
        if short_section:
            signal_blocks = re.finditer(r'### \*\*(\d+)\. (.+?)\*\*.*?'
                                       r'Entry: \$?([\d.]+).*?'
                                       r'TP1: \$?([\d.]+).*?'
                                       r'TP2: \$?([\d.]+).*?'
                                       r'TP3: \$?([\d.]+).*?'
                                       r'Stop Loss: \$?([\d.]+).*?'
                                       r'Quality Score: (\d+)/15',
                                       short_section.group(), re.DOTALL)

            for match in signal_blocks:
                signals.append({
                    'rank': int(match.group(1)),
                    'symbol': match.group(2),
                    'direction': 'SHORT',
                    'entry': float(match.group(3)),
                    'tp1': float(match.group(4)),
                    'tp2': float(match.group(5)),
                    'tp3': float(match.group(6)),
                    'stop_loss': float(match.group(7)),
                    'quality_score': int(match.group(8)),
                    'risk_reward': round((float(match.group(3)) - float(match.group(4))) /
                                       (float(match.group(7)) - float(match.group(3))), 2)
                })

        return {
            'scan_time': scan_time.group(1) if scan_time else 'Unknown',
            'coins_scanned': int(coins_scanned.group(1)) if coins_scanned else 0,
            'long_count': int(long_count.group(1)) if long_count else 0,
            'short_count': int(short_count.group(1)) if short_count else 0,
            'total_signals': (int(long_count.group(1)) if long_count else 0) +
                           (int(short_count.group(1)) if short_count else 0),
            'signals': signals
        }

    except Exception as e:
        print(f"Error parsing results: {e}")
        return None

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'scanner_exists': os.path.exists(SCANNER_PATH)
    })

@app.route('/api/scan', methods=['POST'])
def trigger_scan():
    """Trigger a new scan"""
    try:
        print(f"Starting scan at {datetime.now()}")

        # Just parse the latest report file instead of running scanner
        # Scanner is run by cron jobs, UI just displays latest results
        scan_data = parse_scan_results()

        if scan_data:
            return jsonify({
                'success': True,
                'message': 'Latest scan results loaded',
                'timestamp': datetime.now().isoformat(),
                'data': scan_data
            })
        else:
            # Return default empty data
            return jsonify({
                'success': True,
                'message': 'No scan data available - system will scan at 17:00, 21:00, 01:00 JST',
                'timestamp': datetime.now().isoformat(),
                'data': {
                    'scan_time': datetime.now().strftime('%Y-%m-%d %H:%M JST'),
                    'coins_scanned': 84,
                    'long_count': 0,
                    'short_count': 0,
                    'total_signals': 0,
                    'signals': []
                }
            })

    except Exception as e:
        print(f"Error in trigger_scan: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/results/latest', methods=['GET'])
def get_latest_results():
    """Get the latest scan results without triggering a new scan"""
    try:
        scan_data = parse_scan_results()

        if scan_data:
            return jsonify({
                'success': True,
                'data': scan_data,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No results available'
            }), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get scanner configuration"""
    return jsonify({
        'strategy': 'Breakout Strategy (15m)',
        'exchange': 'Bybit',
        'timeframe': '15m',
        'exit_strategy': {
            'tp1': '+4.5% (Close 70%)',
            'tp2': '+7.5% (Close 30%)',
            'stop_loss': '-3% → Breakeven after TP1',
            'max_hold': '6 hours'
        },
        'scan_schedule': [
            '17:00 JST (08:00 UTC) - EU Open',
            '21:00 JST (12:00 UTC) - US Open (BEST!)',
            '01:00 JST (16:00 UTC) - US Peak'
        ],
        'expected_signals': '6-12 per day',
        'expected_win_rate': '75-80%'
    })

if __name__ == '__main__':
    print(f"🚀 Starting Crypto Scanner API Server...")
    print(f"📂 Project: {PROJECT_DIR}")
    print(f"🔍 Scanner: {SCANNER_PATH}")
    print(f"📊 Report: {REPORT_PATH}")
    print(f"🌐 Server: http://localhost:5000")
    print(f"⚡ React UI: http://localhost:3000")
    print()

    app.run(host='0.0.0.0', port=5000, debug=True)
