import sqlite3
from werkzeug.security import generate_password_hash
import os
import uuid
from datetime import date, datetime
from typing import List, Dict

def get_connection(db_path=None):
    if db_path is None:
        db_path = 'attendance.db'
    return sqlite3.connect(db_path)


def initialize_data_files(db_path='attendance.db'):
    """Initialize all required tables."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                admin_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS faculty (
                faculty_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                department TEXT,
                email TEXT,
                phone TEXT,
                password_hash TEXT,
                face_embedding BLOB,
                registered_on TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                faculty_id TEXT,
                date TEXT,
                time TEXT,
                location TEXT,
                status TEXT,
                recorded_on TEXT,
                FOREIGN KEY(faculty_id) REFERENCES faculty(faculty_id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS absentee_alerts (
                alert_id TEXT PRIMARY KEY,
                faculty_id TEXT,
                date TEXT,
                message TEXT,
                status TEXT,
                sent_time TEXT,
                FOREIGN KEY(faculty_id) REFERENCES faculty(faculty_id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                level TEXT,
                category TEXT,
                message TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chatbot_queries (
                id TEXT PRIMARY KEY,
                question TEXT,
                response TEXT,
                timestamp TEXT
            )
        ''')

        cursor.execute("SELECT COUNT(*) FROM admins WHERE username = 'admin'")
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO admins (admin_id, username, password_hash, email)
                VALUES (?, ?, ?, ?)
            ''', (
                'ADMIN001',
                'admin',
                generate_password_hash('admin123'),
                'admin@faculty-system.com'
            ))

        conn.commit()

# ========== FACULTY FUNCTIONS ==========
def get_all_faculty(db_path='attendance.db') -> List[Dict]:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM faculty")
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

def get_faculty_by_id(faculty_id, db_path='attendance.db') -> Dict:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM faculty WHERE faculty_id = ?", (faculty_id,))
        row = cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None

def create_faculty(faculty_data: Dict, db_path='attendance.db') -> bool:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO faculty (
                faculty_id, name, department, email, phone,
                password_hash, face_embedding, registered_on
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            faculty_data['faculty_id'],
            faculty_data['name'],
            faculty_data.get('department', ''),
            faculty_data.get('email', ''),
            faculty_data.get('phone', ''),
            faculty_data['password_hash'],
            sqlite3.Binary(faculty_data['face_embedding']),
            faculty_data['registered_on']
        ))
        conn.commit()
        return True

def update_faculty(faculty_id: str, updated_data: Dict, db_path='attendance.db') -> bool:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        fields = []
        values = []
        for key, value in updated_data.items():
            fields.append(f"{key} = ?")
            values.append(value)
        values.append(faculty_id)
        cursor.execute(f'''
            UPDATE faculty SET {", ".join(fields)} WHERE faculty_id = ?
        ''', values)
        conn.commit()
        return cursor.rowcount > 0

def delete_faculty(faculty_id: str, db_path='attendance.db') -> bool:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM faculty WHERE faculty_id = ?", (faculty_id,))
        conn.commit()
        return cursor.rowcount > 0

def get_faculty_count(db_path='attendance.db') -> int:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM faculty")
        return cursor.fetchone()[0]

# ========== SYSTEM LOGS ==========
def log_event(level, message, category="application", db_path='attendance.db'):
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute('''
                INSERT INTO system_logs (timestamp, level, category, message)
                VALUES (?, ?, ?, ?)
            ''', (timestamp, level, category, message))
            conn.commit()
    except Exception as e:
        print(f"Logging failed: {e}")

def fetch_logs_by_category(category=None, db_path='attendance.db'):
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            if category:
                cursor.execute('SELECT * FROM system_logs WHERE category=? ORDER BY id DESC', (category,))
            else:
                cursor.execute('SELECT * FROM system_logs ORDER BY id DESC')
            return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching logs: {e}")
        return []

# ========== ATTENDANCE ==========
def get_all_attendance(db_path='attendance.db') -> List[Dict]:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM attendance")
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

def create_attendance(attendance_data: Dict, db_path='attendance.db') -> bool:
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO attendance (faculty_id, date, time, location, status, recorded_on)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                attendance_data['faculty_id'],
                attendance_data['date'],
                attendance_data['time'],
                attendance_data['location'],
                attendance_data['status'],
                attendance_data.get('recorded_on', datetime.now().isoformat())
            ))
            conn.commit()
            return True
    except Exception as e:
        print(f"Error creating attendance: {e}")
        return False

def get_attendance_by_faculty(faculty_id: str, db_path='attendance.db') -> List[Dict]:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM attendance WHERE faculty_id = ?", (faculty_id,))
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

def get_attendance_by_date(date, db_path='attendance.db') -> List[Dict]:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM attendance WHERE date = ?", (date,))
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

def get_attendance_stats(db_path='attendance.db') -> Dict[str, int]:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        today = date.today().strftime('%Y-%m-%d')

        cursor.execute("SELECT COUNT(*) FROM faculty")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM attendance WHERE date = ?", (today,))
        present = cursor.fetchone()[0]

        absent = total - present

        return {
            'total_faculty': total,
            'present': present,
            'absent': absent,
            'date': today
        }

# ========== CHATBOT ==========
def create_chatbot_query(question, response, timestamp):
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO chatbot_queries (id, question, response, timestamp)
        VALUES (?, ?, ?, ?)
    """, (str(uuid.uuid4()), question, response, timestamp))
    conn.commit()
    conn.close()

