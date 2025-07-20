from flask import Blueprint, jsonify, render_template
from routes.auth import login_required
from utils.db_handler import fetch_logs_by_category, get_connection

logs_bp = Blueprint('logs', __name__, url_prefix='/logs')

@logs_bp.route('/')
def logs_home():
    return render_template('system/logs.html')

@logs_bp.route('/get_logs')
def get_logs():
    logs = fetch_logs_by_category()  # Get all logs
    results = []
    for log in logs:
        results.append({
            "timestamp": log[1],
            "level": log[2],
            "category": log[3],
            "message": log[4]
        })
    return jsonify(results)

@logs_bp.route('/clear', methods=['POST'])
def clear_all_logs():
    try:
        with get_connection() as conn:
            conn.execute('DELETE FROM system_logs')
            conn.commit()
        return jsonify({'message': 'Logs cleared successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500