# IMPORTS
from flask import Blueprint, render_template, flash, session, redirect, url_for, request, jsonify, send_from_directory
from blueprints.get_user_info import get_personal_info, get_address_info, get_contact_info, get_valid_info, get_business_info
from db_connection import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import base64
import re
import secrets
from datetime import datetime

seller_settings_bp = Blueprint('seller_settings', __name__)

# Constants for file uploads
PROFILE_PIC_FOLDER = 'static/uploads/seller/profile_pics'
VALID_ID_FOLDER = 'static/uploads/seller/valid_id_pic'
PERMIT_PIC_FOLDER = 'static/uploads/seller/permit_pic'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Ensure folders exist
for folder in [PROFILE_PIC_FOLDER, VALID_ID_FOLDER, PERMIT_PIC_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# HELPER FUNCTIONS
def save_uploaded_file(file, folder):
    """Save uploaded file and return filename"""
    if file and file.filename:
        temp_token = secrets.token_urlsafe(16)
        filename = f"{temp_token}_{secure_filename(file.filename)}"
        file_path = os.path.join(folder, filename)
        file.save(file_path)
        return filename
    return None

def delete_old_file(filename, folder):
    """Delete old file if it exists"""
    if filename:
        file_path = os.path.join(folder, filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")

# VALIDATION FUNCTIONS
def validate_name(name):
    """Validate that name contains only letters and spaces"""
    return bool(re.match(r'^[A-Za-z\s]+$', name))

def validate_phone(phone):
    """Validate Philippine phone number format"""
    # Format: +63XXXXXXXXXX or 09XXXXXXXXX
    return bool(re.match(r'^(\+63|09)\d{9}$', phone))

def validate_email(email):
    """Validate email format"""
    return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))

