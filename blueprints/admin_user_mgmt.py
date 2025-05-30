# IMPORTS
from flask import Blueprint, render_template, flash, session, redirect, url_for, request, send_file, current_app, send_from_directory
from db_connection import get_db_connection  
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

admin_user_mgmt_bp = Blueprint('admin_user_mgmt', __name__)

# Routes to serve images from uploads folders
@admin_user_mgmt_bp.route('/admin/uploads/buyer/valid_id_pic/<filename>')
def serve_buyer_id_pic(filename):
    if 'admin' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Admin':
        flash("Unauthorized access. Admins only.", "danger")
        return redirect(url_for('login.login'))
    
    return send_from_directory('static/uploads/buyer/valid_id_pic', filename)

@admin_user_mgmt_bp.route('/admin/uploads/seller/valid_id_pic/<filename>')
def serve_seller_id_pic(filename):
    if 'admin' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Admin':
        flash("Unauthorized access. Admins only.", "danger")
        return redirect(url_for('login.login'))
    
    return send_from_directory('static/uploads/seller/valid_id_pic', filename)

@admin_user_mgmt_bp.route('/admin/uploads/seller/permit_pic/<filename>')
def serve_seller_permit_pic(filename):
    if 'admin' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Admin':
        flash("Unauthorized access. Admins only.", "danger")
        return redirect(url_for('login.login'))
    
    return send_from_directory('static/uploads/seller/permit_pic', filename)

@admin_user_mgmt_bp.route('/admin/uploads/seller/shop_profile/<filename>')
def serve_seller_shop_pic(filename):
    return send_from_directory('static/uploads/seller/shop_profile', filename)

@admin_user_mgmt_bp.route('/admin/uploads/courier/valid_id_pic/<filename>')
def serve_courier_id_pic(filename):
    if 'admin' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Admin':
        flash("Unauthorized access. Admins only.", "danger")
        return redirect(url_for('login.login'))
    
    return send_from_directory('static/uploads/courier/valid_id_pic', filename)

# Update Buyer Status
@admin_user_mgmt_bp.route('/admin/update_buyer_status', methods=['POST'])
def update_buyer_status():
    if 'admin' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Admin':
        flash("Unauthorized access. Admins only.", "danger")
        return redirect(url_for('login.login'))
    
    user_ids = request.form.getlist("user_ids") 
    new_status = request.form.get("status")

    if not user_ids or not new_status:
        flash("Invalid request. Please select users and a valid status.", "warning")
        return redirect(url_for('admin_user_mgmt.buyer_mgmt'))

    conn = get_db_connection()
    cursor = conn.cursor()

    placeholders = ",".join(["%s"] * len(user_ids))  
    query = f"UPDATE user_account SET status = %s WHERE user_id IN ({placeholders})"

    cursor.execute(query, (new_status, *user_ids))  

    conn.commit()
    cursor.close()
    conn.close()

    flash(f"Updated {len(user_ids)} users to {new_status} Successfully!", "success")
    return redirect(url_for('admin_user_mgmt.buyer_mgmt'))


