from flask import Blueprint, render_template, request, jsonify
from routes.auth import login_required
from utils.db_handler import (
    get_all_faculty, get_all_attendance, create_chatbot_query,
    get_chatbot_queries, get_attendance_stats
)
import uuid
from datetime import datetime, date
import re
import sqlite3

chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')

@chatbot_bp.route('/')
@login_required
def interface():
    recent_queries = get_chatbot_queries()
    recent_queries = sorted(recent_queries, key=lambda x: x['timestamp'], reverse=True)[:10]
    return render_template('chatbot/interface.html', recent_queries=recent_queries)

@chatbot_bp.route('/ask', methods=['POST'])
@login_required
def ask():
    try:
        data = request.get_json()
        question = data.get('question', '').strip()

        if not question:
            return jsonify({'success': False, 'message': 'Please enter a question'})

        response = classic_chatbot_response(question)

        create_chatbot_query(question, response, datetime.now().isoformat())

        return jsonify({
            'success': True,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

def classic_chatbot_response(user_input):
    user_input = user_input.lower()
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()

    today = date.today()
    response = "Sorry, I didn't understand that. Try asking about attendance or reports."

    date_match = re.search(r"\d{4}-\d{2}-\d{2}", user_input)
    requested_date = date_match.group(0) if date_match else today.strftime("%Y-%m-%d")

    if user_input in ['hi', 'hello', 'hey', 'hai']:
        return "👋 Hello! How can I assist you with the Faculty Attendance System?"

    elif "register" in user_input and "faculty" in user_input:
        response = "To register a new faculty, go to the registration form in the dashboard."

    elif "list" in user_input and "faculty" in user_input:
        cursor.execute("SELECT name FROM faculty")
        faculty = cursor.fetchall()
        response = "Registered Faculty: " + ", ".join([f[0] for f in faculty]) if faculty else "No faculty registered yet."

    elif "attendance" in user_input and ("today" in user_input or date_match):
        cursor.execute("""
            SELECT name FROM faculty 
            WHERE faculty_id IN (
                SELECT faculty_id FROM attendance WHERE date = ?
            )
        """, (requested_date,))
        present = cursor.fetchall()
        response = f"🎯 Attendance on {requested_date}: " + ", ".join([f[0] for f in present]) if present else f"No attendance recorded for {requested_date}."

    elif "monthly report" in user_input or "this month" in user_input:
        month = today.strftime("%m")
        year = today.strftime("%Y")
        cursor.execute("""
            SELECT faculty.name, COUNT(*) 
            FROM attendance 
            JOIN faculty ON attendance.faculty_id = faculty.faculty_id 
            WHERE strftime('%m', date) = ? AND strftime('%Y', date) = ?
            GROUP BY faculty.faculty_id
        """, (month, year))
        data = cursor.fetchall()
        response = f"📅 Monthly Report ({today.strftime('%B %Y')}):\n" + "\n".join([f"{name}: {count} days" for name, count in data]) if data else "No attendance records for this month."
        
    # Yearly report
    elif "yearly report" in user_input or "this year" in user_input:
        year = today.strftime("%Y")
        cursor.execute("""
            SELECT faculty.name, COUNT(*) 
            FROM attendance 
            JOIN faculty ON attendance.faculty_id = faculty.faculty_id  
            WHERE strftime('%Y', date) = ?
            GROUP BY faculty.faculty_id
        """, (year,))
        data = cursor.fetchall()
        if data:
            report = "\n".join([f"{name}: {count} days" for name, count in data])
            response = f"📆 Yearly Report ({year}):\n{report}"
        else:
            response = "No attendance records for this year."

    # Absent today or on specific date
    elif "absent" in user_input and ("today" in user_input or date_match):
        cursor.execute("SELECT name FROM faculty")
        all_faculty = set(f[0] for f in cursor.fetchall())

        cursor.execute("""
            SELECT faculty.name 
            FROM attendance 
            JOIN faculty ON attendance.faculty_id = faculty.faculty_id 
            WHERE date = ?
        """, (requested_date,))
        present = set(f[0] for f in cursor.fetchall())

        absent = all_faculty - present
        if absent:
            response = f"🚫 Absent on {requested_date}: " + ", ".join(absent)
        else:
            response = f"✅ All faculty were present on {requested_date}."

    elif "report" in user_input:
        cursor.execute("SELECT COUNT(*) FROM attendance")
        total = cursor.fetchone()[0]
        response = f"📊 Total attendance records: {total}"

    conn.close()
    return response