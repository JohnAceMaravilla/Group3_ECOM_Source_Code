# IMPORTS
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_from_directory, abort
from datetime import datetime
from db_connection import get_db_connection
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import random
import os
import secrets
import mysql.connector
import re

buyer_registration_bp = Blueprint('buyer_registration', __name__)


# FOLDER FOR STORING IMAGES
VALID_ID_UPLOAD_FOLDER = "static/uploads/buyer/valid_id_pic" 
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


# ENSURE FOLDER EXISTS
if not os.path.exists(VALID_ID_UPLOAD_FOLDER):
    os.makedirs(VALID_ID_UPLOAD_FOLDER)


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

def validate_file_extension(filename):
    """Validate file extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_file_size(file):
    """Validate file size (max 5MB)"""
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB in bytes
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    return size <= MAX_FILE_SIZE


# GET PERSONAL INFO
@buyer_registration_bp.route('/buyer_registration/personal_info', methods=['GET', 'POST'])
def get_personal_info():
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        sex = request.form.get('sex')
        birthdate_str = request.form.get('birthdate')

        # Validate inputs
        if not firstname or not lastname:
            flash("First name and last name are required.", "danger")
            return redirect(url_for('buyer_registration.get_personal_info'))

        if not validate_name(firstname) or not validate_name(lastname):
            flash("Names should only contain letters and spaces.", "danger")
            return redirect(url_for('buyer_registration.get_personal_info'))

        if not sex:
            flash("Please select your sex.", "danger")
            return redirect(url_for('buyer_registration.get_personal_info'))

        if not birthdate_str:
            flash("Please enter your birthdate.", "danger")
            return redirect(url_for('buyer_registration.get_personal_info'))

        try:
            birthdate = datetime.strptime(birthdate_str, '%Y-%m-%d')
            today = datetime.today()
            age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

            if age < 18:
                flash("You must be 18 years old or above to create an account.", "danger")
                return redirect(url_for('buyer_registration.get_personal_info'))

        except ValueError:
            flash("Invalid birthdate format.", "danger")
            return redirect(url_for('buyer_registration.get_personal_info'))

        session['personal_info'] = {
            'firstname': firstname,
            'lastname': lastname,
            'sex': sex,
            'age': age,
            'birthdate': birthdate_str
        }

        return redirect(url_for('buyer_registration.get_address_info'))
    
    return render_template('reg_buyer_personal_info.html')


# GET ADDRESS INFO
@buyer_registration_bp.route('/buyer_registration/address_info', methods=['GET', 'POST'])
def get_address_info():
    if request.method == 'POST':
        house_no = request.form.get('house_no')
        street = request.form.get('street_text')
        brgy = request.form.get('barangay_text')
        city = request.form.get('city_text')
        province = request.form.get('province_text')
        region = request.form.get('region_text')

        # Validate inputs
        if not all([house_no, street, brgy, city, province, region]):
            flash("All address fields are required.", "danger")
            return redirect(url_for('buyer_registration.get_address_info'))

        session['address_info'] = {
            'house_no': house_no,
            'street': street,
            'brgy': brgy,
            'city': city,
            'province': province,
            'region': region
        }

        return redirect(url_for('buyer_registration.get_contact_info'))
    
    return render_template('reg_buyer_address_info.html')


# GET CONTACT INFO
@buyer_registration_bp.route('/buyer_registration/contact_info', methods=['GET', 'POST'])
def get_contact_info():
    if request.method == 'POST':
        phone = request.form.get('phone')
        email = request.form.get('email')

        # Validate inputs
        if not phone or not email:
            flash("Phone number and email are required.", "danger")
            return redirect(url_for('buyer_registration.get_contact_info'))

        if not validate_phone(phone):
            flash("Invalid phone number format. Must be 09XXXXXXXXX format.", "danger")
            return redirect(url_for('buyer_registration.get_contact_info'))

        if not validate_email(email):
            flash("Invalid email format.", "danger")
            return redirect(url_for('buyer_registration.get_contact_info'))

        if email_exists(email):
            flash("Email already exists. Please try a different one.", "danger")
            return redirect(url_for('buyer_registration.get_contact_info'))
        
        if phone_exists(phone):
            flash("Phone number already exists. Please try a different one.", "danger")
            return redirect(url_for('buyer_registration.get_contact_info'))
        
        session['contact_info'] = {
            'phone': phone,
            'email': email
        }

        return redirect(url_for('buyer_registration.get_valid_info'))
    
    return render_template('reg_buyer_contact_info.html')


# CHECK IF EMAIL EXISTS
def email_exists(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM account_contact_info WHERE email = %s", (email,))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0


# CHECK IF PHONE EXISTS
def phone_exists(phone):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM account_contact_info WHERE phone = %s", (phone,))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0


# SEND OTP TO EMAIL
def send_otp_email(email, otp):
    sender_email = "fanamazecommerce@zohomail.com"
    zoho_smtp_server = "smtp.zoho.com"
    zoho_smtp_port = 587
    zoho_smtp_user = sender_email
    zoho_smtp_password = "7v7pi67S2Sy6"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = "Your OTP Code - Fenamaz Ecommerce" 

    # Email Body
    body = f"""
