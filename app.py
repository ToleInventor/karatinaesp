from flask import Flask, render_template, request, jsonify
from threading import Lock

app = Flask(__name__)

health_data_store = {}
store_lock = Lock()

@app.route('/post_health', methods=['POST'])
def post_health():
    """
    Receive real-time health data via JSON POST.
    Expected JSON payload:
    {
        "user_id": "user123",
        "bpm": 75,
        "sp02": 96,
        "temp": 24.5
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON payload"}), 400

    required_fields = ["user_id", "bpm", "sp02", "temp"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    user_id = str(data["user_id"])
    try:
        bpm = int(data["bpm"])
        sp02 = int(data["sp02"])
        temp = float(data["temp"])
    except ValueError:
        return jsonify({"error": "Invalid data types"}), 400

    with store_lock:
        health_data_store[user_id] = {
            "bpm": bpm,
            "sp02": sp02,
            "temp": temp
        }

    return jsonify({"status": "success", "message": f"Data stored for user {user_id}"}), 200

@app.route('/get_health/<user_id>', methods=['GET'])
def get_health(user_id):
    """
    Retrieve latest health data for a specific user.
    """
    with store_lock:
        data = health_data_store.get(user_id)

    if data:
        return jsonify({"user_id": user_id, **data}), 200
    else:
        return jsonify({"error": "User not found"}), 404

@app.route('/get_all_health', methods=['GET'])
def get_all_health():
    """
    Retrieve all stored health data.
    """
    with store_lock:
        return jsonify(health_data_store), 200

if __name__ == '__main__':
    # Runs on all interfaces for real-time access
    app.run(host='0.0.0.0', port=5000, debug=True)
