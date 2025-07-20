from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from werkzeug.security import generate_password_hash
from routes.auth import login_required
from utils.db_handler import (
    get_all_faculty, get_faculty_by_id, create_faculty, 
    update_faculty, delete_faculty
)
from face_utils import get_average_embedding_from_images, get_embedding_from_image, l2_normalize
import uuid
from datetime import datetime
import os
import numpy as np
from PIL import Image

faculty_bp = Blueprint('faculty', __name__, url_prefix='/faculty')

@faculty_bp.route('/manage')
def manage_faculty():
    return render_template('faculty/manage.html')

@faculty_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            # ✅ Extract form fields
            name = request.form.get('name')
            email = request.form.get('email')
            phone = request.form.get('phone', '')
            department = request.form.get('department')
            faculty_id = request.form.get('faculty_id')
            password = request.form.get('password')

            # ✅ Get non-empty images
            image_files = [f for f in request.files.getlist('face_images') if f and f.filename]

            # ✅ Validate form fields
            if not all([name, email, phone, department, password, faculty_id]):
                flash('Please fill in all required fields.', 'error')
                return render_template('faculty/register.html')

            # ✅ Require exactly 3 images
            if len(image_files) != 3:
                flash('Exactly 3 face images are required for registration.', 'error')
                return render_template('faculty/register.html')

            print(f"✅ Received {len(image_files)} face images: {[f.filename for f in image_files]}")

            # ✅ Check for duplicates
            existing_faculty = get_all_faculty(db_path=current_app.config['DB_PATH'])
            if any(fac['email'] == email or fac['faculty_id'] == faculty_id for fac in existing_faculty):
                flash('Faculty with this email or ID already exists.', 'error')
                return render_template('faculty/register.html')

            # ✅ Convert to PIL images
            image_objs = []
            for file in image_files:
                try:
                    image_objs.append(Image.open(file).convert('RGB'))
                except Exception as e:
                    print(f"Skipping image due to error: {file.filename} -> {e}")

            if not image_objs:
                flash('No valid images uploaded.', 'error')
                return render_template('faculty/register.html')

            # ✅ Generate average embedding
            mean_embedding = get_average_embedding_from_images(image_objs)
            if mean_embedding is None:
                flash('No face detected in uploaded images.', 'error')
                return render_template('faculty/register.html')
            mean_embedding = l2_normalize(mean_embedding)

            # ✅ Optional .npy backup
            embeddings_dir = os.path.join(os.path.dirname(current_app.config['DB_PATH']), 'faces')
            os.makedirs(embeddings_dir, exist_ok=True)
            embedding_path = os.path.join(embeddings_dir, f"{faculty_id}.npy")
            np.save(embedding_path, mean_embedding)

            # ✅ Prepare DB payload
            faculty_data = {
                'faculty_id': faculty_id,
                'name': name,
                'email': email,
                'phone': phone,
                'department': department,
                'password_hash': generate_password_hash(password),
                'face_embedding': mean_embedding.astype(np.float32).tobytes(),
                'registered_on': datetime.now().isoformat()
            }

            # ✅ Save to DB
            if create_faculty(faculty_data, db_path=current_app.config['DB_PATH']):
                flash(f'Faculty {name} registered successfully with ID: {faculty_id}', 'success')
                return redirect(url_for('faculty.register'))
            else:
                flash('Failed to register faculty. Please try again.', 'error')
                return render_template('faculty/register.html')

        except Exception as e:
            flash(f"Unexpected error occurred: {str(e)}", "error")
            return render_template('faculty/register.html')

    return render_template('faculty/register.html')

@faculty_bp.route('/api/list', methods=['GET'])
def api_get_faculty_list():
    try:
        faculty_list = get_all_faculty(db_path=current_app.config['DB_PATH'])
        # Hide sensitive fields
        cleaned = [{
            "faculty_id": f["faculty_id"],
            "name": f["name"],
            "email": f["email"],
            "department": f["department"]
        } for f in faculty_list]
        return jsonify(cleaned)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@faculty_bp.route('/api/save', methods=['POST'])
@login_required
def api_save_faculty():
    faculty_id = request.form.get('faculty_id', '').strip()
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    department = request.form.get('department', '').strip()
    password = request.form.get('password', '').strip()
    image_file = request.files.get('face_image')

    if not all([faculty_id, name, email, phone, department]):
        return jsonify({'success': False, 'message': 'All fields except password and image are required.'}), 400

    embedding_bytes = None
    if image_file:
        try:
            image = Image.open(image_file).convert('RGB')
            embedding = get_embedding_from_image(np.array(image))
            if embedding is None:
                return jsonify({'success': False, 'message': 'Face not detected.'}), 400
            embedding = l2_normalize(embedding)
            embedding_bytes = embedding.tobytes()
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error processing image: {e}'}), 400

    existing_faculty = get_faculty_by_id(faculty_id, db_path=current_app.config['DB_PATH'])

    if existing_faculty:
        # UPDATE
        updated_fields = {
            'name': name,
            'email': email,
            'phone': phone,
            'department': department
        }
        if password:
            updated_fields['password_hash'] = generate_password_hash(password)
        if embedding_bytes:
            updated_fields['face_embedding'] = embedding_bytes

        success = update_faculty(faculty_id, updated_fields, db_path=current_app.config['DB_PATH'])
        message = "Faculty updated successfully." if success else "Failed to update faculty."
        return jsonify({'success': success, 'message': message})

    else:
        # CREATE
        if not password or not embedding_bytes:
            return jsonify({'success': False, 'message': 'Password and face image are required for new faculty.'}), 400

        faculty_data = {
            'faculty_id': faculty_id,
            'name': name,
            'email': email,
            'phone': phone,
            'department': department,
            'password_hash': generate_password_hash(password),
            'face_embedding': embedding_bytes,
            'registered_on': datetime.now().isoformat()
        }

        success = create_faculty(faculty_data, db_path=current_app.config['DB_PATH'])
        message = "Faculty created successfully." if success else "Failed to create faculty."
        return jsonify({'success': success, 'message': message})

@faculty_bp.route('/api/delete/<faculty_id>', methods=['DELETE'])
@login_required
def api_delete_faculty(faculty_id):
    success = delete_faculty(faculty_id, db_path=current_app.config['DB_PATH'])
    return jsonify({'success': success, 'message': 'Deleted.' if success else 'Deletion failed.'})