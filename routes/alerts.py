from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from routes.auth import login_required
from twilio.rest import Client
from utils.db_handler import (
    get_all_faculty, insert_absentee_alert, create_absentee_alert,
    get_absentee_alerts, get_attendance_by_date,log_event
)
import uuid
from datetime import datetime, date
import os
import json
import csv
import io
from dotenv import load_dotenv

alerts_bp = Blueprint('alerts', __name__)

load_dotenv()  # loads .env into environment

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

logs_bp = Blueprint('logs', __name__, url_prefix='/logs')
alerts_bp = Blueprint('alerts', __name__, url_prefix='/alerts')

@alerts_bp.route('/')
def alert_home():
    return render_template('alert/history.html') 

@alerts_bp.route('/send_sms', methods=['POST'])
def send_sms_alert():
    data = request.get_json()
    name = data.get('name')
    phone = data.get('phone')
    date_ = data.get('date')
    faculty_id = data.get('faculty_id')

    if not all([name, phone, date_, faculty_id]):
        return jsonify({'message': 'Missing required fields'}), 400

    message_body = f"Dear {name}, you were marked absent on {date_}. Please contact administration."

    try:
        # Send SMS via Twilio
        message = client.messages.create(
            body=message_body,
            from_=TWILIO_PHONE_NUMBER,
            to=phone
        )

        # Store alert with status "Sent"
        insert_absentee_alert(
            faculty_id=faculty_id,
            date=date_,
            message=message_body,
            status="Sent"
        )

        log_event("application", f"SMS alert sent to {faculty_id} at {phone}")
        return jsonify({'message': f"SMS sent to {name} at {phone}", 'sid': message.sid})

    except Exception as e:
        # Log and store alert with "Failed" status
        insert_absentee_alert(
            faculty_id=faculty_id,
            date=date_,
            message=message_body,
            status="Failed: " + str(e)
        )

        log_event("error", f"Failed to send SMS alert to {faculty_id}: {e}")
        return jsonify({'message': f"Failed to send SMS: {str(e)}"}), 500
    

@alerts_bp.route('/send-absentee-alerts', methods=['POST'])
@login_required
def send_absentee_alerts():
    try:
        target_date = request.form.get('target_date') or date.today().strftime('%Y-%m-%d')
        absent_faculty = get_absent_faculty(target_date)

        if not absent_faculty:
            flash(f'No absent faculty found for {target_date}', 'info')
            return redirect(url_for('alerts.send'))

        sent_count, failed_count = 0, 0
        failed_logs = []

        for faculty in absent_faculty:
            try:
                success = simulate_send_alert(faculty, target_date)
                if success:
                    create_absentee_alert({
                        'alert_id': str(uuid.uuid4()),
                        'faculty_id': faculty['faculty_id'],
                        'date': target_date,
                        'message_sent': True
                    })
                    sent_count += 1
                else:
                    failed_logs.append(faculty['name'])
                    failed_count += 1
            except Exception as e:
                failed_logs.append(f"{faculty['name']} - {str(e)}")
                failed_count += 1

        if sent_count > 0:
            flash(f'Successfully sent alerts to {sent_count} faculty members', 'success')
        if failed_count > 0:
            flash(f'Failed to send alerts to {failed_count} faculty members', 'warning')
            log_failed_alerts(failed_logs, target_date)

        return redirect(url_for('alerts.send'))

    except Exception as e:
        flash(f'Error sending alerts: {str(e)}', 'danger')
        return redirect(url_for('alerts.send'))

