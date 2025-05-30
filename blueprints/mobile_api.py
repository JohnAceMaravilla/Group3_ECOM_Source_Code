from flask import Blueprint, jsonify, request, session
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from db_connection import get_db_connection
from datetime import datetime, timedelta
import re
import secrets
import os
import mysql.connector
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import random
import hashlib

mobile_api_bp = Blueprint('mobile_api', __name__, url_prefix='/api/mobile')

# Enable CORS for mobile app communication
CORS(mobile_api_bp)

# File upload settings
BUYER_ID_UPLOAD_FOLDER = "static/uploads/buyer/valid_id_pic"
COURIER_ID_UPLOAD_FOLDER = "static/uploads/courier/valid_id_pic"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Ensure upload folders exist
for folder in [BUYER_ID_UPLOAD_FOLDER, COURIER_ID_UPLOAD_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Validation functions
def validate_name(name):
    return bool(re.match(r'^[A-Za-z\s]+$', name))

def validate_phone(phone):
    return bool(re.match(r'^(\+63|09)\d{9}$', phone))

def validate_email(email):
    return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))

def validate_password_strength(password):
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

def validate_file_extension(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_file_size(file):
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    return size <= MAX_FILE_SIZE

def email_exists(email):
    conn = get_db_connection()
    if not conn:
        return False
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM account_contact_info WHERE email = %s", (email,))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

def phone_exists(phone):
    conn = get_db_connection()
    if not conn:
        return False
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM account_contact_info WHERE phone = %s", (phone,))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

def id_number_exists(id_no):
    conn = get_db_connection()
    if not conn:
        return False
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM account_valid_info WHERE id_no = %s", (id_no,))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

def send_otp_email(email, otp):
    """Send OTP email to user"""
    sender_email = "fanamazecommerce@zohomail.com"
    zoho_smtp_server = "smtp.zoho.com"
    zoho_smtp_port = 587
    zoho_smtp_user = sender_email
    zoho_smtp_password = "7v7pi67S2Sy6"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = "Your OTP Code - Fenamaz Ecommerce"

    body = f"""
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            font-size: 20px;
            color: #333;
            margin: 0; 
            padding: 0; 
        }}
        .email-container {{
            width: 100%;
            background-color: #ffffff;
            padding: 20px;
            box-sizing: border-box; 
            margin: 0; 
            border-radius: 16px;
        }}
        .otp {{
            font-size: 32px;
            color: #007bff;
            font-weight: bold;
            padding: 10px;
            background-color: #f1f1f1;
            border-radius: 4px;
            text-align: center;
        }}
        .footer {{
            font-size: 14px;
            color: #888888;
            text-align: center;
        }}
        .footer a {{
            color: #007bff;
            text-decoration: none;
        }}
        p {{
            margin: 30px 0;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <p><strong>Dear Valued Customer,</strong></p>
        <p>Thank you for choosing <strong>Fenamaz Ecommerce</strong>, your trusted platform for technology and gadgets online shopping.</p>
        <p>We have received your request to authenticate your account. Please find your One-Time Password (OTP) below:</p>
        <div class="otp">{otp}</div>
        <p>Please enter this code in the mobile app to complete your registration process.</p>
        <p>If you have any concerns, please do not hesitate to contact us at <a href="mailto:fanamazecommerce@zohomail.com">fanamazecommerce@zohomail.com</a></p>
        <p>Thank you for choosing <strong>Fenamaz Ecommerce</strong>!</p>
        <p>Best regards, <br>The Fenamaz Team</p>
        <div class="footer">
            <p><br>&copy; {2024} Fenamaz Ecommerce | <a href="https://www.fenamazecommerce.com">www.fenamazecommerce.com</a></p>
        </div>
    </div>
</body>
</html>
    """

    msg.attach(MIMEText(body, 'html'))

    try:
        with smtplib.SMTP(zoho_smtp_server, zoho_smtp_port) as server:
            server.starttls()
            server.login(zoho_smtp_user, zoho_smtp_password)
            server.sendmail(sender_email, email, msg.as_string())
            print("OTP email sent successfully!")
    except Exception as e:
        print(f"Failed to send OTP email: {e}")

# Add this global dictionary to store OTP data (in production, use Redis or database)
forgot_password_tokens = {}

@mobile_api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for mobile app"""
    return jsonify({
        'status': 'success',
        'message': 'Fenamaz Ecommerce API is running',
        'version': '1.0.0'
    }), 200

@mobile_api_bp.route('/auth/login', methods=['POST'])
def mobile_login():
    """Mobile login endpoint for both buyer and courier"""
    data = request.get_json()
    
    if not data:
        return jsonify({
            'status': 'error',
            'message': 'No data provided'
        }), 400
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({
            'status': 'error',
            'message': 'Username and password are required'
        }), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({
            'status': 'error',
            'message': 'Database connection error'
        }), 500

    cursor = conn.cursor()
    cursor.execute("SELECT username, password, user_role, login_id FROM account_login_info WHERE username = %s", (username,))
    user = cursor.fetchone()

    if user and check_password_hash(user[1], password):
        role = user[2]
        
        # Only allow buyer and courier for mobile app
        if role not in ['Buyer', 'Courier']:
            conn.close()
            return jsonify({
                'status': 'error',
                'message': 'Mobile app is only for buyers and couriers'
            }), 403

        cursor.execute("""
            SELECT user_id, personal_id, address_id, valid_id, contact_id, login_id, business_id, profile_pic, status, date_created, user_role
            FROM user_account 
            WHERE login_id = %s
        """, (user[3],))
        user_info = cursor.fetchone()

        if user_info:
            status = user_info[8]
            
            if status == 'Approved':
                # Get personal info
                cursor.execute("SELECT firstname, lastname, sex, age, birthdate FROM account_personal_info WHERE personal_id = %s", (user_info[1],))
                personal_info = cursor.fetchone()
                
                # Get contact info
                cursor.execute("SELECT phone, email FROM account_contact_info WHERE contact_id = %s", (user_info[4],))
                contact_info = cursor.fetchone()

                conn.close()
                
                return jsonify({
                    'status': 'success',
                    'message': 'Login successful',
                    'data': {
                        'user_id': user_info[0],
                        'user_type': role.lower(),
                        'status': status,
                        'profile': {
                            'name': f"{personal_info[0]} {personal_info[1]}" if personal_info else "Unknown",
                            'email': contact_info[1] if contact_info else "",
                            'phone': contact_info[0] if contact_info else "",
                            'profile_pic': user_info[7]
                        }
                    }
                }), 200
            elif status == 'Banned':
                conn.close()
                return jsonify({
                    'status': 'error',
                    'message': 'Your account has been banned'
                }), 403
            elif status == 'Suspended':
                conn.close()
                return jsonify({
                    'status': 'error',
                    'message': 'Your account has been suspended'
                }), 403
            else:
                conn.close()
                return jsonify({
                    'status': 'error',
                    'message': 'Your account is pending approval'
                }), 403

    conn.close()
    return jsonify({
        'status': 'error',
        'message': 'Invalid username or password'
    }), 401

@mobile_api_bp.route('/auth/send-otp/<user_type>', methods=['POST'])
def send_registration_otp(user_type):
    """Send OTP for registration verification"""
    if user_type not in ['buyer', 'courier']:
        return jsonify({
            'status': 'error',
            'message': 'Invalid user type. Must be buyer or courier'
        }), 400
    
    data = request.get_json()
    if not data:
        return jsonify({
            'status': 'error',
            'message': 'No data provided'
        }), 400
    
    email = data.get('email')
    if not email:
        return jsonify({
            'status': 'error',
            'message': 'Email is required'
        }), 400

    # Generate OTP
    otp = random.randint(100000, 999999)
    
    # Store OTP in session (in production, use Redis or database)
    session['registration_otp'] = {
        'otp': otp,
        'email': email,
        'timestamp': datetime.now().isoformat(),
        'user_type': user_type
    }
    
    # Send OTP email
    send_otp_email(email, otp)
    
    return jsonify({
        'status': 'success',
        'message': f'OTP sent to {email}',
        'otp': str(otp)  # Remove this in production
    }), 200

@mobile_api_bp.route('/auth/register/<user_type>', methods=['POST'])
def mobile_register(user_type):
    """Mobile registration endpoint for buyer or courier with complete 6-step process"""
    if user_type not in ['buyer', 'courier']:
        return jsonify({
            'status': 'error',
            'message': 'Invalid user type. Must be buyer or courier'
        }), 400
    
    # Extract form data
    try:
        # Personal Information
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        sex = request.form.get('sex')
        birthdate_str = request.form.get('birthdate')
        
        # Address Information
        house_no = request.form.get('house_no')
        street = request.form.get('street', '')  # Optional
        barangay = request.form.get('barangay')
        city = request.form.get('city')
        province = request.form.get('province')
        region = request.form.get('region')
        
        # Contact Information
        phone = request.form.get('phone')
        email = request.form.get('email')
        
        # Valid ID Information
        id_type = request.form.get('id_type')
        id_no = request.form.get('id_no')
        id_pic = request.files.get('id_pic')
        
        # Login Information
        username = request.form.get('username')
        password = request.form.get('password')
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error parsing form data: {str(e)}'
        }), 400
    
    # Validate required fields
    required_fields = {
        'firstname': firstname,
        'lastname': lastname,
        'sex': sex,
        'birthdate': birthdate_str,
        'house_no': house_no,
        'barangay': barangay,
        'city': city,
        'province': province,
        'region': region,
        'phone': phone,
        'email': email,
        'id_type': id_type,
        'id_no': id_no,
        'username': username,
        'password': password
    }
    
    for field_name, field_value in required_fields.items():
        if not field_value:
            return jsonify({
                'status': 'error',
                'message': f'{field_name} is required'
            }), 400
    
    # Validate file upload
    if not id_pic:
        return jsonify({
            'status': 'error',
            'message': 'Valid ID picture is required'
        }), 400
    
    if not validate_file_extension(id_pic.filename):
        return jsonify({
            'status': 'error',
            'message': 'Invalid file type. Please upload PNG, JPG, or JPEG'
        }), 400
    
    if not validate_file_size(id_pic):
        return jsonify({
            'status': 'error',
            'message': 'File size too large. Maximum size is 5MB'
        }), 400
    
    # Validate email format
    if not validate_email(email):
        return jsonify({
            'status': 'error',
            'message': 'Invalid email format'
        }), 400
    
    # Check if email already exists
    if email_exists(email):
        return jsonify({
            'status': 'error',
            'message': 'Email already exists'
        }), 400
    
    # Validate phone format
    if not validate_phone(phone):
        return jsonify({
            'status': 'error',
            'message': 'Invalid phone number format (use 09XXXXXXXXX)'
        }), 400
    
    # Check if phone already exists
    if phone_exists(phone):
        return jsonify({
            'status': 'error',
            'message': 'Phone number already exists'
        }), 400
    
    # Check if ID number already exists
    if id_number_exists(id_no):
        return jsonify({
            'status': 'error',
            'message': f'ID number {id_no} already exists'
        }), 400
    
    # Validate password strength
    is_strong, password_message = validate_password_strength(password)
    if not is_strong:
        return jsonify({
            'status': 'error',
            'message': password_message
        }), 400
    
    # Validate names
    if not validate_name(firstname) or not validate_name(lastname):
        return jsonify({
            'status': 'error',
            'message': 'Names should only contain letters and spaces'
        }), 400
    
    # Validate age
    try:
        birthdate = datetime.strptime(birthdate_str, '%Y-%m-%d')
        today = datetime.today()
        age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
        if age < 18:
            return jsonify({
                'status': 'error',
                'message': 'You must be 18 years old or above'
            }), 400
    except ValueError:
        return jsonify({
            'status': 'error',
            'message': 'Invalid birthdate format'
        }), 400
    
    # Save uploaded file
    try:
        temp_token = secrets.token_urlsafe(16)
        filename = f"{temp_token}_{secure_filename(id_pic.filename)}"
        if user_type == 'buyer':
            file_path = os.path.join(BUYER_ID_UPLOAD_FOLDER, filename)
        else:
            file_path = os.path.join(COURIER_ID_UPLOAD_FOLDER, filename)
        id_pic.save(file_path)
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to save ID picture: {str(e)}'
        }), 500
    
    # Insert data into database
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'status': 'error',
                'message': 'Database connection error'
            }), 500
        
        cursor = conn.cursor()
        cursor.execute("START TRANSACTION;")
        
        # Hash password
        hashed_password = generate_password_hash(password)
        
        # Insert personal info
        cursor.execute("""
            INSERT INTO account_personal_info (firstname, lastname, sex, age, birthdate)
            VALUES (%s, %s, %s, %s, %s)
        """, (firstname, lastname, sex, age, birthdate_str))
        personal_id = cursor.lastrowid
        
        # Insert address info
        cursor.execute("""
            INSERT INTO account_address_info (house_no, street, barangay, city, province, region)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (house_no, street, barangay, city, province, region))
        address_id = cursor.lastrowid
        
        # Insert contact info
        cursor.execute("""
            INSERT INTO account_contact_info (email, phone)
            VALUES (%s, %s)
        """, (email, phone))
        contact_id = cursor.lastrowid
        
        # Insert valid info
        cursor.execute("""
            INSERT INTO account_valid_info (id_type, id_no, id_pic)
            VALUES (%s, %s, %s)
        """, (id_type, id_no, filename))
        valid_id = cursor.lastrowid
        
        # Insert login info
        cursor.execute("""
            INSERT INTO account_login_info (username, password, user_role)
            VALUES (%s, %s, %s)
        """, (username, hashed_password, user_type.capitalize()))
        login_id = cursor.lastrowid
        
        # Insert user account
        status = 'Pending' if user_type == 'courier' else 'Approved'
        cursor.execute("""
            INSERT INTO user_account (personal_id, address_id, contact_id, valid_id, login_id, 
                                    user_role, status, date_created)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
        """, (personal_id, address_id, contact_id, valid_id, login_id, user_type.capitalize(), status))
        user_id = cursor.lastrowid
        
        # Add notifications following the web registration pattern
        admin_id = 1
        if user_type == 'courier':
            # Notify admin for courier registration
            admin_notification_message = f"A new courier has successfully registered and is waiting for your approval. Check Now!"
            admin_notification_type = f"New Courier Registration - {firstname} {lastname}"
            
            cursor.execute("""
                INSERT INTO notifications (recipient_id, sender_id, notification_type, notification_title, content, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """, (admin_id, user_id, 'Account Registration', admin_notification_type, admin_notification_message, 'Unread'))
        else:
            # Notify admin and buyer for buyer registration
            admin_notification_message = f"A new buyer has successfully registered and is waiting for your approval. Check Now!"
            admin_notification_type = f"New Buyer Registration - {firstname} {lastname}"
            
            buyer_notification_message = ("Congratulations! 🎉 Your buyer account registration has been created successfully. "
                                        "You can now explore a wide range of the latest products in technology, gadgets, and more.")
            
            cursor.execute("""
                INSERT INTO notifications (recipient_id, sender_id, notification_type, notification_title, content, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """, (admin_id, user_id, 'Account Registration', admin_notification_type, admin_notification_message, 'Unread'))
            
            cursor.execute("""
                INSERT INTO notifications (recipient_id, sender_id, notification_type, notification_title, content, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """, (user_id, admin_id, 'Account Registration', 'Registration Success', buyer_notification_message, 'Unread'))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'message': f'{user_type.capitalize()} registration successful',
            'data': {
                'user_id': user_id,
                'status': status,
                'requires_approval': user_type == 'courier'
            }
        }), 201
        
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        # Delete uploaded file if database insert fails
        try:
            os.remove(file_path)
        except:
            pass
        print(f"Registration error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Registration failed: {str(e)}'
        }), 500

