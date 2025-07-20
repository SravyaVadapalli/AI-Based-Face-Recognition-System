from flask import Blueprint, render_template, request, flash, jsonify
from routes.auth import login_required
from utils.face_recognition import recognize_faces
from utils.db_handler import (
    get_all_attendance, create_attendance,
    get_attendance_by_faculty, get_faculty_by_id, get_all_faculty, get_attendance_by_date
)
from utils.db_handler import get_attendance_by_date
import uuid
from datetime import datetime, date

attendance_bp = Blueprint('attendance', __name__, url_prefix='/attendance')


@attendance_bp.route('/capture', methods=['GET', 'POST'])
@login_required
def capture():
    if request.method == 'POST':
        captured_image = request.files.get('captured_image')
        location = request.form.get('location', 'Unknown')
        faculty_id = request.form.get('faculty_id')  # optional in real use

        if not captured_image:
            return jsonify({'success': False, 'message': 'No image uploaded'}), 400

        current_date = date.today().strftime('%Y-%m-%d')
        current_time = datetime.now().strftime('%H:%M:%S')

        existing_today = get_attendance_by_date(current_date)
        existing_ids = {r['faculty_id'] for r in existing_today}

        try:
            recognized_faculty_ids = recognize_faces(captured_image)
            print("📸 Recognized faculty IDs:", recognized_faculty_ids)

            if not recognized_faculty_ids:
                return jsonify({'success': False, 'message': 'No known faces recognized'}), 404

            matched_id = None
            if faculty_id and faculty_id in recognized_faculty_ids:
                matched_id = faculty_id
            elif not faculty_id and len(recognized_faculty_ids) == 1:
                matched_id = recognized_faculty_ids[0]

            if not matched_id:
                return jsonify({'success': False, 'message': 'Face does not match any faculty'}), 403

            if matched_id in existing_ids:
                return jsonify({'success': True, 'message': 'Already marked present'}), 200

            faculty = get_faculty_by_id(matched_id)
            if not faculty:
                return jsonify({'success': False, 'message': 'Faculty not found'}), 404

            attendance_data = {
                'faculty_id': matched_id,
                'date': current_date,
                'time': current_time,
                'location': location,
                'status': 'Present'
            }

            if create_attendance(attendance_data):
                return jsonify({
                    'success': True,
                    'message': f"Attendance marked for {faculty['name']}",
                    'data': {
                        'faculty_id': matched_id,
                        'faculty_name': faculty['name'],
                        'time': current_time,
                        'location': location
                    }
                }), 200
            else:
                return jsonify({'success': False, 'message': 'Failed to save attendance'}), 500

        except Exception as e:
            return jsonify({'success': False, 'message': f"Error during recognition: {str(e)}"}), 500

    return render_template('attendance/capture.html')

@attendance_bp.route('/mark', methods=['POST'])
def mark():
    try:
        faculty_id = request.form.get('faculty_id')
        image_file = request.files.get('image')
        location = request.form.get('location', 'Unknown')

        if not image_file or not faculty_id:
            return jsonify({'success': False, 'message': 'Missing image or faculty ID'}), 400

        # ✅ Step 1: Recognize face from image
        recognized_ids = recognize_faces(image_file)

        if not recognized_ids:
            return jsonify({'success': False, 'message': 'No face recognized!'}), 400

        # ✅ Step 2: Face must match the entered Faculty ID
        if faculty_id not in recognized_ids:
            return jsonify({'success': False, 'message': '❌ Face does not match the Faculty ID!'}), 400

        # ✅ Step 3: Prevent double marking
        current_date = date.today().strftime('%Y-%m-%d')
        current_time = datetime.now().strftime('%H:%M:%S')
        existing_today = get_attendance_by_date(current_date)
        existing_ids = {r['faculty_id'] for r in existing_today}

        if faculty_id in existing_ids:
            return jsonify({'success': True, 'message': '⚠️ Attendance already marked today!'}), 200

        # ✅ Step 4: Validate faculty ID exists in DB
        faculty = get_faculty_by_id(faculty_id)
        if not faculty:
            return jsonify({'success': False, 'message': 'Invalid Faculty ID'}), 404

        # ✅ Step 5: Save attendance
        attendance_data = {
            'faculty_id': faculty_id,
            'date': current_date,
            'time': current_time,
            'location': location,
            'status': 'Present'
        }

        if create_attendance(attendance_data):
            return jsonify({
                'success': True,
                'message': f'✅ Attendance marked successfully for {faculty["name"]}.',
                'data': {
                    'faculty_name': faculty["name"],
                    'time': current_time,
                    'location': location
                }
            }), 200
        else:
            return jsonify({'success': False, 'message': 'Failed to mark attendance.'}), 500

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@attendance_bp.route('/logs')
@login_required
def logs():
    date_filter = request.args.get('date')
    faculty_filter = request.args.get('faculty_id')
    status_filter = request.args.get('status')

    attendance_records = get_all_attendance()

    if date_filter:
        attendance_records = [r for r in attendance_records if r['date'] == date_filter]

    if faculty_filter:
        attendance_records = [r for r in attendance_records if r['faculty_id'] == faculty_filter]

    if status_filter:
        attendance_records = [r for r in attendance_records if r['status'] == status_filter]

    faculty_list = get_all_faculty()
    faculty_map = {f['faculty_id']: f for f in faculty_list}

    enriched_records = []
    for record in attendance_records:
        faculty = faculty_map.get(record['faculty_id'])
        if faculty:
            enriched = record.copy()
            enriched['faculty_name'] = faculty['name']
            enriched['department'] = faculty['department']
            enriched_records.append(enriched)

    enriched_records.sort(key=lambda x: f"{x['date']} {x['time']}", reverse=True)

    return render_template('attendance/logs.html',
                           attendance_records=enriched_records,
                           faculty_list=faculty_list,
                           filters={
                               'date': date_filter,
                               'faculty_id': faculty_filter,
                               'status': status_filter
                           })


@attendance_bp.route('/api/today-summary')
@login_required
def api_today_summary():
    today = date.today().strftime('%Y-%m-%d')
    today_records = get_attendance_by_date(today)

    total_faculty = len(get_all_faculty())
    present_count = len(today_records)
    absent_count = total_faculty - present_count

    return jsonify({
        'total_faculty': total_faculty,
        'present': present_count,
        'absent': absent_count,
        'date': today
    })


@attendance_bp.route('/liveattendance')
def live_attendance():
    return render_template('liveattendance.html')