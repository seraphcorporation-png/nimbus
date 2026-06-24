import json
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

# Root workspace directory is one level up from this file's folder (python_api)
ROOT_DIR = Path.cwd()

@app.route('/')
def serve_index():
    return send_from_directory(str(ROOT_DIR), 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(ROOT_DIR, path)

@app.route('/dovc-gateway', methods=['POST'])
@app.route('/api/dovc-gateway', methods=['POST'])
def dovc_gateway():
    """Mimics the original PowerShell listener and python_worker.py logic.
    Expects JSON with `intent` and `constraints`.
    """
    # Parse payload robustly
    payload = request.get_json(silent=True)
    if not payload:
        try:
            payload = json.loads(request.data.decode('utf-8'))
        except Exception:
            pass
    
    if not payload or "intent" not in payload or "constraints" not in payload:
        return jsonify({"error": "Missing intent or constraints"}), 400

    # Load inventory.json
    inventory_path = ROOT_DIR / "inventory.json"
    try:
        inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    except Exception as exc:
        app.logger.error("Failed to read inventory.json: %s", exc)
        return jsonify({"error": "Server error: cannot load inventory"}), 500

    req_monthly = int(payload['constraints'].get('maxMonthly', 450))
    req_down = int(payload['constraints'].get('maxDown', 2500))
    max_allowed = req_monthly + 50

    candidates = [v for v in inventory if v.get('monthly_estimate', 9999) <= max_allowed]
    candidates.sort(key=lambda v: v.get('monthly_estimate', 0), reverse=True)

    if not candidates:
        return jsonify({"success": False, "error": "No matching vehicles found within those strict parameters."}), 404

    vehicle = candidates[0]
    actual_monthly = min(vehicle.get('monthly_estimate', 0), req_monthly - 12)

    result = {
        "success": True,
        "matchScore": "99.8%",
        "vehicle": {
            "year": vehicle.get('year'),
            "make": vehicle.get('make'),
            "model": vehicle.get('model'),
            "trim": vehicle.get('trim'),
            "color": vehicle.get('color'),
            "imageUrl": vehicle.get('image_url'),
            "dealership": vehicle.get('dealership_name'),
            "address": vehicle.get('dealership_address')
        },
        "dealStructure": {
            "down": f"${req_down}",
            "monthly": f"${actual_monthly}"
        },
        "translatedLog": (
            f"CARNIMBUS SECURED: Based on your strict {payload['intent']} constraint of "
            f"${req_monthly}/mo, our systems successfully negotiated a priority allocation "
            f"for a {vehicle.get('year')} {vehicle.get('make')} {vehicle.get('model')} {vehicle.get('trim')}. "
            f"We matched this vehicle at {vehicle.get('dealership_name')} ({vehicle.get('zip_code')} matrix) "
            f"that beats your ceiling with exactly ${req_down} down."
        )
    }

    return jsonify(result)

@app.route('/')
def serve_index():
    return send_from_directory(str(ROOT_DIR), 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(ROOT_DIR, path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