@mobile_api_bp.route('/auth/register/validate', methods=['POST'])
def validate_registration_data():
    """Validate registration data"""
    data = request.get_json()
    
    if not data:
        return jsonify({
            'status': 'error',
            'message': 'No data provided'
        }), 400
    
    errors = []
    
    # Validate email
    email = data.get('email')
    if email:
        if not validate_email(email):
            errors.append('Invalid email format')
        elif email_exists(email):
            errors.append('Email already exists')
    
    # Validate phone
    phone = data.get('phone')
    if phone:
        if not validate_phone(phone):
            errors.append('Invalid phone number format (use 09XXXXXXXXX)')
        elif phone_exists(phone):
            errors.append('Phone number already exists')
    
    # Validate password
    password = data.get('password')
    if password:
        is_strong, message = validate_password_strength(password)
        if not is_strong:
            errors.append(message)
    
    # Validate names
    firstname = data.get('firstname')
    lastname = data.get('lastname')
    if firstname and not validate_name(firstname):
        errors.append('First name should only contain letters and spaces')
    if lastname and not validate_name(lastname):
        errors.append('Last name should only contain letters and spaces')
    
    # Validate age
    birthdate_str = data.get('birthdate')
    if birthdate_str:
        try:
            birthdate = datetime.strptime(birthdate_str, '%Y-%m-%d')
            today = datetime.today()
            age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
            if age < 18:
                errors.append('You must be 18 years old or above')
        except ValueError:
            errors.append('Invalid birthdate format')
    
    if errors:
        return jsonify({
            'status': 'error',
            'message': 'Validation failed',
            'errors': errors
        }), 400
    
    return jsonify({
        'status': 'success',
        'message': 'Validation passed'
    }), 200

