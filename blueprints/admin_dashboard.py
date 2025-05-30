# IMPORTS
from flask import Blueprint, render_template, flash, session, redirect, url_for, jsonify, request
from blueprints.get_user_info import get_personal_info, get_address_info, get_contact_info, get_valid_info, get_business_info
from blueprints.admin_notifications import get_unread_notifications_count
from db_connection import get_db_connection
from datetime import datetime, timedelta
import json

admin_dashboard_bp = Blueprint('admin_dashboard', __name__)

# Constants for file uploads
SELLER_PROFILE_PIC_FOLDER = "static/uploads/seller/profile_pics"
COURIER_PROFILE_PIC_FOLDER = "static/uploads/courier/profile_pics"

def get_chart_data(admin_id, chart_period='last_7_days', chart_custom_date=None):
    """Get chart data separately from dashboard stats"""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Base date filter condition for chart
    date_condition = ""
    params = [admin_id]
    
    if chart_custom_date:
        date_condition = " AND DATE(ads.date_generated) = %s"
        params.append(chart_custom_date)
    elif chart_period == 'last_7_days':
        date_condition = " AND ads.date_generated >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)"
    elif chart_period == 'last_14_days':
        date_condition = " AND ads.date_generated >= DATE_SUB(CURDATE(), INTERVAL 14 DAY)"
    elif chart_period == 'last_30_days':
        date_condition = " AND ads.date_generated >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)"
    elif chart_period == 'this_month':
        date_condition = " AND MONTH(ads.date_generated) = MONTH(CURDATE()) AND YEAR(ads.date_generated) = YEAR(CURDATE())"
    
    # Get daily admin commission for chart
    cursor.execute(f"""
        SELECT 
            DATE(ads.date_generated) as date,
            COALESCE(SUM(ads.total_sales), 0) as daily_commission,
            COUNT(*) as daily_transactions
        FROM admin_sales ads
        WHERE ads.admin_id = %s {date_condition}
        GROUP BY DATE(ads.date_generated)
        ORDER BY DATE(ads.date_generated) ASC
    """, params)
    
    chart_data = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return chart_data

def get_seller_commission_chart_data(seller_id, chart_period='last_7_days', chart_custom_date=None):
    """Get seller-specific commission chart data"""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Base date filter condition for seller chart
    date_condition = ""
    params = [seller_id]
    
    if chart_custom_date:
        date_condition = " AND DATE(ads.date_generated) = %s"
        params.append(chart_custom_date)
    elif chart_period == 'last_7_days':
        date_condition = " AND ads.date_generated >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)"
    elif chart_period == 'last_14_days':
        date_condition = " AND ads.date_generated >= DATE_SUB(CURDATE(), INTERVAL 14 DAY)"
    elif chart_period == 'last_30_days':
        date_condition = " AND ads.date_generated >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)"
    elif chart_period == 'this_month':
        date_condition = " AND MONTH(ads.date_generated) = MONTH(CURDATE()) AND YEAR(ads.date_generated) = YEAR(CURDATE())"
    
    # Get daily seller commission for chart
    cursor.execute(f"""
        SELECT 
            DATE(ads.date_generated) as date,
            COALESCE(SUM(ads.total_sales), 0) as daily_commission,
            COUNT(*) as daily_transactions
        FROM admin_sales ads
        WHERE ads.user_id = %s AND ads.user_type = 'Seller' {date_condition}
        GROUP BY DATE(ads.date_generated)
        ORDER BY DATE(ads.date_generated) ASC
    """, params)
    
    chart_data = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return chart_data

