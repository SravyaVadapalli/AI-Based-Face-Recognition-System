from flask import Blueprint, render_template, request, send_file, flash, redirect, url_for
from routes.auth import login_required
from utils.db_handler import get_all_attendance, get_all_faculty, get_attendance_by_date
from datetime import datetime, date, timedelta
import csv
import json
import os
from io import StringIO, BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/')
@login_required
def reports_home():
    return render_template('reports/export.html')

@reports_bp.route('/view')
@login_required
def view():
    return render_template('reports/view.html')

@reports_bp.route('/generate', methods=['POST'])
@login_required
def generate():
    report_type = request.form.get('report_type')
    format_type = request.form.get('format_type')
    date_from = request.form.get('date_from')
    date_to = request.form.get('date_to')
    faculty_filter = request.form.get('faculty_filter')
    department_filter = request.form.get('department_filter')
    
    if not all([report_type, format_type]):
        flash('Please select report type and format', 'error')
        return redirect(url_for('reports.export'))
    
    try:
        # Get filtered data
        attendance_data = get_filtered_attendance_data(
            date_from, date_to, faculty_filter, department_filter
        )
        
        if not attendance_data:
            flash('No data found for the selected criteria', 'warning')
            return redirect(url_for('reports.export'))
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{report_type}_{timestamp}.{format_type}"
        
        if format_type == 'csv':
            return generate_csv_report(attendance_data, filename, report_type)
        elif format_type == 'pdf':
            return generate_pdf_report(attendance_data, filename, report_type, 
                                     date_from, date_to)
        else:
            flash('Invalid format type', 'error')
            return redirect(url_for('reports.export'))
    
    except Exception as e:
        flash(f'Error generating report: {str(e)}', 'error')
        return redirect(url_for('reports.export'))

def get_filtered_attendance_data(date_from, date_to, faculty_filter, department_filter):
    """Get attendance data based on filters"""
    all_attendance = get_all_attendance()
    all_faculty = get_all_faculty()
    
    # Create faculty lookup
    faculty_map = {f['faculty_id']: f for f in all_faculty}
    
    # Filter by date range
    if date_from and date_to:
        all_attendance = [
            r for r in all_attendance 
            if date_from <= r['date'] <= date_to
        ]
    elif date_from:
        all_attendance = [
            r for r in all_attendance 
            if r['date'] >= date_from
        ]
    elif date_to:
        all_attendance = [
            r for r in all_attendance 
            if r['date'] <= date_to
        ]
    
    # Enrich with faculty information and apply filters
    enriched_data = []
    for record in all_attendance:
        faculty = faculty_map.get(record['faculty_id'])
        if faculty:
            # Apply faculty filter
            if faculty_filter and record['faculty_id'] != faculty_filter:
                continue
            
            # Apply department filter
            if department_filter and faculty['department'] != department_filter:
                continue
            
            enriched_record = record.copy()
            enriched_record.update({
                'faculty_name': faculty['name'],
                'department': faculty['department'],
                'email': faculty['email'],
                'phone': faculty.get('phone', '')
            })
            enriched_data.append(enriched_record)
    
    return enriched_data

def generate_csv_report(data, filename, report_type):
    """Generate CSV report"""
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    headers = [
        'Faculty ID', 'Faculty Name', 'Department', 'Email', 
        'Date', 'Time', 'Status', 'Location'
    ]
    writer.writerow(headers)
    
    # Write data
    for record in data:
        writer.writerow([
            record['faculty_id'],
            record['faculty_name'],
            record['department'],
            record['email'],
            record['date'],
            record['time'],
            record['status'],
            record['location']
        ])
    
    # Save to uploads folder
    report_dir = os.path.join('uploads', 'attendance-reports', 'daily')
    os.makedirs(report_dir, exist_ok=True)
    file_path = os.path.join(report_dir, filename)
    
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        f.write(output.getvalue())
    
    output.close()
    
    # Send file to user
    return send_file(file_path, as_attachment=True, download_name=filename)

def generate_pdf_report(data, filename, report_type, date_from, date_to):
    """Generate PDF report"""
    # Create BytesIO buffer
    buffer = BytesIO()
    
    # Create PDF document
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.darkblue,
        alignment=1  # Center alignment
    )
    
    # Add title
    title = f"Faculty Attendance Report"
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 12))
    
    # Add report info
    info_style = styles['Normal']
    if date_from and date_to:
        date_range = f"Period: {date_from} to {date_to}"
    elif date_from:
        date_range = f"From: {date_from}"
    elif date_to:
        date_range = f"Until: {date_to}"
    else:
        date_range = "All Records"
    
    elements.append(Paragraph(date_range, info_style))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", info_style))
    elements.append(Paragraph(f"Total Records: {len(data)}", info_style))
    elements.append(Spacer(1, 12))
    
    # Create table data
    table_data = [['Faculty ID', 'Name', 'Department', 'Date', 'Time', 'Status']]
    
    for record in data:
        table_data.append([
            record['faculty_id'],
            record['faculty_name'][:20] + '...' if len(record['faculty_name']) > 20 else record['faculty_name'],
            record['department'][:15] + '...' if len(record['department']) > 15 else record['department'],
            record['date'],
            record['time'],
            record['status']
        ])
    
    # Create table
    table = Table(table_data)
    
    # Add style to table
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    
    # Build PDF
    doc.build(elements)
    
    # Save to uploads folder
    report_dir = os.path.join('uploads', 'attendance-reports', 'weekly')
    os.makedirs(report_dir, exist_ok=True)
    file_path = os.path.join(report_dir, filename)
    
    with open(file_path, 'wb') as f:
        f.write(buffer.getvalue())
    
    buffer.seek(0)
    
    # Send file to user
    return send_file(BytesIO(buffer.getvalue()), 
                     as_attachment=True, 
                     download_name=filename,
                     mimetype='application/pdf')