@mobile_api_bp.route('/user/profile', methods=['GET'])
def get_user_profile():
    """Get user profile for mobile app"""
    # TODO: Implement actual profile logic with authentication
    return jsonify({
        'status': 'success',
        'message': 'Profile endpoint ready',
        'data': {
            'user_id': None,
            'name': 'Test User',
            'email': 'test@example.com'
        }
    }), 200

@mobile_api_bp.route('/products', methods=['GET'])
def get_products():
    """Get products for mobile app"""
    # TODO: Implement actual products logic
    return jsonify({
        'status': 'success',
        'message': 'Products endpoint ready',
        'data': []
    }), 200

@mobile_api_bp.route('/auth/forgot-password', methods=['POST'])
def mobile_forgot_password():
    """Mobile forgot password - send OTP to email"""
    data = request.get_json()
    
    if not data:
        return jsonify({
            'status': 'error',
            'message': 'No data provided'
        }), 400
    
    email = data.get('email')
    if not email:
        return jsonify({
            'status': 'error',
            'message': 'Email is required'
        }), 400

    # Validate email format
    if not validate_email(email):
        return jsonify({
            'status': 'error',
            'message': 'Invalid email format'
        }), 400

    # Check if email exists
    if not email_exists(email):
        return jsonify({
            'status': 'error',
            'message': 'Email not found. Please try again.'
        }), 404

    # Generate OTP and token
    otp = random.randint(100000, 999999)
    token = secrets.token_urlsafe(32)
    
    # Store OTP data with token as key (expires in 30 minutes)
    forgot_password_tokens[token] = {
        'otp': otp,
        'email': email,
        'timestamp': datetime.now(),
        'verified': False
    }
    
    # Clean up expired tokens (older than 30 minutes)
    current_time = datetime.now()
    expired_tokens = [t for t, data in forgot_password_tokens.items() 
                     if current_time - data['timestamp'] > timedelta(minutes=30)]
    for expired_token in expired_tokens:
        del forgot_password_tokens[expired_token]
    
    # Send OTP email with forgot password template
    send_forgot_password_otp_email(email, otp)
    
    return jsonify({
        'status': 'success',
        'message': f'Password reset OTP sent to {email}',
        'token': token,  # Send token to client
        'otp': str(otp)  # Remove this in production
    }), 200