def get_admin_dashboard_stats(admin_id, date_filter='today', custom_date=None):
    """Get comprehensive dashboard statistics for admin"""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Base date filter condition
    date_condition = ""
    params = [admin_id]
    
    if custom_date:
        date_condition = " AND DATE(ads.date_generated) = %s"
        params.append(custom_date)
    elif date_filter == 'today':
        date_condition = " AND DATE(ads.date_generated) = CURDATE()"
    elif date_filter == 'last_7_days':
        date_condition = " AND ads.date_generated >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)"
    elif date_filter == 'last_30_days':
        date_condition = " AND ads.date_generated >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)"
    elif date_filter == 'this_month':
        date_condition = " AND MONTH(ads.date_generated) = MONTH(CURDATE()) AND YEAR(ads.date_generated) = YEAR(CURDATE())"
    
    # Get commission statistics
    cursor.execute(f"""
        SELECT 
            COUNT(*) as total_commissions,
            COALESCE(SUM(ads.total_sales), 0) as total_commission_earnings,
            COALESCE(AVG(ads.total_sales), 0) as average_commission,
            COALESCE(MAX(ads.total_sales), 0) as highest_commission
        FROM admin_sales ads
        WHERE ads.admin_id = %s {date_condition}
    """, params)
    
    commission_stats = cursor.fetchone()
    
    # Get user count statistics (all time for context)
    cursor.execute("""
        SELECT 
            COUNT(CASE WHEN ua.user_role = 'Buyer' THEN 1 END) as total_buyers,
            COUNT(CASE WHEN ua.user_role = 'Seller' THEN 1 END) as total_sellers,
            COUNT(CASE WHEN ua.user_role = 'Courier' THEN 1 END) as total_couriers,
            COUNT(CASE WHEN ua.user_role = 'Seller' AND ua.status = 'Pending' THEN 1 END) as pending_sellers,
            COUNT(CASE WHEN ua.user_role = 'Courier' AND ua.status = 'Pending' THEN 1 END) as pending_couriers,
            COUNT(CASE WHEN ua.user_role = 'Buyer' AND ua.status = 'Pending' THEN 1 END) as pending_buyers
        FROM user_account ua
    """)
    
    user_stats = cursor.fetchone()
    
    # Get commission breakdown by type (for the filtered period)
    cursor.execute(f"""
        SELECT 
            COUNT(CASE WHEN ads.user_type = 'Seller' THEN 1 END) as seller_commissions,
            COUNT(CASE WHEN ads.user_type = 'Courier' THEN 1 END) as courier_commissions,
            COALESCE(SUM(CASE WHEN ads.user_type = 'Seller' THEN ads.total_sales ELSE 0 END), 0) as seller_commission_earnings,
            COALESCE(SUM(CASE WHEN ads.user_type = 'Courier' THEN ads.total_sales ELSE 0 END), 0) as courier_commission_earnings
        FROM admin_sales ads
        WHERE ads.admin_id = %s {date_condition}
    """, params)
    
    commission_breakdown = cursor.fetchone()
    
    cursor.close()
    connection.close()
    
    return {
        'commission_stats': commission_stats,
        'user_stats': user_stats,
        'commission_breakdown': commission_breakdown
    }

def get_top_sellers_leaderboard(admin_id, limit=5):
    """Get top sellers by commission for leaderboard"""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    query = """
        SELECT 
            ads.user_id,
            pi.firstname,
            pi.lastname,
            ci.email,
            COUNT(*) as total_orders,
            SUM(ads.total_sales) as total_commission,
            AVG(ads.total_sales) as average_commission
        FROM admin_sales ads
        JOIN user_account ua ON ads.user_id = ua.user_id
        JOIN account_personal_info pi ON ua.personal_id = pi.personal_id
        JOIN account_contact_info ci ON ua.contact_id = ci.contact_id
        WHERE ads.admin_id = %s AND ads.user_type = 'Seller'
        GROUP BY ads.user_id, pi.firstname, pi.lastname, ci.email
        ORDER BY total_commission DESC
        LIMIT %s
    """
    
    cursor.execute(query, [admin_id, limit])
    sellers = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return sellers

def get_top_couriers_leaderboard(admin_id, limit=5):
    """Get top couriers by commission for leaderboard"""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    query = """
        SELECT 
            ads.user_id,
            pi.firstname,
            pi.lastname,
            ci.email,
            COUNT(*) as total_deliveries,
            SUM(ads.total_sales) as total_commission,
            AVG(ads.total_sales) as average_commission
        FROM admin_sales ads
        JOIN user_account ua ON ads.user_id = ua.user_id
        JOIN account_personal_info pi ON ua.personal_id = pi.personal_id
        JOIN account_contact_info ci ON ua.contact_id = ci.contact_id
        WHERE ads.admin_id = %s AND ads.user_type = 'Courier'
        GROUP BY ads.user_id, pi.firstname, pi.lastname, ci.email
        ORDER BY total_commission DESC
        LIMIT %s
    """
    
    cursor.execute(query, [admin_id, limit])
    couriers = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return couriers

def get_seller_list():
    """Get list of all sellers for dropdown selection"""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    query = """
        SELECT 
            ua.user_id,
            CONCAT(pi.firstname, ' ', pi.lastname) as full_name,
            ci.email
        FROM user_account ua
        JOIN account_personal_info pi ON ua.personal_id = pi.personal_id
        JOIN account_contact_info ci ON ua.contact_id = ci.contact_id
        WHERE ua.user_role = 'Seller' AND ua.status = 'Approved'
        ORDER BY pi.firstname, pi.lastname
    """
    
    cursor.execute(query)
    sellers = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return sellers