@alerts_bp.route('/api/get-absent-faculty')
@login_required
def api_get_absent_faculty():
    target_date = request.args.get('date', date.today().strftime('%Y-%m-%d'))
    format_type = request.args.get('format', '').lower()
    absent_faculty = get_absent_faculty(target_date)

    if format_type == 'csv':
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=['faculty_id', 'name', 'department', 'email', 'phone'])
        writer.writeheader()
        for f in absent_faculty:
            writer.writerow({
                'faculty_id': f['faculty_id'],
                'name': f['name'],
                'department': f['department'],
                'email': f['email'],
                'phone': f.get('phone', 'N/A')
            })
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'absent_faculty_{target_date}.csv'
        )

    return jsonify({
        'date': target_date,
        'absent_count': len(absent_faculty),
        'absent_faculty': [
            {
                'faculty_id': f['faculty_id'],
                'name': f['name'],
                'department': f['department'],
                'email': f['email'],
                'phone': f.get('phone', 'N/A')
            } for f in absent_faculty
        ]
    })

@alerts_bp.route('/history')
@login_required
def history():
    alerts = get_absentee_alerts()
    all_faculty = get_all_faculty()
    faculty_map = {f['faculty_id']: f for f in all_faculty}

    enriched_alerts = []
    for alert in alerts:
        faculty = faculty_map.get(alert['faculty_id'])
        if faculty:
            enriched_alert = alert.copy()
            enriched_alert.update({
                'faculty_name': faculty['name'],
                'department': faculty['department'],
                'email': faculty['email']
            })
            enriched_alerts.append(enriched_alert)

    enriched_alerts.sort(key=lambda x: x['date'], reverse=True)
    return render_template('alerts/history.html', alerts=enriched_alerts)

# -------------------------------
# Utility Functions
# -------------------------------

def get_absent_faculty(target_date):
    all_faculty = get_all_faculty()
    attendance_records = get_attendance_by_date(target_date)
    present_faculty_ids = {record['faculty_id'] for record in attendance_records}
    return [faculty for faculty in all_faculty if faculty['faculty_id'] not in present_faculty_ids]

def simulate_send_alert(faculty, date):
    try:
        print(f"📧 ALERT SENT TO: {faculty['name']} ({faculty['email']})")
        print(f"   Subject: Attendance Alert - {date}")
        print(f"   Message: You were marked absent on {date}. Please contact administration if this is incorrect.")

        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'faculty_id': faculty['faculty_id'],
            'faculty_name': faculty['name'],
            'email': faculty['email'],
            'date': date,
            'type': 'absence_alert',
            'status': 'sent'
        }

        alerts_dir = os.path.join('uploads', 'alerts')
        os.makedirs(alerts_dir, exist_ok=True)
        log_file = os.path.join(alerts_dir, f"{date}-alerts.json")

        logs = []
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                try:
                    logs = json.load(f)
                except:
                    logs = []

        logs.append(log_entry)

        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)

        return True
    except Exception as e:
        print(f"Failed to send alert: {str(e)}")
        return False

def log_failed_alerts(failed_list, date):
    log_dir = os.path.join('uploads', 'alerts')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"{date}-failed.json")

    with open(log_file, 'w') as f:
        json.dump({'failed_alerts': failed_list, 'date': date}, f, indent=2)

# Optional: Real email sending function (secure placeholder)
def send_real_email(faculty, date):
    """
    Replace simulate_send_alert with this to enable real emails
    Requires:
    - SMTP_SERVER
    - SMTP_PORT
    - SMTP_USERNAME
    - SMTP_PASSWORD
    - FROM_EMAIL
    """
    pass

# Optional: Scheduling alert sender
def schedule_daily_alerts(app):
    """Optional: Schedule daily absentee alert sending at 10 AM"""
    from apscheduler.schedulers.background import BackgroundScheduler

    def job():
        with app.app_context():
            today = date.today().strftime('%Y-%m-%d')
            print(f"Running scheduled alert for {today}")
            absent_faculty = get_absent_faculty(today)
            for faculty in absent_faculty:
                simulate_send_alert(faculty, today)
                create_absentee_alert({
                    'alert_id': str(uuid.uuid4()),
                    'faculty_id': faculty['faculty_id'],
                    'date': today,
                    'message_sent': True
                })

    scheduler = BackgroundScheduler()
    scheduler.add_job(job, 'cron', hour=10, minute=0)
    scheduler.start()