<html>
<head>
    <style>
        html, body {{
            margin: 0;
            padding: 0;
            width: 100%;
        }}
        
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
        <p>Please enter this code on the registration to complete your authentication process.</p>
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
            print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")


# CHECK IF VALID ID EXISTS
def valid_id_exists(id_no):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM account_valid_info WHERE id_no = %s", (id_no,))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0


# GET VALID INFO
@buyer_registration_bp.route('/buyer_registration/valid_info', methods=['GET', 'POST'])
def get_valid_info():
    if request.method == 'POST':
        id_type = request.form.get('id_type')
        id_no = request.form.get('id_no')
        id_pic = request.files.get('id_pic')

        # Validate inputs
        if not id_type or not id_no:
            flash("ID type and number are required.", "danger")
            return redirect(url_for('buyer_registration.get_valid_info'))

        if not id_pic:
            flash('Valid ID picture is required.', 'danger')
            return redirect(url_for('buyer_registration.get_valid_info'))

        if not validate_file_extension(id_pic.filename):
            flash('Invalid file type. Please re-upload your valid ID picture (png, jpg, jpeg).', 'danger')
            return redirect(url_for('buyer_registration.get_valid_info'))

        if not validate_file_size(id_pic):
            flash('File size too large. Maximum size is 5MB.', 'danger')
            return redirect(url_for('buyer_registration.get_valid_info'))

        if valid_id_exists(id_no):
            flash(f"Valid ID with no {id_no} already exists. Please use a different one.", "danger")
            return redirect(url_for('buyer_registration.get_valid_info'))

        temp_token = secrets.token_urlsafe(16)
        filename = f"{temp_token}_{secure_filename(id_pic.filename)}"
        file_path = os.path.join(VALID_ID_UPLOAD_FOLDER, filename)
        id_pic.save(file_path)

        session['valid_info'] = {
            'id_type': id_type,
            'id_no': id_no,
            'id_pic': filename,
            'token': temp_token 
        }

        return redirect(url_for('buyer_registration.get_login_info'))
    
    return render_template('reg_buyer_valid_info.html')


# GET IMAGE
@buyer_registration_bp.route('/get_image/<filename>')
def get_image(filename):
    valid_info = session.get('valid_info')

    if not valid_info or 'token' not in valid_info:
        abort(403) 

    if filename != valid_info['id_pic']:
        abort(403)

    return send_from_directory(VALID_ID_UPLOAD_FOLDER, filename)


# GET LOGIN INFO
@buyer_registration_bp.route('/buyer_registration/login_info', methods=['GET', 'POST'])
def get_login_info():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate inputs
        if not username or not password or not confirm_password:
            flash("All fields are required.", "danger")
            return redirect(url_for('buyer_registration.get_login_info'))

        if not validate_email(username):
            flash("Username must be a valid email address.", "danger")
            return redirect(url_for('buyer_registration.get_login_info'))

        is_valid_password, password_message = validate_password_strength(password)
        if not is_valid_password:
            flash(password_message, "danger")
            return redirect(url_for('buyer_registration.get_login_info'))

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for('buyer_registration.get_login_info'))

        session['login_info'] = {
            'username': username,
            'password': generate_password_hash(password)  # Hash the password before storing
        }
        
        otp = random.randint(100000, 999999)
        session['otp'] = otp
        send_otp_email(username, otp)
        
        return redirect(url_for('buyer_registration.get_verification'))
    
    return render_template('reg_buyer_login_info.html')


# GET VERIFICATION
@buyer_registration_bp.route('/buyer_registration/verification', methods=['GET', 'POST'])
def get_verification():
    if request.method == 'POST':
        entered_otp = request.form.get('otp')

        if int(entered_otp) == session.get('otp'):
            insert_data()
            
            user_email = session.get('contact_info')['email'] 
            user_name = session.get('personal_info')['firstname'] 
            send_registration_success_email(user_email, user_name)
            
            session.pop('personal_info', None)
            session.pop('address_info', None)
            session.pop('contact_info', None)
            session.pop('valid_info', None)
            session.pop('login_info', None)
            session.pop('otp', None)
            return redirect(url_for('login.success'))
        else:
            flash("Invalid OTP. Please try again.", "danger")
            return redirect(url_for('buyer_registration.get_verification'))
    
    return render_template('reg_buyer_verification.html')


# RESEND OTP
@buyer_registration_bp.route('/buyer_registration/resend_otp', methods=['GET'])
def resend_registration_otp():
    email = session.get('contact_info', {}).get('email')

    if not email or 'otp' not in session:
        flash("Session expired. Please request OTP again.", "danger")
        return redirect(url_for('buyer_registration.get_login_info'))  

    otp = session.get('otp')  

    send_otp_email(email, otp)

    flash("OTP has been resent to your email!", "success")
    return redirect(url_for('buyer_registration.get_verification')) 


