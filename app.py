from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import os
import json
from datetime import datetime
import threading
import time
from database import Database
from log_analyzer import LogAnalyzer
from email_notifier import EmailNotifier
from config_manager import ConfigManager

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)

db = Database()
config_manager = ConfigManager()
log_analyzer = None
monitoring_thread = None
monitoring_active = False


@app.route('/')
def index():
    lang = session.get('language', 'en')
    return render_template('index.html', lang=lang)


@app.route('/api/language', methods=['POST'])
def set_language():
    data = request.json
    session['language'] = data.get('language', 'en')
    return jsonify({'status': 'success'})


@app.route('/api/config', methods=['GET', 'POST'])
def handle_config():
    if request.method == 'GET':
        config = config_manager.get_config()
        return jsonify(config)
    else:
        data = request.json
        config_manager.update_config(data)
        return jsonify({'status': 'success'})


@app.route('/api/start-monitoring', methods=['POST'])
def start_monitoring():
    global log_analyzer, monitoring_thread, monitoring_active

    data = request.json
    log_paths = data.get('log_paths', [])

    if not log_paths:
        return jsonify({'status': 'error', 'message': 'No log paths provided'})

    config = config_manager.get_config()
    log_analyzer = LogAnalyzer(db, config)

    monitoring_active = True
    monitoring_thread = threading.Thread(
        target=monitor_logs,
        args=(log_paths, log_analyzer),
        daemon=True
    )
    monitoring_thread.start()

    return jsonify({'status': 'success'})


@app.route('/api/stop-monitoring', methods=['POST'])
def stop_monitoring():
    global monitoring_active
    monitoring_active = False
    return jsonify({'status': 'success'})


@app.route('/api/logs', methods=['GET'])
def get_logs():
    limit = request.args.get('limit', 50, type=int)
    logs = db.get_recent_logs(limit)
    return jsonify(logs)


@app.route('/api/log/<int:log_id>', methods=['GET'])
def get_log_detail(log_id):
    log = db.get_log_detail(log_id)
    if log:
        return jsonify(log)
    return jsonify({'error': 'Log not found'}), 404


@app.route('/api/stats', methods=['GET'])
def get_stats():
    stats = db.get_statistics()
    return jsonify(stats)


def monitor_logs(log_paths, analyzer):
    global monitoring_active
    file_positions = {path: 0 for path in log_paths}

    while monitoring_active:
        for log_path in log_paths:
            if not os.path.exists(log_path):
                continue

            try:
                with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                    f.seek(file_positions[log_path])
                    new_lines = f.readlines()
                    file_positions[log_path] = f.tell()

                    for line in new_lines:
                        if line.strip():
                            analyzer.analyze_log_line(line, log_path)
            except Exception as e:
                print(f"Error reading {log_path}: {e}")

        time.sleep(2)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)