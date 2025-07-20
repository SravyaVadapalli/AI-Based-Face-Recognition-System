from flask import Blueprint, render_template, jsonify
from routes.auth import login_required
from utils.db_handler import (
    get_all_faculty, get_all_attendance, get_attendance_by_date,
    get_faculty_count, get_attendance_stats
)
from datetime import date, datetime, timedelta
from collections import defaultdict, Counter
import calendar

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/logs')
def show_logs():
    return render_template('system/logs.html')

@dashboard_bp.route('/')
@login_required
def admin_dashboard():
    # Get basic stats
    total_faculty = get_faculty_count()
    today = date.today().strftime('%Y-%m-%d')
    today_attendance = get_attendance_by_date(today)
    present_today = len(today_attendance)
    absent_today = total_faculty - present_today
    
    # Get recent attendance records
    all_attendance = get_all_attendance()
    recent_attendance = sorted(all_attendance, 
                              key=lambda x: f"{x['date']} {x['time']}", 
                              reverse=True)[:10]
    
    # Enrich with faculty info
    faculty_map = {f['faculty_id']: f for f in get_all_faculty()}
    for record in recent_attendance:
        faculty = faculty_map.get(record['faculty_id'])
        if faculty:
            record['faculty_name'] = faculty['name']
            record['department'] = faculty['department']
    
    # Calculate attendance percentage for this month
    current_month = date.today().replace(day=1)
    month_attendance = [r for r in all_attendance if r['date'].startswith(current_month.strftime('%Y-%m'))]
    
    # Get department-wise stats
    departments = defaultdict(int)
    for faculty in get_all_faculty():
        departments[faculty['department']] += 1
    
    stats = {
        'total_faculty': total_faculty,
        'present_today': present_today,
        'absent_today': absent_today,
        'attendance_percentage': round((present_today / total_faculty * 100) if total_faculty > 0 else 0, 1),
        'departments': dict(departments),
        'month_records': len(month_attendance)
    }
    
    return render_template('dashboard/index.html', 
                         stats=stats, 
                         recent_attendance=recent_attendance)

@dashboard_bp.route('/api/weekly-stats')
@login_required
def api_weekly_stats():
    """API endpoint for weekly attendance statistics"""
    end_date = date.today()
    start_date = end_date - timedelta(days=6)  # Last 7 days
    
    all_attendance = get_all_attendance()
    total_faculty = get_faculty_count()
    
    weekly_data = []
    current_date = start_date
    
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        day_attendance = [r for r in all_attendance if r['date'] == date_str]
        present_count = len(day_attendance)
        
        weekly_data.append({
            'date': date_str,
            'day': current_date.strftime('%a'),
            'present': present_count,
            'absent': total_faculty - present_count,
            'percentage': round((present_count / total_faculty * 100) if total_faculty > 0 else 0, 1)
        })
        
        current_date += timedelta(days=1)
    
    return jsonify(weekly_data)

@dashboard_bp.route('/api/monthly-stats')
@login_required
def api_monthly_stats():
    """API endpoint for monthly attendance statistics"""
    current_month = date.today().replace(day=1)
    all_attendance = get_all_attendance()
    total_faculty = get_faculty_count()
    
    # Get this month's data
    month_attendance = [r for r in all_attendance 
                       if r['date'].startswith(current_month.strftime('%Y-%m'))]
    
    # Group by date
    daily_counts = defaultdict(int)
    for record in month_attendance:
        daily_counts[record['date']] += 1
    
    # Get number of days in current month
    _, days_in_month = calendar.monthrange(current_month.year, current_month.month)
    
    monthly_data = []
    for day in range(1, days_in_month + 1):
        check_date = current_month.replace(day=day)
        date_str = check_date.strftime('%Y-%m-%d')
        
        # Only include past dates and today
        if check_date <= date.today():
            present_count = daily_counts.get(date_str, 0)
            monthly_data.append({
                'date': date_str,
                'day': day,
                'present': present_count,
                'absent': total_faculty - present_count,
                'percentage': round((present_count / total_faculty * 100) if total_faculty > 0 else 0, 1)
            })
    
    return jsonify(monthly_data)

@dashboard_bp.route('/api/department-stats')
@login_required
def api_department_stats():
    """API endpoint for department-wise attendance statistics"""
    all_faculty = get_all_faculty()
    all_attendance = get_all_attendance()
    today = date.today().strftime('%Y-%m-%d')
    
    # Get today's attendance
    today_attendance = [r for r in all_attendance if r['date'] == today]
    present_faculty_ids = {r['faculty_id'] for r in today_attendance}
    
    # Group faculty by department
    dept_stats = defaultdict(lambda: {'total': 0, 'present': 0})
    
    for faculty in all_faculty:
        dept = faculty['department']
        dept_stats[dept]['total'] += 1
        if faculty['faculty_id'] in present_faculty_ids:
            dept_stats[dept]['present'] += 1
    
    # Convert to list format for charts
    department_data = []
    for dept, stats in dept_stats.items():
        absent = stats['total'] - stats['present']
        percentage = round((stats['present'] / stats['total'] * 100) if stats['total'] > 0 else 0, 1)
        
        department_data.append({
            'department': dept,
            'total': stats['total'],
            'present': stats['present'],
            'absent': absent,
            'percentage': percentage
        })
    
    return jsonify(department_data)

@dashboard_bp.route('/api/attendance-trends')
@login_required
def api_attendance_trends():
    """API endpoint for attendance trends over time"""
    all_attendance = get_all_attendance()
    total_faculty = get_faculty_count()
    
    # Group attendance by date
    daily_attendance = defaultdict(int)
    for record in all_attendance:
        daily_attendance[record['date']] += 1
    
    # Get last 30 days of data
    end_date = date.today()
    start_date = end_date - timedelta(days=29)
    
    trend_data = []
    current_date = start_date
    
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        present_count = daily_attendance.get(date_str, 0)
        percentage = round((present_count / total_faculty * 100) if total_faculty > 0 else 0, 1)
        
        trend_data.append({
            'date': date_str,
            'present': present_count,
            'percentage': percentage
        })
        
        current_date += timedelta(days=1)
    
    return jsonify(trend_data)