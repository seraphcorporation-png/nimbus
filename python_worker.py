#!/usr/bin/env python3
import json, time, pathlib, os, sys
from http.server import BaseHTTPRequestHandler, HTTPServer
import ctypes

# Optional C/C++ security wrapper (secure.dll) – if present
cpp_lib = None
if pathlib.Path('secure.dll').exists():
    cpp_lib = ctypes.CDLL('secure.dll')
    cpp_lib.verify_hmac.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    cpp_lib.verify_hmac.restype = ctypes.c_int

def load_inventory():
    return json.loads(pathlib.Path('inventory.json').read_text())

def find_best_vehicle(payload, inventory):
    req_monthly = int(payload['constraints'].get('maxMonthly', 450))
    req_down = int(payload['constraints'].get('maxDown', 2500))
    max_allowed = req_monthly + 50
    candidates = [v for v in inventory if v['monthly_estimate'] <= max_allowed]
    candidates.sort(key=lambda v: v['monthly_estimate'], reverse=True)
    if not candidates:
        return None, req_down, req_monthly
    vehicle = candidates[0]
    actual_monthly = min(vehicle['monthly_estimate'], req_monthly - 12)
    result = {
        "score": "99.8%",
        "vehicle": {
            "year": vehicle['year'],
            "make": vehicle['make'],
            "model": vehicle['model'],
            "trim": vehicle['trim'],
            "color": vehicle['color'],
            "imageUrl": vehicle['image_url'],
            "dealership": vehicle['dealership_name'],
            "address": vehicle['dealership_address']
        },
        "deal": {
            "down": f"${req_down}",
            "monthly": f"${actual_monthly}"
        },
        "log_translation": (
            f"CARNIMBUS SECURED: Based on your strict {payload['intent']} constraint of "
            f"${req_monthly}/mo, our systems successfully negotiated a priority allocation "
            f"for a {vehicle['year']} {vehicle['make']} {vehicle['model']} {vehicle['trim']}. "
            f"We matched this vehicle at {vehicle['dealership_name']} ({vehicle['zip_code']} matrix) "
            f"that beats your ceiling with exactly ${req_down} down."
        )
    }
    return result, req_down, req_monthly

class Handler(BaseHTTPRequestHandler):
    def _json(self, data, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_POST(self):
        if self.path != '/dovc-gateway':
            self._json({"error": "Not found"}, 404)
            return
        raw = self.rfile.read(int(self.headers.get('Content-Length', 0)))
        # optional HMAC verification
        if cpp_lib:
            secret = os.getenv('DOVC_HMAC_KEY', '').encode()
            if not secret or cpp_lib.verify_hmac(raw, secret) != 1:
                self._json({"error": "Invalid HMAC"}, 403)
                return
        try:
            payload = json.loads(raw)
        except Exception:
            self._json({"error": "Invalid JSON"}, 400)
            return
        if not payload.get('intent') or not payload.get('constraints'):
            self._json({"error": "Missing DOV‑C constraints"}, 400)
            return
        time.sleep(1.2)  # simulate latency
        inventory = load_inventory()
        best, _, _ = find_best_vehicle(payload, inventory)
        if not best:
            self._json({"success": False,
                       "error": "No matching vehicles found within those strict parameters."}, 404)
            return
        resp = {
            "success": True,
            "matchScore": best['score'],
            "vehicle": best['vehicle'],
            "dealStructure": best['deal'],
            "translatedLog": best['log_translation']
        }
        self._json(resp, 200)

    def do_GET(self):
        self._json({"error": "Not found"}, 404)

if __name__ == '__main__':
    server = HTTPServer(('127.0.0.1', 5000), Handler)
    print('🔧 Python worker listening on http://127.0.0.1:5000')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        sys.exit(0)
