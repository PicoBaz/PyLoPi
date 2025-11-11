import sqlite3
import json
from datetime import datetime
import threading


class Database:
    def __init__(self, db_path='pylopi.db'):
        self.db_path = db_path
        self.lock = threading.Lock()
        self.init_database()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    log_file TEXT NOT NULL,
                    error_type TEXT NOT NULL,
                    error_message TEXT NOT NULL,
                    full_log TEXT NOT NULL,
                    analysis TEXT,
                    solution TEXT,
                    code_fix TEXT,
                    severity TEXT DEFAULT 'medium',
                    status TEXT DEFAULT 'new'
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            ''')

            conn.commit()
            conn.close()

    def insert_log(self, log_data):
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO logs (log_file, error_type, error_message, full_log,
                                analysis, solution, code_fix, severity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                log_data['log_file'],
                log_data['error_type'],
                log_data['error_message'],
                log_data['full_log'],
                log_data.get('analysis', ''),
                log_data.get('solution', ''),
                log_data.get('code_fix', ''),
                log_data.get('severity', 'medium')
            ))

            log_id = cursor.lastrowid
            conn.commit()
            conn.close()

            return log_id

    def get_recent_logs(self, limit=50):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, timestamp, log_file, error_type, error_message,
                   LEFT(analysis, 200) as short_analysis, severity, status
            FROM logs
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))

        logs = []
        for row in cursor.fetchall():
            logs.append({
                'id': row['id'],
                'timestamp': row['timestamp'],
                'log_file': row['log_file'],
                'error_type': row['error_type'],
                'error_message': row['error_message'],
                'short_analysis': row['short_analysis'],
                'severity': row['severity'],
                'status': row['status']
            })

        conn.close()
        return logs

    def get_log_detail(self, log_id):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM logs WHERE id = ?
        ''', (log_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'id': row['id'],
                'timestamp': row['timestamp'],
                'log_file': row['log_file'],
                'error_type': row['error_type'],
                'error_message': row['error_message'],
                'full_log': row['full_log'],
                'analysis': row['analysis'],
                'solution': row['solution'],
                'code_fix': row['code_fix'],
                'severity': row['severity'],
                'status': row['status']
            }
        return None

    def get_statistics(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) as total FROM logs')
        total = cursor.fetchone()['total']

        cursor.execute('''
            SELECT error_type, COUNT(*) as count
            FROM logs
            GROUP BY error_type
            ORDER BY count DESC
            LIMIT 5
        ''')
        top_errors = [dict(row) for row in cursor.fetchall()]

        cursor.execute('''
            SELECT severity, COUNT(*) as count
            FROM logs
            GROUP BY severity
        ''')
        by_severity = [dict(row) for row in cursor.fetchall()]

        cursor.execute('''
            SELECT COUNT(*) as count
            FROM logs
            WHERE date(timestamp) = date('now')
        ''')
        today_count = cursor.fetchone()['count']

        conn.close()

        return {
            'total_logs': total,
            'today_count': today_count,
            'top_errors': top_errors,
            'by_severity': by_severity
        }

    def update_setting(self, key, value):
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO settings (key, value)
                VALUES (?, ?)
            ''', (key, json.dumps(value)))

            conn.commit()
            conn.close()

    def get_setting(self, key, default=None):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return json.loads(row['value'])
        return default