@mobile_api_bp.route('/auth/verify-forgot-otp', methods=['POST'])
def mobile_verify_forgot_otp():
    """Verify OTP for forgot password"""
    data = request.get_json()
    
    if not data:
        return jsonify({
            'status': 'error',
            'message': 'No data provided'
        }), 400
    
    entered_otp = data.get('otp')
    token = data.get('token')
    
    if not entered_otp or not token:
        return jsonify({
            'status': 'error',
            'message': 'OTP and token are required'
        }), 400

    # Check if token exists
    if token not in forgot_password_tokens:
        return jsonify({
            'status': 'error',
            'message': 'Session expired. Please request OTP again.'
        }), 400

    token_data = forgot_password_tokens[token]
    
    # Check OTP expiry (30 minutes)
    if datetime.now() - token_data['timestamp'] > timedelta(minutes=30):
        del forgot_password_tokens[token]
        return jsonify({
            'status': 'error',
            'message': 'OTP expired. Please request a new one.'
        }), 400

    if int(entered_otp) == token_data['otp']:
        # Mark OTP as verified
        forgot_password_tokens[token]['verified'] = True
        return jsonify({
            'status': 'success',
            'message': 'OTP verified successfully',
            'token': token  # Return token for next step
        }), 200
    else:
        return jsonify({
            'status': 'error',
            'message': 'Invalid OTP. Please try again.'
        }), 400