@admin_user_mgmt_bp.route('/admin/buyer_management')
def buyer_mgmt():
    if 'admin' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Admin':
        flash("Unauthorized access. Admins only.", "danger")
        return redirect(url_for('login.login'))

    status = request.args.get("status", "Approved")
    sort_by = request.args.get("sort_by", "date_created")
    order = request.args.get("order", "DESC").upper()
    search = request.args.get("search", "").strip()

    # Allow only predefined sorting columns
    allowed_columns = {
        "firstname", "lastname", "sex", "age", "city", "province",
        "email", "status", "date_created"
    }
    if sort_by not in allowed_columns:
        sort_by = "date_created"

    order = "DESC" if order == "DESC" else "ASC"

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT 
        ua.user_id, pi.firstname, pi.lastname, pi.sex, pi.age, pi.birthdate,
        ai.house_no, ai.street, ai.barangay, ai.city, ai.province, ai.region,
        ci.email, ci.phone, vi.id_type, vi.id_no, vi.id_pic,
        ua.profile_pic, ua.status, ua.date_created
    FROM user_account ua
    JOIN account_personal_info pi ON ua.personal_id = pi.personal_id
    JOIN account_address_info ai ON ua.address_id = ai.address_id
    JOIN account_contact_info ci ON ua.contact_id = ci.contact_id
    JOIN account_valid_info vi ON ua.valid_id = vi.valid_id
    WHERE ua.user_role = 'Buyer' AND ua.status = %s
    """

    params = [status]

    if search:
        query += """ 
        AND (
            pi.firstname LIKE %s OR 
            pi.lastname LIKE %s OR 
            pi.sex LIKE %s OR
            pi.age LIKE %s OR
            ci.email LIKE %s OR 
            ci.phone LIKE %s OR 
            ai.city LIKE %s OR 
            ai.province LIKE %s OR
            ua.date_created LIKE %s OR
            ua.status LIKE %s
        )
        """
        search_term = f"%{search}%"
        params.extend([search_term] * 10)

    query += f" ORDER BY {sort_by} {order}"

    cursor.execute(query, params)
    buyers = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'admin_buyer_mgmt.html', 
        buyers=buyers, 
        selected_status=status, 
        sort_by=sort_by, 
        order=order, 
        search=search
    )


# Update Courier Status
@admin_user_mgmt_bp.route('/admin/update_courier_status', methods=['POST'])
def update_courier_status():
    if 'admin' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Admin':
        flash("Unauthorized access. Admins only.", "danger")
        return redirect(url_for('login.login'))
    
    user_ids = request.form.getlist("user_ids") 
    new_status = request.form.get("status")

    if not user_ids or not new_status:
        flash("Invalid request. Please select users and a valid status.", "warning")
        return redirect(url_for('admin_user_mgmt.courier_mgmt'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    placeholders = ",".join(["%s"] * len(user_ids))  
    query = f"UPDATE user_account SET status = %s WHERE user_id IN ({placeholders})"
    cursor.execute(query, (new_status, *user_ids))  
    conn.commit()

    if new_status == "Approved":
        cursor.execute(f"SELECT user_id, email, firstname FROM user_account JOIN account_contact_info ON user_account.contact_id = account_contact_info.contact_id JOIN account_personal_info ON user_account.personal_id = account_personal_info.personal_id WHERE user_id IN ({placeholders})", user_ids)
        couriers_info = cursor.fetchall()
        
        for courier in couriers_info:
            courier_id = courier['user_id']
            courier_email = courier['email']
            courier_name = courier['firstname']
            admin_id = 1

            notification_message = "Your courier account has been approved! You can now start accepting delivery requests."
            cursor.execute(""" 
                INSERT INTO notifications (recipient_id, sender_id, notification_type, notification_title, content, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())""",
                (courier_id, admin_id, 'Account Registration', 'Account Approved', notification_message, 'Unread')
            )

            send_registration_success_email(courier_email, courier_name)

    conn.commit()
    cursor.close()
    conn.close()

    flash(f"Updated {len(user_ids)} couriers to {new_status} successfully!", "success")
    return redirect(url_for('admin_user_mgmt.courier_mgmt'))


# COURIER MANAGEMENT
@admin_user_mgmt_bp.route('/admin/courier_management')
def courier_mgmt():
    
    if 'admin' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Admin':
        flash("Unauthorized access. Admins only.", "danger")
        return redirect(url_for('login.login'))

    status = request.args.get("status", "Approved")
    sort_by = request.args.get("sort_by", "date_created")
    order = request.args.get("order", "DESC").upper()
    search = request.args.get("search", "").strip()

    # Allow only predefined sorting columns
    allowed_columns = {
        "firstname", "lastname", "sex", "age", "city", "province",
        "email", "status", "date_created"
    }
    if sort_by not in allowed_columns:
        sort_by = "date_created"

    order = "DESC" if order == "DESC" else "ASC"

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT 
        ua.user_id, pi.firstname, pi.lastname, pi.sex, pi.age, pi.birthdate,
        ai.house_no, ai.street, ai.barangay, ai.city, ai.province, ai.region,
        ci.email, ci.phone, vi.id_type, vi.id_no, vi.id_pic,
        ua.profile_pic, ua.status, ua.date_created
    FROM user_account ua
    JOIN account_personal_info pi ON ua.personal_id = pi.personal_id
    JOIN account_address_info ai ON ua.address_id = ai.address_id
    JOIN account_contact_info ci ON ua.contact_id = ci.contact_id
    JOIN account_valid_info vi ON ua.valid_id = vi.valid_id
    WHERE ua.user_role = 'Courier' AND ua.status = %s
    """

    params = [status]

    if search:
        query += """ 
        AND (
            pi.firstname LIKE %s OR 
            pi.lastname LIKE %s OR 
            pi.sex LIKE %s OR
            pi.age LIKE %s OR
            ci.email LIKE %s OR 
            ci.phone LIKE %s OR 
            ai.city LIKE %s OR 
            ai.province LIKE %s OR
            ua.date_created LIKE %s OR
            ua.status LIKE %s
        )
        """
        search_term = f"%{search}%"
        params.extend([search_term] * 10)

    query += f" ORDER BY {sort_by} {order}"

    cursor.execute(query, params)
    couriers = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'admin_courier_mgmt.html', 
        couriers=couriers, 
        selected_status=status, 
        sort_by=sort_by, 
        order=order, 
        search=search
    )
    
    