# INSERT DATA TO DATABASE
def insert_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        personal_info = session.get('personal_info')
        address_info = session.get('address_info')
        contact_info = session.get('contact_info')
        valid_info = session.get('valid_info')
        login_info = session.get('login_info')

        cursor.execute("START TRANSACTION;")

        # Insert into Personal Info
        cursor.execute("""
            INSERT INTO account_personal_info (firstname, lastname, sex, age, birthdate)
            VALUES (%s, %s, %s, %s, %s)""",
            (personal_info['firstname'], personal_info['lastname'], personal_info['sex'], 
             personal_info['age'], personal_info['birthdate'])
        )
        personal_id = cursor.lastrowid

        # Insert into Address Info
        cursor.execute("""
            INSERT INTO account_address_info (house_no, street, barangay, city, province, region)
            VALUES (%s, %s, %s, %s, %s, %s)""",
            (address_info['house_no'], address_info['street'], address_info['brgy'], address_info['city'], 
             address_info['province'], address_info['region'])
        )
        address_id = cursor.lastrowid

        # Insert into Contact Info
        cursor.execute("""
            INSERT INTO account_contact_info (email, phone)
            VALUES (%s, %s)""",
            (contact_info['email'], contact_info['phone'])
        )
        contact_id = cursor.lastrowid
        
        # Insert into Valid Info - Store file path instead of blob
        cursor.execute("""
            INSERT INTO account_valid_info (id_type, id_no, id_pic)
            VALUES (%s, %s, %s)""",
            (valid_info['id_type'], valid_info['id_no'], valid_info['id_pic'])
        )
        valid_id = cursor.lastrowid

        # Insert into Login Info
        cursor.execute("""
            INSERT INTO account_login_info (username, password, user_role)
            VALUES (%s, %s, 'Buyer')""",
            (login_info['username'], login_info['password'])
        )
        login_id = cursor.lastrowid

        # Insert into Buyer Account
        cursor.execute("""
            INSERT INTO user_account (personal_id, address_id, contact_id, valid_id, login_id, user_role, status, date_created)
            VALUES (%s, %s, %s, %s, %s, 'Buyer', 'Approved', NOW())""",
            (personal_id, address_id, contact_id, valid_id, login_id)
        )
        buyer_id = cursor.lastrowid
        
        # Notification
        admin_id = 1
        admin_notification_message = (
            f"A new buyer has successfully registered and is waiting for your approval. Check Now!"
        )
        admin_notification_type = (
            f"New Buyer Registration - {personal_info['firstname']} {personal_info['lastname']}"
        )
        
        buyer_notification_message = (
            "Congratulations! 🎉 Your buyer account registration has been created successfully. "
            "You can now explore a wide range of the latest products in technology, gadgets, and more."
        )
        
        # Insert Admin Notifications
        cursor.execute(""" 
            INSERT INTO notifications (recipient_id, sender_id, notification_type, notification_title, content, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())""",
            (admin_id, buyer_id, 'Account Registration', admin_notification_type, admin_notification_message, 'Unread')
        )
        
        # Insert Buyer Notifications
        cursor.execute(""" 
            INSERT INTO notifications (recipient_id, sender_id, notification_type, notification_title, content, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())""",
            (buyer_id, admin_id, 'Account Registration', 'Registration Success', buyer_notification_message, 'Unread')
        )

        conn.commit()
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


# SEND EMAIL REGISTRATION SUCCESS
def send_registration_success_email(email, name):
    sender_email = "fanamazecommerce@zohomail.com"
    zoho_smtp_server = "smtp.zoho.com"
    zoho_smtp_port = 587
    zoho_smtp_user = sender_email
    zoho_smtp_password = "7v7pi67S2Sy6"  

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = "Registration Successful - Fenamaz Ecommerce" 

    # Email Body 
    body = f"""
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            color: #333;
        }}
        .container {{
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 10px;
            margin: 20px;
        }}
        .header {{
            background-image: url("static/img/cover/cover.jpg");
            background-position: center; 
            background-repeat: no-repeat;
            background-size: cover;
            color: white;
            padding: 10px;
            border-radius: 10px;
            text-align: center;
        }}
        .footer {{
            font-size: 12px;
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
        .blue {{
            color: #007bff;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="container">  
        <div class="header">
            <h1><strong class="blue">Welcome to Fenamaz!</strong></h1>
        </div>      
        <p><strong>Hi!, {name},</strong></p>
        <p>We are excited to inform you that your registration with <strong>Fenamaz Ecommerce</strong> has been <strong class="blue">successfully completed.<strong></p>
        <p>Thank you for choosing Fenamaz Ecommerce. You can now explore a wide range of the latest products in technology, gadgets, and more.</p>
        <p>If you have any questions or need assistance, please do not hesitate to contact our support team at <a href="mailto:fanamazecommerce@zohomail.com">fanamazecommerce@zohomail.com</a>.</p>
        <p>We look forward to serving you and ensuring you have a smooth shopping experience!</p>
        <p>Best regards,<br>The Fenamaz Team</p>
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
    except Exception as e:
        print(f"Failed to send email: {e}")
