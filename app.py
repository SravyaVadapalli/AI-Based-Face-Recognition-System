import sys
import os
import logging
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

# Extend path for internal imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "faculty-attendance-system-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Upload settings
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database path
app.config['DB_PATH'] = os.path.join(os.getcwd(), 'attendance.db')

# ========== Import Blueprints ==========
from routes.main import main_bp
from routes.auth import auth_bp
from routes.faculty import faculty_bp
from routes.attendance import attendance_bp
from routes.dashboard import dashboard_bp
from routes.reports import reports_bp
from routes.chatbot import chatbot_bp
from routes.alerts import alerts_bp
from routes.logs import logs_bp

# ========== Register Blueprints ==========
app.register_blueprint(main_bp)
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(faculty_bp, url_prefix='/faculty')
app.register_blueprint(attendance_bp, url_prefix='/attendance')
app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
app.register_blueprint(reports_bp, url_prefix='/reports')
app.register_blueprint(chatbot_bp, url_prefix='/chatbot')
app.register_blueprint(alerts_bp, url_prefix='/alerts')
app.register_blueprint(logs_bp, url_prefix='/logs')

# ========== Initialize SQLite Database ==========
from utils.db_handler import initialize_data_files
initialize_data_files(db_path=app.config['DB_PATH'])

# Run the app
if __name__ == '__main__':
    app.run(debug=True)