@mobile_api_bp.route('/auth/reset-password', methods=['POST'])
def mobile_reset_password():
    """Reset password after OTP verification"""
    data = request.get_json()
    
    if not data:
        return jsonify({
            'status': 'error',
            'message': 'No data provided'
        }), 400
    
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')
    token = data.get('token')
    
    if not new_password or not confirm_password or not token:
        return jsonify({
            'status': 'error',
            'message': 'New password, confirm password and token are required'
        }), 400

    if new_password != confirm_password:
        return jsonify({
            'status': 'error',
            'message': 'Passwords do not match'
        }), 400

    # Validate password strength
    is_strong, password_message = validate_password_strength(new_password)
    if not is_strong:
        return jsonify({
            'status': 'error',
            'message': password_message
        }), 400

    # Check if token exists and OTP was verified
    if token not in forgot_password_tokens:
        return jsonify({
            'status': 'error',
            'message': 'Session expired. Please try again.'
        }), 400

    token_data = forgot_password_tokens[token]
    
    if not token_data.get('verified'):
        return jsonify({
            'status': 'error',
            'message': 'Please verify OTP first.'
        }), 400

    email = token_data['email']

    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'status': 'error',
                'message': 'Database connection error'
            }), 500

        cursor = conn.cursor()
        
        # Hash the new password
        hashed_password = generate_password_hash(new_password)
        
        # Update password in database
        cursor.execute("""
            UPDATE account_login_info ali
            INNER JOIN user_account ua ON ali.login_id = ua.login_id
            INNER JOIN account_contact_info aci ON ua.contact_id = aci.contact_id
            SET ali.password = %s 
            WHERE aci.email = %s
        """, (hashed_password, email))

        if cursor.rowcount == 0:
            conn.close()
            return jsonify({
                'status': 'error',
                'message': 'Failed to update password. Please try again.'
            }), 500

        conn.commit()
        conn.close()

        # Clear token data
        del forgot_password_tokens[token]

        return jsonify({
            'status': 'success',
            'message': 'Your password has been reset successfully!'
        }), 200

    except Exception as e:
        if conn:
            conn.close()
        print(f"Reset password error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'An error occurred. Please try again later.'
        }), 500

