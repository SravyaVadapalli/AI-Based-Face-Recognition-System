from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from utils.db_handler import get_connection
import sqlite3
import logging

# Define the Blueprint
auth_bp = Blueprint('auth', __name__)

# --- Helper Decorator ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin' not in session:
            flash('Please log in to access this page', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def verify_admin_login(username, password, db_path='attendance.db'):
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admins WHERE username = ?", (username,))
        admin = cursor.fetchone()
        if admin and check_password_hash(admin[2], password):  # admin[2] = password_hash
            return True
        return False

# --- Routes ---

@auth_bp.route('/')
def home():
    return redirect(url_for('auth.login'))

@auth_bp.route('/admin/signup')
def admin_signup():
    return render_template('auth/adminsignup.html')

@auth_bp.route('/admin/register', methods=['POST'])
def admin_register():
    username = request.form.get('name')
    email = request.form.get('email')
    admin_id = request.form.get('emp_id')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    if not all([username, email, admin_id, password, confirm_password]):
        flash("All fields are required.", "error")
        return redirect(url_for('auth.admin_signup'))

    if password != confirm_password:
        flash("Passwords do not match.", "error")
        return redirect(url_for('auth.admin_signup'))

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admins WHERE admin_id = ? OR username = ?", (admin_id, username))
        if cursor.fetchone():
            flash("Admin with this ID or username already exists.", "error")
            return redirect(url_for('auth.admin_signup'))

        hashed_password = generate_password_hash(password)
        cursor.execute('''
            INSERT INTO admins (admin_id, username, password_hash, email)
            VALUES (?, ?, ?, ?)
        ''', (admin_id, username, hashed_password, email))
        conn.commit()
        conn.close()

        flash("Admin registered successfully!", "success")
        return redirect(url_for('auth.login'))

    except sqlite3.Error as e:
        flash(f"Database error: {e}", "error")
        return redirect(url_for('auth.admin_signup'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    logging.warning("⚠️ Login route was triggered")  # Debug log
    if request.method == 'POST':
        username = request.form.get('email')
        password = request.form.get('password')

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM admins WHERE email = ?", (username,))
            admin = cursor.fetchone()

            if admin and check_password_hash(admin[2], password):
                session['admin'] = username
                return redirect(url_for('dashboard.admin_dashboard'))  # ✅ final fix
            else:
                flash("Invalid username or password.", "error")
                return redirect(url_for('auth.login'))

        except sqlite3.Error as e:
            flash(f"Database error: {e}", "error")
            return redirect(url_for('auth.login'))

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('auth.login'))