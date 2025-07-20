import os
import uuid
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from typing import Optional

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_extension(filename: str) -> str:
    """Get file extension"""
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

def save_faculty_image(faculty_id: str, file: FileStorage) -> Optional[str]:
    """Save faculty face image and return S3-like path"""
    if not file or not file.filename:
        return None
    
    if not allowed_file(file.filename):
        return None
    
    try:
        # Create faculty directory
        faculty_dir = os.path.join('uploads', 'faculty', faculty_id)
        os.makedirs(faculty_dir, exist_ok=True)
        
        # Generate secure filename
        extension = get_file_extension(file.filename)
        filename = f"face.{extension}"
        file_path = os.path.join(faculty_dir, filename)
        
        # Save file
        file.save(file_path)
        
        # Return S3-like URL path
        s3_path = f"faculty/{faculty_id}/{filename}"
        return s3_path
    
    except Exception as e:
        print(f"Error saving faculty image: {str(e)}")
        return None

def delete_faculty_image(faculty_id: str) -> bool:
    """Delete faculty face image"""
    try:
        faculty_dir = os.path.join('uploads', 'faculty', faculty_id)
        
        if os.path.exists(faculty_dir):
            # Remove all files in faculty directory
            for filename in os.listdir(faculty_dir):
                file_path = os.path.join(faculty_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            
            # Remove directory if empty
            try:
                os.rmdir(faculty_dir)
            except OSError:
                pass  # Directory not empty, that's okay
        
        return True
    
    except Exception as e:
        print(f"Error deleting faculty image: {str(e)}")
        return False

def get_faculty_image_path(faculty_id: str) -> Optional[str]:
    """Get faculty image file path"""
    faculty_dir = os.path.join('uploads', 'faculty', faculty_id)
    
    if not os.path.exists(faculty_dir):
        return None
    
    # Look for face image files
    for filename in os.listdir(faculty_dir):
        if filename.startswith('face.') and allowed_file(filename):
            return os.path.join(faculty_dir, filename)
    
    return None

def save_attendance_record(date: str, record_data: dict) -> bool:
    """Save attendance record as JSON file"""
    try:
        records_dir = os.path.join('uploads', 'attendance-records')
        os.makedirs(records_dir, exist_ok=True)
        
        filename = f"{date}.json"
        file_path = os.path.join(records_dir, filename)
        
        import json
        
        # Load existing records if file exists
        existing_records = []
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                try:
                    existing_records = json.load(f)
                except:
                    existing_records = []
        
        # Add new record
        existing_records.append(record_data)
        
        # Save updated records
        with open(file_path, 'w') as f:
            json.dump(existing_records, f, indent=2)
        
        return True
    
    except Exception as e:
        print(f"Error saving attendance record: {str(e)}")
        return False

def save_captured_image(image_file: FileStorage, faculty_id: str = None) -> Optional[str]:
    """Save captured image for attendance"""
    if not image_file or not image_file.filename:
        return None
    
    try:
        # Create videos directory (as per S3 structure)
        if faculty_id:
            videos_dir = os.path.join('uploads', 'videos', faculty_id)
        else:
            videos_dir = os.path.join('uploads', 'videos', 'captured')
        
        os.makedirs(videos_dir, exist_ok=True)
        
        # Generate filename with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        extension = get_file_extension(image_file.filename)
        filename = f"capture_{timestamp}.{extension}"
        file_path = os.path.join(videos_dir, filename)
        
        # Save file
        image_file.save(file_path)
        
        return file_path
    
    except Exception as e:
        print(f"Error saving captured image: {str(e)}")
        return None

def create_upload_directories():
    """Create all necessary upload directories as per S3 structure"""
    directories = [
        'uploads/faculty',
        'uploads/attendance-records',
        'uploads/attendance-reports/daily',
        'uploads/attendance-reports/weekly',
        'uploads/attendance-reports/monthly',
        'uploads/videos',
        'uploads/models',
        'uploads/chatbot-logs',
        'uploads/alerts',
        'uploads/logs',
        'uploads/docs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

# Initialize directories on import
create_upload_directories()