def validate_password_strength(password):
    """
    Validate password strength:
    - At least 8 characters
    - Contains uppercase and lowercase
    - Contains numbers
    - Contains special characters
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    return True, "Password is strong"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@seller_settings_bp.route('/seller/settings')
def settings():
    if 'seller' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Seller':
        flash("Unauthorized access. Sellers only.", "danger")
        return redirect(url_for('login.login'))
    
    seller_id = session['seller']
    
    # Get all user information
    personal_info = get_personal_info(seller_id)
    address_info = get_address_info(seller_id)
    contact_info = get_contact_info(seller_id)
    valid_info = get_valid_info(seller_id)
    business_info = get_business_info(seller_id)
    
    return render_template('seller_settings.html', 
                         personal_info=personal_info,
                         address_info=address_info,
                         contact_info=contact_info,
                         valid_info=valid_info,
                         business_info=business_info)

@seller_settings_bp.route('/seller/settings/update-personal', methods=['POST'])
def update_personal_info():
    if 'seller' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Seller':
        return jsonify({'success': False, 'message': 'Unauthorized access'})
    
    try:
        seller_id = session['seller']
        
        # Get form data
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        sex = request.form.get('sex')
        birthdate = request.form.get('birthdate')
        
        # Validate inputs
        if not firstname or not lastname:
            return jsonify({'success': False, 'message': 'First name and last name are required.'})

        if not validate_name(firstname) or not validate_name(lastname):
            return jsonify({'success': False, 'message': 'Names should only contain letters and spaces.'})

        if not sex:
            return jsonify({'success': False, 'message': 'Please select your sex.'})

        if not birthdate:
            return jsonify({'success': False, 'message': 'Please enter your birthdate.'})

        try:
            birth_date = datetime.strptime(birthdate, '%Y-%m-%d')
            today = datetime.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

            if age < 18:
                return jsonify({'success': False, 'message': 'You must be 18 years old or above.'})

        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid birthdate format.'})
        
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Get personal_id for the user
        cursor.execute("SELECT personal_id FROM user_account WHERE user_id = %s", (seller_id,))
        result = cursor.fetchone()
        
        if not result:
            return jsonify({'success': False, 'message': 'User not found.'})
            
        personal_id = result[0]
        
        # Update personal information
        cursor.execute("""
            UPDATE account_personal_info 
            SET firstname = %s, lastname = %s, sex = %s, age = %s, birthdate = %s
            WHERE personal_id = %s
        """, (firstname, lastname, sex, age, birthdate, personal_id))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        # Update session data
        session['personal_data'] = {
            'firstname': firstname,
            'lastname': lastname,
            'sex': sex,
            'age': age,
            'birthdate': birthdate
        }
        
        return jsonify({'success': True, 'message': 'Personal information updated successfully!'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error updating personal information: {str(e)}'})

@seller_settings_bp.route('/seller/settings/update-address', methods=['POST'])
def update_address_info():
    if 'seller' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Seller':
        return jsonify({'success': False, 'message': 'Unauthorized access'})
    
    try:
        seller_id = session['seller']
        
        # Get form data
        house_no = request.form.get('house_no')
        street = request.form.get('street_text')
        barangay = request.form.get('barangay_text')
        city = request.form.get('city_text')
        province = request.form.get('province_text')
        region = request.form.get('region_text')
        
        # Validate inputs
        if not house_no:
            return jsonify({'success': False, 'message': 'House number is required.'})
        
        if not barangay or not city or not province or not region:
            return jsonify({'success': False, 'message': 'Please fill in all required address fields.'})
        
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Get address_id for the user
        cursor.execute("SELECT address_id FROM user_account WHERE user_id = %s", (seller_id,))
        result = cursor.fetchone()
        
        if not result:
            return jsonify({'success': False, 'message': 'User not found.'})
            
        address_id = result[0]
        
        # Update address information
        cursor.execute("""
            UPDATE account_address_info 
            SET house_no = %s, street = %s, barangay = %s, city = %s, province = %s, region = %s
            WHERE address_id = %s
        """, (house_no, street, barangay, city, province, region, address_id))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({'success': True, 'message': 'Address information updated successfully!'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error updating address information: {str(e)}'})

@seller_settings_bp.route('/seller/settings/update-contact', methods=['POST'])
def update_contact_info():
    if 'seller' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Seller':
        return jsonify({'success': False, 'message': 'Unauthorized access'})
    
    try:
        seller_id = session['seller']
        
        # Get form data
        email = request.form.get('email')
        phone = request.form.get('phone')
        
        # Validate inputs
        if not phone or not email:
            return jsonify({'success': False, 'message': 'Phone number and email are required.'})

        if not validate_phone(phone):
            return jsonify({'success': False, 'message': 'Invalid phone number format. Must be 09XXXXXXXXX format.'})

        if not validate_email(email):
            return jsonify({'success': False, 'message': 'Invalid email format.'})
        
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Check if email already exists (excluding current user)
        cursor.execute("""
            SELECT aci.contact_id FROM account_contact_info aci
            JOIN user_account ua ON aci.contact_id = ua.contact_id
            WHERE aci.email = %s AND ua.user_id != %s
        """, (email, seller_id))
        
        if cursor.fetchone():
            return jsonify({'success': False, 'message': 'Email already exists!'})
        
        # Check if phone already exists (excluding current user)
        cursor.execute("""
            SELECT aci.contact_id FROM account_contact_info aci
            JOIN user_account ua ON aci.contact_id = ua.contact_id
            WHERE aci.phone = %s AND ua.user_id != %s
        """, (phone, seller_id))
        
        if cursor.fetchone():
            return jsonify({'success': False, 'message': 'Phone number already exists!'})
        
        # Get contact_id for the user
        cursor.execute("SELECT contact_id FROM user_account WHERE user_id = %s", (seller_id,))
        result = cursor.fetchone()
        
        if not result:
            return jsonify({'success': False, 'message': 'User not found.'})
            
        contact_id = result[0]
        
        # Update contact information
        cursor.execute("""
            UPDATE account_contact_info 
            SET email = %s, phone = %s
            WHERE contact_id = %s
        """, (email, phone, contact_id))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        # Update session data
        session['contact_data'] = {
            'email': email,
            'phone': phone
        }
        
        return jsonify({'success': True, 'message': 'Contact information updated successfully!'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error updating contact information: {str(e)}'})

@seller_settings_bp.route('/seller/settings/update-business', methods=['POST'])
def update_business_info():
    if 'seller' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Seller':
        return jsonify({'success': False, 'message': 'Unauthorized access'})
    
    try:
        seller_id = session['seller']
        
        # Get form data
        business_name = request.form.get('business_name')
        permit_no = request.form.get('permit_no')
        issue_date_str = request.form.get('issue_date')
        expiry_date_str = request.form.get('expiry_date')
        
        # Validate inputs
        if not business_name or not permit_no:
            return jsonify({'success': False, 'message': 'Business name and permit number are required.'})

        if not issue_date_str or not expiry_date_str:
            return jsonify({'success': False, 'message': 'Issue date and expiry date are required.'})

        try:
            issue_date = datetime.strptime(issue_date_str, '%Y-%m-%d')
            expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d')
            
            if issue_date >= expiry_date:
                return jsonify({'success': False, 'message': 'Issue date must be before expiry date.'})

            if expiry_date < datetime.today():
                return jsonify({'success': False, 'message': 'Business permit has expired. Please provide a valid permit.'})

        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid date format.'})
        
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Get business_id for the user
        cursor.execute("SELECT business_id FROM user_account WHERE user_id = %s", (seller_id,))
        result = cursor.fetchone()
        
        if not result:
            return jsonify({'success': False, 'message': 'User not found.'})
            
        business_id = result[0]
        
        # Get current permit picture filename to delete old one if new file is uploaded
        cursor.execute("SELECT permit_pic FROM account_business_info WHERE business_id = %s", (business_id,))
        result = cursor.fetchone()
        old_permit_filename = result[0] if result else None
        
        # Handle file upload if provided
        new_permit_filename = None
        if 'permit_pic' in request.files:
            file = request.files['permit_pic']
            if file and file.filename != '' and allowed_file(file.filename):
                # Validate file size (5MB max)
                file.seek(0, 2)  # Seek to end to get file size
                file_size = file.tell()
                file.seek(0)  # Reset to beginning
                
                if file_size > 5 * 1024 * 1024:  # 5MB
                    return jsonify({'success': False, 'message': 'File size too large. Maximum size is 5MB.'})
                
                # Save new file
                new_permit_filename = save_uploaded_file(file, PERMIT_PIC_FOLDER)
                if not new_permit_filename:
                    return jsonify({'success': False, 'message': 'Failed to save permit picture.'})
                    
            elif file and file.filename != '' and not allowed_file(file.filename):
                return jsonify({'success': False, 'message': 'Invalid file type. Please upload PNG, JPG, or JPEG files only.'})
        
        # Update business information
        if new_permit_filename:
            cursor.execute("""
                UPDATE account_business_info 
                SET business_name = %s, permit_no = %s, issue_date = %s, expiry_date = %s, permit_pic = %s
                WHERE business_id = %s
            """, (business_name, permit_no, issue_date_str, expiry_date_str, new_permit_filename, business_id))
            
            # Delete old file after successful database update
            if old_permit_filename:
                delete_old_file(old_permit_filename, PERMIT_PIC_FOLDER)
        else:
            cursor.execute("""
                UPDATE account_business_info 
                SET business_name = %s, permit_no = %s, issue_date = %s, expiry_date = %s
                WHERE business_id = %s
            """, (business_name, permit_no, issue_date_str, expiry_date_str, business_id))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({'success': True, 'message': 'Business information updated successfully!'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error updating business information: {str(e)}'})

@seller_settings_bp.route('/seller/settings/update-valid-id', methods=['POST'])
def update_valid_id():
    if 'seller' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Seller':
        return jsonify({'success': False, 'message': 'Unauthorized access'})
    
    try:
        seller_id = session['seller']
        
        # Get form data
        id_type = request.form.get('id_type')
        id_no = request.form.get('id_no')
        
        # Validate inputs
        if not id_type or not id_no:
            return jsonify({'success': False, 'message': 'ID type and number are required.'})
        
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Check if ID number already exists (excluding current user)
        cursor.execute("""
            SELECT avi.valid_id FROM account_valid_info avi
            JOIN user_account ua ON avi.valid_id = ua.valid_id
            WHERE avi.id_no = %s AND ua.user_id != %s
        """, (id_no, seller_id))
        
        if cursor.fetchone():
            return jsonify({'success': False, 'message': 'ID number already exists!'})
        
        # Get valid_id for the user
        cursor.execute("SELECT valid_id FROM user_account WHERE user_id = %s", (seller_id,))
        result = cursor.fetchone()
        
        if not result:
            return jsonify({'success': False, 'message': 'User not found.'})
            
        valid_id = result[0]
        
        # Get current ID picture filename to delete old one if new file is uploaded
        cursor.execute("SELECT id_pic FROM account_valid_info WHERE valid_id = %s", (valid_id,))
        result = cursor.fetchone()
        old_id_filename = result[0] if result else None
        
        # Handle file upload if provided
        new_id_filename = None
        if 'id_pic' in request.files:
            file = request.files['id_pic']
            if file and file.filename != '' and allowed_file(file.filename):
                # Validate file size (5MB max)
                file.seek(0, 2)  # Seek to end to get file size
                file_size = file.tell()
                file.seek(0)  # Reset to beginning
                
                if file_size > 5 * 1024 * 1024:  # 5MB
                    return jsonify({'success': False, 'message': 'File size too large. Maximum size is 5MB.'})
                
                # Save new file
                new_id_filename = save_uploaded_file(file, VALID_ID_FOLDER)
                if not new_id_filename:
                    return jsonify({'success': False, 'message': 'Failed to save ID picture.'})
                    
            elif file and file.filename != '' and not allowed_file(file.filename):
                return jsonify({'success': False, 'message': 'Invalid file type. Please upload PNG, JPG, or JPEG files only.'})
        
        # Update valid ID information
        if new_id_filename:
            cursor.execute("""
                UPDATE account_valid_info 
                SET id_type = %s, id_no = %s, id_pic = %s
                WHERE valid_id = %s
            """, (id_type, id_no, new_id_filename, valid_id))
            
            # Delete old file after successful database update
            if old_id_filename:
                delete_old_file(old_id_filename, VALID_ID_FOLDER)
        else:
            cursor.execute("""
                UPDATE account_valid_info 
                SET id_type = %s, id_no = %s
                WHERE valid_id = %s
            """, (id_type, id_no, valid_id))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({'success': True, 'message': 'Valid ID information updated successfully!'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error updating valid ID information: {str(e)}'})

@seller_settings_bp.route('/seller/settings/change-password', methods=['POST'])
def change_password():
    if 'seller' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Seller':
        return jsonify({'success': False, 'message': 'Unauthorized access'})
    
    try:
        seller_id = session['seller']
        
        # Get form data
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate inputs
        if not current_password or not new_password or not confirm_password:
            return jsonify({'success': False, 'message': 'All fields are required.'})
        
        # Validate passwords
        if new_password != confirm_password:
            return jsonify({'success': False, 'message': 'New passwords do not match!'})
        
        # Validate password strength
        is_valid, message = validate_password_strength(new_password)
        if not is_valid:
            return jsonify({'success': False, 'message': message})
        
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Get current password hash
        cursor.execute("""
            SELECT ali.password FROM account_login_info ali
            JOIN user_account ua ON ali.login_id = ua.login_id
            WHERE ua.user_id = %s
        """, (seller_id,))
        
        result = cursor.fetchone()
        if not result:
            cursor.close()
            connection.close()
            return jsonify({'success': False, 'message': 'User not found!'})
        
        current_password_hash = result[0]
        
        # Verify current password
        if not check_password_hash(current_password_hash, current_password):
            cursor.close()
            connection.close()
            return jsonify({'success': False, 'message': 'Current password is incorrect!'})
        
        # Hash new password
        new_password_hash = generate_password_hash(new_password)
        
        # Update password
        cursor.execute("""
            UPDATE account_login_info ali
            JOIN user_account ua ON ali.login_id = ua.login_id
            SET ali.password = %s
            WHERE ua.user_id = %s
        """, (new_password_hash, seller_id))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({'success': True, 'message': 'Password changed successfully!'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error changing password: {str(e)}'})

@seller_settings_bp.route('/seller/settings/update-profile-pic', methods=['POST'])
def update_profile_pic():
    if 'seller' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Seller':
        return jsonify({'success': False, 'message': 'Unauthorized access'})
    
    try:
        seller_id = session['seller']
        
        if 'profile_pic' not in request.files:
            return jsonify({'success': False, 'message': 'No file selected!'})
        
        file = request.files['profile_pic']
        
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected!'})
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'message': 'Invalid file type! Please upload PNG, JPG, or JPEG files only.'})
        
        # Validate file size (5MB max)
        file.seek(0, 2)  # Seek to end to get file size
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if file_size > 5 * 1024 * 1024:  # 5MB
            return jsonify({'success': False, 'message': 'File size too large. Maximum size is 5MB.'})
        
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Get current profile picture filename to delete old one
        cursor.execute("SELECT profile_pic FROM user_account WHERE user_id = %s", (seller_id,))
        result = cursor.fetchone()
        old_filename = result[0] if result else None
        
        # Save new file
        new_filename = save_uploaded_file(file, PROFILE_PIC_FOLDER)
        
        if not new_filename:
            cursor.close()
            connection.close()
            return jsonify({'success': False, 'message': 'Failed to save file.'})
        
        # Update profile picture filename in database
        cursor.execute("""
            UPDATE user_account 
            SET profile_pic = %s
            WHERE user_id = %s
        """, (new_filename, seller_id))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        # Delete old file after successful database update
        if old_filename:
            delete_old_file(old_filename, PROFILE_PIC_FOLDER)
        
        # Update session data
        session['profile_pic'] = new_filename
        
        return jsonify({'success': True, 'message': 'Profile picture updated successfully!'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error updating profile picture: {str(e)}'})

# Routes to serve uploaded files
@seller_settings_bp.route('/uploads/profile_pics/<filename>')
def serve_profile_pic(filename):
    return send_from_directory(PROFILE_PIC_FOLDER, filename)

@seller_settings_bp.route('/uploads/valid_ids/<filename>')
def serve_valid_id(filename):
    return send_from_directory(VALID_ID_FOLDER, filename)

@seller_settings_bp.route('/uploads/permit_pics/<filename>')
def serve_permit_pic(filename):
    return send_from_directory(PERMIT_PIC_FOLDER, filename) 