def get_chatbot_queries():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT question, response, timestamp FROM chatbot_queries")
        rows = cursor.fetchall()
        return [{'question': q, 'response': r, 'timestamp': t} for q, r, t in rows]

# ========== ABSENTEE ALERT ==========
def create_absentee_alert(alert_data, db_path='attendance.db'):
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO absentee_alerts (alert_id, faculty_id, date, message, status, sent_time)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                alert_data['alert_id'],
                alert_data['faculty_id'],
                alert_data['date'],
                alert_data['message'],
                alert_data['status'],
                alert_data['sent_time']
            ))
            conn.commit()
            return True
    except Exception as e:
        print(f"Error creating absentee alert: {e}")
        return False

def insert_absentee_alert(faculty_id, date, message, status="Pending"):
    alert_id = str(uuid.uuid4())
    sent_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO absentee_alerts (alert_id, faculty_id, date, message, status, sent_time)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (alert_id, faculty_id, date, message, status, sent_time))
            conn.commit()
        return alert_id
    except Exception as e:
        print(f"Error inserting absentee alert: {e}")
        return None

def get_absentee_alerts(db_path='attendance.db'):
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    f.name AS faculty,
                    f.department,
                    f.phone,
                    a.date,
                    a.status,
                    a.sent_time
                FROM absentee_alerts a
                JOIN faculty f ON a.faculty_id = f.faculty_id
                ORDER BY a.date DESC
            ''')
            rows = cursor.fetchall()
            keys = [description[0] for description in cursor.description]
            return [dict(zip(keys, row)) for row in rows]
    except Exception as e:
        print(f"Error fetching absentee alerts: {e}")
        return []

# ========== ADMIN ==========
def create_admin(admin_data: dict, db_path='attendance.db') -> bool:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO admins (admin_id, username, password_hash, email)
            VALUES (?, ?, ?, ?)
        ''', (
            admin_data['admin_id'],
            admin_data['username'],
            admin_data['password_hash'],
            admin_data['email']
        ))
        conn.commit()
        return True

def reset_absentee_alerts_table(db_path='attendance.db'):
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS absentee_alerts")
        cursor.execute('''
            CREATE TABLE absentee_alerts (
                alert_id TEXT PRIMARY KEY,
                faculty_id TEXT,
                date TEXT,
                message TEXT,
                status TEXT,
                sent_time TEXT,
                FOREIGN KEY(faculty_id) REFERENCES faculty(faculty_id)
            )
        ''')
        conn.commit()
        print("✅ absentee_alerts table reset successfully.")