# Update Seller Status
@admin_user_mgmt_bp.route('/admin/update_seller_status', methods=['POST'])
def update_seller_status():
    if 'admin' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Admin':
        flash("Unauthorized access. Admins only.", "danger")
        return redirect(url_for('login.login'))
    
    user_ids = request.form.getlist("user_ids") 
    new_status = request.form.get("status")

    if not user_ids or not new_status:
        flash("Invalid request. Please select users and a valid status.", "warning")
        return redirect(url_for('admin_user_mgmt.seller_mgmt'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    placeholders = ",".join(["%s"] * len(user_ids))  
    query = f"UPDATE user_account SET status = %s WHERE user_id IN ({placeholders})"
    cursor.execute(query, (new_status, *user_ids))  
    conn.commit()

    if new_status == "Approved":
        cursor.execute(f"SELECT user_id, email, firstname FROM user_account JOIN account_contact_info ON user_account.contact_id = account_contact_info.contact_id JOIN account_personal_info ON user_account.personal_id = account_personal_info.personal_id WHERE user_id IN ({placeholders})", user_ids)
        sellers_info = cursor.fetchall()
        
        for seller in sellers_info:
            seller_id = seller['user_id']
            seller_email = seller['email']
            seller_name = seller['firstname']
            admin_id = 1

            # Send notification
            notification_message = (
                "Congratulations! 🎉 Your seller account has been approved. "
                "You can now start managing your shop and selling your products."
            )
            cursor.execute(""" 
                INSERT INTO notifications (recipient_id, sender_id, notification_type, notification_title,content, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())""",
                (seller_id, admin_id, 'Account Registration', 'Account Approved', notification_message, 'Unread')
            )

            # Send email
            send_registration_success_email(seller_email, seller_name)

    conn.commit()
    cursor.close()
    conn.close()

    flash(f"Updated {len(user_ids)} sellers to {new_status} successfully!", "success")
    return redirect(url_for('admin_user_mgmt.seller_mgmt'))


# SELLER MANAGEMENT
@admin_user_mgmt_bp.route('/admin/seller_management')
def seller_mgmt():
    
    if 'admin' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Admin':
        flash("Unauthorized access. Admins only.", "danger")
        return redirect(url_for('login.login'))

    status = request.args.get("status", "Approved")
    sort_by = request.args.get("sort_by", "date_created")
    order = request.args.get("order", "DESC").upper()
    search = request.args.get("search", "").strip()

    # Allow only predefined sorting columns
    allowed_columns = {
        "firstname", "lastname", "sex", "age", "city", "province",
        "email", "status", "date_created"
    }
    if sort_by not in allowed_columns:
        sort_by = "date_created"

    order = "DESC" if order == "DESC" else "ASC"

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT 
        ua.user_id, pi.firstname, pi.lastname, pi.sex, pi.age, pi.birthdate,
        ai.house_no, ai.street, ai.barangay, ai.city, ai.province, ai.region,
        ci.email, ci.phone, vi.id_type, vi.id_no, vi.id_pic,
        bi.business_name, bi.permit_no, bi.issue_date, bi.expiry_date, bi.permit_pic,
        s.shop_id, s.shop_info_id, si.shop_name, si.shop_description, si.shop_pic,
        ua.profile_pic, ua.status, ua.date_created
    FROM user_account ua
    JOIN account_personal_info pi ON ua.personal_id = pi.personal_id
    JOIN account_address_info ai ON ua.address_id = ai.address_id
    JOIN account_contact_info ci ON ua.contact_id = ci.contact_id
    JOIN account_valid_info vi ON ua.valid_id = vi.valid_id
    JOIN account_business_info bi ON ua.business_id = bi.business_id
    LEFT JOIN shop s ON ua.user_id = s.seller_id  -- Join shop table
    LEFT JOIN shop_info si ON s.shop_info_id = si.shop_info_id 
    WHERE ua.user_role = 'Seller' AND ua.status = %s
    """

    params = [status]

    if search:
        query += """ 
        AND (
            pi.firstname LIKE %s OR 
            pi.lastname LIKE %s OR 
            pi.sex LIKE %s OR
            pi.age LIKE %s OR
            ci.email LIKE %s OR 
            ci.phone LIKE %s OR 
            ai.city LIKE %s OR 
            ai.province LIKE %s OR
            ua.date_created LIKE %s OR
            ua.status LIKE %s
        )
        """
        search_term = f"%{search}%"
        params.extend([search_term] * 10)

    query += f" ORDER BY {sort_by} {order}"

    cursor.execute(query, params)
    sellers = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'admin_seller_mgmt.html', 
        sellers=sellers, 
        selected_status=status, 
        sort_by=sort_by, 
        order=order, 
        search=search
    )


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
    msg['Subject'] = "Approve Successful - Fenamaz Ecommerce" 

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
        <p><strong>Hi {name},</strong></p>
        <p>We are excited to inform you that your registration with <strong>Fenamaz Ecommerce</strong> has been <strong class="blue">successfully approved!</strong></p>
        <p>Thank you for choosing Fenamaz Ecommerce.</p>
        <p>If you have any questions, feel free to contact our support team at <a href="mailto:fanamazecommerce@zohomail.com">fanamazecommerce@zohomail.com</a>.</p>
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