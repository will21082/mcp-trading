import httpx

body = {"exchanges": ["bybit"], "timeframes": ["15m"], "min_confidence": 5}

print("=== Scan 1 (fresh) ===")
r1 = httpx.post("http://localhost:8000/api/scan", json=body, timeout=60)
d1 = r1.json()
print(f"  total_signals={d1['total_signals']}, from_cache={d1.get('_from_cache')}")

print("\n=== Scan 2 (immediate - should be cached) ===")
r2 = httpx.post("http://localhost:8000/api/scan", json=body, timeout=60)
d2 = r2.json()
print(f"  total_signals={d2['total_signals']}, from_cache={d2.get('_from_cache')}")
print(f"  notice={d2.get('_notice', 'none')}")

print("\n=== Scan 3 (immediate - should be cached) ===")
r3 = httpx.post("http://localhost:8000/api/scan", json=body, timeout=60)
d3 = r3.json()
print(f"  total_signals={d3['total_signals']}, from_cache={d3.get('_from_cache')}")
print(f"  notice={d3.get('_notice', 'none')}")