@mobile_api_bp.route('/auth/resend-forgot-otp', methods=['POST'])
def mobile_resend_forgot_otp():
    """Resend OTP for forgot password"""
    data = request.get_json()
    
    if not data:
        return jsonify({
            'status': 'error',
            'message': 'No data provided'
        }), 400
    
    token = data.get('token')
    
    if not token or token not in forgot_password_tokens:
        return jsonify({
            'status': 'error',
            'message': 'Session expired. Please request OTP again.'
        }), 400

    token_data = forgot_password_tokens[token]
    email = token_data['email']

    # Generate new OTP
    otp = random.randint(100000, 999999)
    
    # Update token data
    forgot_password_tokens[token] = {
        'otp': otp,
        'email': email,
        'timestamp': datetime.now(),
        'verified': False
    }
    
    # Send OTP email
    send_forgot_password_otp_email(email, otp)
    
    return jsonify({
        'status': 'success',
        'message': f'OTP has been resent to {email}',
        'otp': str(otp)  # Remove this in production
    }), 200

def send_forgot_password_otp_email(email, otp):
    """Send OTP email for forgot password"""
    sender_email = "fanamazecommerce@zohomail.com"
    zoho_smtp_server = "smtp.zoho.com"
    zoho_smtp_port = 587
    zoho_smtp_user = sender_email
    zoho_smtp_password = "7v7pi67S2Sy6"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = "Password Reset OTP - Fenamaz Ecommerce"

    body = f"""
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            font-size: 20px;
            color: #333;
            margin: 0; 
            padding: 0; 
        }}
        .email-container {{
            width: 100%;
            background-color: #ffffff;
            padding: 20px;
            box-sizing: border-box; 
            margin: 0; 
            border-radius: 16px;
        }}
        .otp {{
            font-size: 32px;
            color: #007bff;
            font-weight: bold;
            padding: 10px;
            background-color: #f1f1f1;
            border-radius: 4px;
            text-align: center;
        }}
        .footer {{
            font-size: 14px;
            color: #888888;
            text-align: center;
        }}
        .footer a {{
            color: #007bff;
            text-decoration: none;
        }}
        p {{
            margin: 30px 0;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <p><strong>Dear Valued Customer,</strong></p>
        <p>We received a request to change your password for your <strong>Fenamaz Ecommerce</strong> account.</p>
        <p>To proceed with the password reset process, please use the One-Time Password (OTP) provided below:</p>
        <div class="otp">{otp}</div>
        <p>Enter this code on the password reset page to confirm your request and change your password.</p>
        <p>If you did not request a password change, please ignore this email or contact our support team for assistance.</p>
        <p>If you have any concerns or need help, feel free to reach out to us at <a href="mailto:fanamazecommerce@zohomail.com">fanamazecommerce@zohomail.com</a></p>
        <p>Thank you for trusting <strong>Fenamaz Ecommerce</strong>!</p>
        <p>Best regards, <br>The Fenamaz Team</p>
        <div class="footer">
            <p><br>&copy; {2024} Fenamaz Ecommerce | <a href="https://www.fenamazecommerce.com">www.fenamazecommerce.com</a></p>
        </div>
    </div>
</body>
</html>
    """

    msg.attach(MIMEText(body, 'html'))

    try:
        with smtplib.SMTP(zoho_smtp_server, zoho_smtp_port) as server:
            server.starttls()
            server.login(zoho_smtp_user, zoho_smtp_password)
            server.sendmail(sender_email, email, msg.as_string())
            print("Forgot password OTP email sent successfully!")
    except Exception as e:
        print(f"Failed to send forgot password OTP email: {e}") 