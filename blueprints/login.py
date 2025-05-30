# IMPORTS
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from db_connection import get_db_connection
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import random

login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_role' in session and session.get('status') == 'Approved':
        role = session.get('user_role')
        if role == 'Admin':
            return redirect(url_for('admin_dashboard.dashboard'))
        elif role == 'Seller':
            return redirect(url_for('seller_dashboard.dashboard'))
        elif role == 'Buyer':
            return redirect(url_for('buyer_homepage.show_buyer_homepage'))
        elif role == 'Courier':
            return redirect(url_for('courier_dashboard.dashboard'))
        
    login_success = False
    user_role = None 

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        ip_address = request.remote_addr

        if too_many_failed_attempts(username, ip_address):
            flash("Too many failed login attempts. Please try again after 10 minutes.", "danger")
            return redirect(url_for('login.login'))
        
        conn = get_db_connection()
        if not conn:
            flash("Database connection error.", "danger")
            return redirect(url_for('login.login'))

        cursor = conn.cursor()
        cursor.execute("SELECT username, password, user_role, login_id FROM account_login_info WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user[1], password):
            role = user[2]
            user_role = role

            cursor.execute("""
                SELECT user_id, personal_id, address_id, valid_id, contact_id, login_id, business_id, profile_pic, status, date_created, user_role
                FROM user_account 
                WHERE login_id = %s
            """, (user[3],))
            user_info = cursor.fetchone()

            if user_info:
                status = user_info[8]
                record_login_attempt(user_info[0], username, ip_address, role, 'success')

                if status == 'Approved':
                    session.permanent = True
                    session['login_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    if role == 'Buyer':
                        session['buyer'] = user_info[0]
                    elif role == 'Seller':
                        session['seller'] = user_info[0]
                    elif role == 'Courier':
                        session['courier'] = user_info[0]
                    elif role == 'Admin':
                        session['admin'] = user_info[0]
                        
                    session['personal_info'] = user_info[1] 
                    session['address_info'] = user_info[2]  
                    session['valid_info'] = user_info[3]  
                    session['contact_info'] = user_info[4]  
                    session['business_info'] = user_info[6] 
                    session['profile_pic'] = user_info[7] if user_info[7] else None  
                    session['status'] = user_info[8]  
                    session['date_created'] = user_info[9]  
                    session['user_role'] = user_info[10] 
                    
                    login_success = True

                elif status == 'Banned':
                    return redirect(url_for('login.banned'))
                elif status == 'Suspended':
                    return redirect(url_for('login.suspended'))
                else:
                    return redirect(url_for('login.pending'))

            else:
                record_login_attempt(None, username, ip_address, role, 'failed')
                flash("Account details not found", "danger")
                return redirect(url_for('login.login'))

        else:
            record_login_attempt(None, username, ip_address, None, 'failed')
            flash("Invalid username or password", "danger")
            return redirect(url_for('login.login'))

    return render_template('login.html', login_success=login_success, user_role=user_role)


# RECORD LOGIN ATTEMPT
def record_login_attempt(user_id, email, ip_address, user_type, status):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO login_attempts (user_id, email, ip_address, user_type, status, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, email, ip_address, user_type, status, datetime.now()))
            conn.commit()
        except Exception as e:
            print(f"Error logging login attempt: {e}")
        finally:
            cursor.close()
            conn.close()
            

# TOO MANY FAILED ATTEMPTS
def too_many_failed_attempts(email, ip_address, max_attempts=5, within_minutes=10):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            time_threshold = datetime.now() - timedelta(minutes=within_minutes)

            cursor.execute("""
                SELECT COUNT(*) FROM login_attempts
                WHERE (email = %s OR ip_address = %s) AND status = 'failed' AND timestamp >= %s
            """, (email, ip_address, time_threshold))

            result = cursor.fetchone()
            return result[0] >= max_attempts
        except Exception as e:
            print(f"Error checking login attempts: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    return False
            
            
# LOG OUT
@login_bp.route('/logout')
def logout():
    session.clear()
    flash("You've been logged out successfully!", "success")
    return redirect(url_for('login.login'))


# USER TERMS
@login_bp.route('/user_terms', methods=['GET', 'POST'])
def show_user_terms():
    if 'user_role' in session and session.get('status') == 'Approved':
        role = session.get('user_role')
        if role == 'Admin':
            return redirect(url_for('admin_dashboard.dashboard'))
        elif role == 'Seller':
            return redirect(url_for('seller_dashboard.dashboard'))
        elif role == 'Buyer':
            return redirect(url_for('buyer_homepage.show_buyer_homepage'))
        elif role == 'Courier':
            return redirect(url_for('courier_dashboard.dashboard'))
        
    if request.method == 'POST':
        terms_agreement = request.form.get('terms_agreement')

        if terms_agreement:
            return redirect(url_for('login.user_choose'))
        else:
            flash("You must agree to the Terms of Use to proceed.", "danger")
            return redirect(url_for('login.show_user_terms'))  
    
    return render_template('reg_user_terms.html')


# USER CHOOSE
@login_bp.route('/registration')
def user_choose():
    
    if 'user_role' in session and session.get('status') == 'Approved':
        role = session.get('user_role')
        if role == 'Admin':
            return redirect(url_for('admin_dashboard.dashboard'))
        elif role == 'Seller':
            return redirect(url_for('seller_dashboard.dashboard'))
        elif role == 'Buyer':
            return redirect(url_for('buyer_homepage.show_buyer_homepage'))
        elif role == 'Courier':
            return redirect(url_for('courier_dashboard.dashboard'))
        
    return render_template('reg_user_choose.html')


# ACCOUNT SUCCESS
@login_bp.route('/account_success')
def success():
    
    if 'user_role' in session and session.get('status') == 'Approved':
        role = session.get('user_role')
        if role == 'Admin':
            return redirect(url_for('admin_dashboard.dashboard'))
        elif role == 'Seller':
            return redirect(url_for('seller_dashboard.dashboard'))
        elif role == 'Buyer':
            return redirect(url_for('buyer_homepage.show_buyer_homepage'))
        elif role == 'Courier':
            return redirect(url_for('courier_dashboard.dashboard'))
    
    return render_template('account_success.html')


# ACCOUNT PENDING
@login_bp.route('/account_pending')
def pending():
    
    if 'user_role' in session and session.get('status') == 'Approved':
        role = session.get('user_role')
        if role == 'Admin':
            return redirect(url_for('admin_dashboard.dashboard'))
        elif role == 'Seller':
            return redirect(url_for('seller_dashboard.dashboard'))
        elif role == 'Buyer':
            return redirect(url_for('buyer_homepage.show_buyer_homepage'))
        elif role == 'Courier':
            return redirect(url_for('courier_dashboard.dashboard'))
    
    return render_template('account_pending.html')


# ACCOUNT SUSPENDED
@login_bp.route('/account_suspended')
def suspended():
    
    if 'user_role' in session and session.get('status') == 'Approved':
        role = session.get('user_role')
        if role == 'Admin':
            return redirect(url_for('admin_dashboard.dashboard'))
        elif role == 'Seller':
            return redirect(url_for('seller_dashboard.dashboard'))
        elif role == 'Buyer':
            return redirect(url_for('buyer_homepage.show_buyer_homepage'))
        elif role == 'Courier':
            return redirect(url_for('courier_dashboard.dashboard'))
    
    return render_template('account_suspended.html')


# ACCOUNT BANNED
@login_bp.route('/account_banned')
def banned():
    
    if 'user_role' in session and session.get('status') == 'Approved':
        role = session.get('user_role')
        if role == 'Admin':
            return redirect(url_for('admin_dashboard.dashboard'))
        elif role == 'Seller':
            return redirect(url_for('seller_dashboard.dashboard'))
        elif role == 'Buyer':
            return redirect(url_for('buyer_homepage.show_buyer_homepage'))
        elif role == 'Courier':
            return redirect(url_for('courier_dashboard.dashboard'))
    
    return render_template('account_banned.html')


def send_otp_email(email, otp):
    sender_email = "fanamazecommerce@zohomail.com"
    zoho_smtp_server = "smtp.zoho.com"
    zoho_smtp_port = 587
    zoho_smtp_user = sender_email
    zoho_smtp_password = "7v7pi67S2Sy6"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = "Password Change OTP - Fenamaz Ecommerce" 

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
            print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")


# EMAIL EXISTS
def email_exists(email):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT COUNT(*) 
                FROM account_contact_info 
                WHERE email = %s
            """, (email,))

            result = cursor.fetchone()

            if result and result[0] > 0:
                return True
            else:
                return False

        except Exception as e:
            print(f"Error checking email: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    return False


# FORGOT PASS
@login_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_pass():
    
    if 'user_role' in session and session.get('status') == 'Approved':
        role = session.get('user_role')
        if role == 'Admin':
            return redirect(url_for('admin_dashboard.dashboard'))
        elif role == 'Seller':
            return redirect(url_for('seller_dashboard.dashboard'))
        elif role == 'Buyer':
            return redirect(url_for('buyer_homepage.show_buyer_homepage'))
        elif role == 'Courier':
            return redirect(url_for('courier_dashboard.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        
        if not email_exists(email):
            flash("Email not found. Please try again.", "danger")
            return redirect(url_for('login.forgot_pass'))

        otp = random.randint(100000, 999999)
        session['forgot_otp'] = otp
        session['forgot_email'] = email

        send_otp_email(email, otp)
        
        return redirect(url_for('login.verify_otp'))

    return render_template('account_forgot_pass.html')


# VERIFY OTP
@login_bp.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    
    if request.method == 'POST':
        entered_otp = request.form.get('otp')
        
        if int(entered_otp) == session.get('forgot_otp'):
            return redirect(url_for('login.reset_password'))
        else:
            flash("Invalid OTP. Please try again.", "danger")
            return redirect(url_for('login.verify_otp'))

    return render_template('account_verify_otp.html')


# RESEND OTP
@login_bp.route('/resend_otp', methods=['GET'])
def resend_otp():
        
    if 'user_role' in session and session.get('status') == 'Approved':
        role = session.get('user_role')
        if role == 'Admin':
            return redirect(url_for('admin_dashboard.dashboard'))
        elif role == 'Seller':
            return redirect(url_for('seller_dashboard.dashboard'))
        elif role == 'Buyer':
            return redirect(url_for('buyer_homepage.show_buyer_homepage'))
        elif role == 'Courier':
            return redirect(url_for('courier_dashboard.dashboard'))
    
    email = session.get('forgot_email')
    
    if not email or 'forgot_otp' not in session:
        flash("Session expired. Please request OTP again.", "danger")
        return redirect(url_for('login.forgot_pass'))

    otp = session.get('forgot_otp') 

    send_otp_email(email, otp)

    flash("OTP has been resent to your email!", "success")
    return redirect(url_for('login.verify_otp'))


# RESET PASSWORD
@login_bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
        
    if 'user_role' in session and session.get('status') == 'Approved':
        role = session.get('user_role')
        if role == 'Admin':
            return redirect(url_for('admin_dashboard.dashboard'))
        elif role == 'Seller':
            return redirect(url_for('seller_dashboard.dashboard'))
        elif role == 'Buyer':
            return redirect(url_for('buyer_homepage.show_buyer_homepage'))
        elif role == 'Courier':
            return redirect(url_for('courier_dashboard.dashboard'))
    
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        
        hashed_password = generate_password_hash(new_password)

        email = session.get('forgot_email')
        
        if not email:
            flash("Session expired. Please try again.", "danger")
            return redirect(url_for('login.forgot_pass'))

        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                cursor.execute(""" 
                    UPDATE account_login_info 
                    SET password = %s 
                    WHERE login_id = (SELECT login_id FROM account_contact_info WHERE email = %s)
                """, (hashed_password, email))

                conn.commit()

                session.pop('forgot_otp', None)
                session.pop('forgot_email', None)

                flash("Your password has been reset successfully!", "success")
                return redirect(url_for('login.login'))  

            except Exception as e:
                print(f"Error resetting password: {e}")
                flash("An error occurred. Please try again later.", "danger")
                return redirect(url_for('login.reset_password'))
            finally:
                cursor.close()
                conn.close()
        else:
            flash("Database connection error. Please try again.", "danger")
            return redirect(url_for('login.reset_password'))

    return render_template('account_reset_pass.html')