@admin_dashboard_bp.route('/admin/dashboard')
def dashboard():
    
    if 'admin' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Admin':
        flash("Unauthorized access. Admins only.", "danger")
        return redirect(url_for('login.login'))
    
    admin_info = session.get('admin', {})
    if not admin_info:
        return render_template('admin_dashboard.html')
    
    # Get filter parameters
    date_filter = request.args.get('date_filter', 'today')
    sort_by = request.args.get('sort_by', 'date_created')
    order = request.args.get('order', 'desc')
    custom_date = request.args.get('custom_date', '')
    
    # Get chart-specific filter parameters
    chart_period = request.args.get('chart_period', 'last_7_days')
    chart_custom_date = request.args.get('chart_custom_date', '')
    
    # Get seller commission chart parameters
    seller_chart_period = request.args.get('seller_chart_period', 'last_7_days')
    seller_chart_custom_date = request.args.get('seller_chart_custom_date', '')
    selected_seller_id = request.args.get('selected_seller_id', '')
    
    # Convert custom_date to proper format if provided
    custom_date_formatted = None
    if custom_date:
        try:
            custom_date_formatted = datetime.strptime(custom_date, '%Y-%m-%d').date()
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD format.", "danger")
            custom_date = ''
    
    # Convert chart_custom_date to proper format if provided
    chart_custom_date_formatted = None
    if chart_custom_date:
        try:
            chart_custom_date_formatted = datetime.strptime(chart_custom_date, '%Y-%m-%d').date()
        except ValueError:
            flash("Invalid chart date format. Please use YYYY-MM-DD format.", "danger")
            chart_custom_date = ''
    
    # Convert seller_chart_custom_date to proper format if provided
    seller_chart_custom_date_formatted = None
    if seller_chart_custom_date:
        try:
            seller_chart_custom_date_formatted = datetime.strptime(seller_chart_custom_date, '%Y-%m-%d').date()
        except ValueError:
            flash("Invalid seller chart date format. Please use YYYY-MM-DD format.", "danger")
            seller_chart_custom_date = ''
    
    # Get dashboard data
    stats = get_admin_dashboard_stats(admin_info, date_filter, custom_date_formatted)
    top_sellers = get_top_sellers_leaderboard(admin_info, 5)
    top_couriers = get_top_couriers_leaderboard(admin_info, 5)
    chart_data_raw = get_chart_data(admin_info, chart_period, chart_custom_date_formatted)
    seller_list = get_seller_list()
    
    # Get seller-specific chart data if seller is selected
    seller_chart_data_raw = []
    if selected_seller_id:
        seller_chart_data_raw = get_seller_commission_chart_data(selected_seller_id, seller_chart_period, seller_chart_custom_date_formatted)
    
    # Get user information
    personal = get_personal_info()  
    address = get_address_info()
    contact = get_contact_info()
    valid = get_valid_info()
    session['notif_unread_count'] = get_unread_notifications_count(admin_info)
    session.modified = True 
    
    # Prepare chart data
    chart_data = {
        'daily_labels': [item['date'].strftime('%m/%d') for item in chart_data_raw],
        'daily_commission': [float(item['daily_commission']) for item in chart_data_raw],
        'daily_transactions': [item['daily_transactions'] for item in chart_data_raw]
    }
    
    # Prepare seller chart data
    seller_chart_data = {
        'daily_labels': [item['date'].strftime('%m/%d') for item in seller_chart_data_raw],
        'daily_commission': [float(item['daily_commission']) for item in seller_chart_data_raw],
        'daily_transactions': [item['daily_transactions'] for item in seller_chart_data_raw]
    }
    
    # Dynamic title and description based on filter
    filter_info = {
        'today': {'title': 'Today\'s Admin Overview', 'description': 'Your admin commission and platform performance for today.'},
        'last_7_days': {'title': 'Last 7 Days Admin Overview', 'description': 'Your admin commission and platform performance for the last 7 days.'},
        'last_30_days': {'title': 'Last 30 Days Admin Overview', 'description': 'Your admin commission and platform performance for the last 30 days.'},
        'this_month': {'title': 'This Month Admin Overview', 'description': 'Your admin commission and platform performance for this month.'}
    }
    
    if custom_date:
        current_filter_info = {
            'title': f'Admin Overview for {custom_date}', 
            'description': f'Your admin commission and platform performance for {custom_date}.'
        }
    else:
        current_filter_info = filter_info.get(date_filter, filter_info['today'])

    return render_template('admin_dashboard.html', 
                         personal=personal, 
                         address=address, 
                         contact=contact, 
                         valid=valid,
                         stats=stats,
                         top_sellers=top_sellers,
                         top_couriers=top_couriers,
                         chart_data=json.dumps(chart_data),
                         seller_chart_data=json.dumps(seller_chart_data),
                         seller_list=seller_list,
                         date_filter=date_filter,
                         sort_by=sort_by,
                         order=order,
                         custom_date=custom_date,
                         chart_period=chart_period,
                         chart_custom_date=chart_custom_date,
                         seller_chart_period=seller_chart_period,
                         seller_chart_custom_date=seller_chart_custom_date,
                         selected_seller_id=selected_seller_id,
                         page_title=current_filter_info['title'],
                         page_description=current_filter_info['description'])

@admin_dashboard_bp.route('/admin/notifications/read', methods=['POST'])
def mark_notifications_read():
    if 'admin' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    admin_id = session.get('admin')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE notifications 
            SET status = 'Read' 
            WHERE recipient_id = %s AND status = 'Unread'
        """, (admin_id,))
        conn.commit()
        session['notif_unread_count'] = 0
        session.modified = True
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cursor.close()
        conn.close()

# Routes to serve uploaded files
@admin_dashboard_bp.route('/uploads/seller_profile_pics/<filename>')
def serve_seller_profile_pic(filename):
    from flask import send_from_directory
    return send_from_directory(SELLER_PROFILE_PIC_FOLDER, filename)

@admin_dashboard_bp.route('/uploads/courier_profile_pics/<filename>')
def serve_courier_profile_pic(filename):
    from flask import send_from_directory
    return send_from_directory(COURIER_PROFILE_PIC_FOLDER, filename)
