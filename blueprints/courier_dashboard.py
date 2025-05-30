# IMPORTS
from flask import Blueprint, render_template, flash, session, redirect, url_for, jsonify, request
from blueprints.get_user_info import get_personal_info, get_address_info, get_contact_info, get_valid_info, get_business_info
from db_connection import get_db_connection
from blueprints.courier_notifications import get_unread_notifications_count
from datetime import datetime, timedelta
import json

courier_dashboard_bp = Blueprint('courier_dashboard', __name__)

def get_chart_data(courier_id, chart_period='last_7_days', chart_custom_date=None):
    """Get chart data separately from dashboard stats"""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Base date filter condition for chart
    date_condition = ""
    params = [courier_id]
    
    if chart_custom_date:
        date_condition = " AND DATE(cs.date_created) = %s"
        params.append(chart_custom_date)
    elif chart_period == 'last_7_days':
        date_condition = " AND cs.date_created >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)"
    elif chart_period == 'last_14_days':
        date_condition = " AND cs.date_created >= DATE_SUB(CURDATE(), INTERVAL 14 DAY)"
    elif chart_period == 'last_30_days':
        date_condition = " AND cs.date_created >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)"
    elif chart_period == 'this_month':
        date_condition = " AND MONTH(cs.date_created) = MONTH(CURDATE()) AND YEAR(cs.date_created) = YEAR(CURDATE())"
    
    # Get daily earnings for chart
    cursor.execute(f"""
        SELECT 
            DATE(cs.date_created) as date,
            COALESCE(SUM(cs.sale), 0) as daily_earnings,
            COUNT(*) as daily_deliveries
        FROM courier_sales cs
        WHERE cs.courier_id = %s {date_condition}
        GROUP BY DATE(cs.date_created)
        ORDER BY DATE(cs.date_created) ASC
    """, params)
    
    chart_data = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return chart_data

def get_courier_dashboard_stats(courier_id, date_filter='today', custom_date=None):
    """Get comprehensive dashboard statistics for courier"""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Base date filter condition
    date_condition = ""
    params = [courier_id]
    
    if custom_date:
        date_condition = " AND DATE(cs.date_created) = %s"
        params.append(custom_date)
    elif date_filter == 'today':
        date_condition = " AND DATE(cs.date_created) = CURDATE()"
    elif date_filter == 'last_7_days':
        date_condition = " AND cs.date_created >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)"
    elif date_filter == 'last_30_days':
        date_condition = " AND cs.date_created >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)"
    elif date_filter == 'this_month':
        date_condition = " AND MONTH(cs.date_created) = MONTH(CURDATE()) AND YEAR(cs.date_created) = YEAR(CURDATE())"
    
    # Get delivery earnings statistics
    cursor.execute(f"""
        SELECT 
            COUNT(*) as total_deliveries,
            COALESCE(SUM(cs.sale), 0) as total_earnings,
            COALESCE(AVG(cs.sale), 0) as average_earning,
            COALESCE(MAX(cs.sale), 0) as highest_earning
        FROM courier_sales cs
        WHERE cs.courier_id = %s {date_condition}
    """, params)
    
    earnings_stats = cursor.fetchone()
    
    # Get delivery status statistics (all time for context)
    cursor.execute("""
        SELECT 
            COUNT(CASE WHEN od.status = 'For Delivery' THEN 1 END) as pending_deliveries,
            COUNT(CASE WHEN od.status = 'Out for Delivery' THEN 1 END) as active_deliveries,
            COUNT(CASE WHEN od.status = 'Delivered' THEN 1 END) as completed_deliveries,
            COUNT(*) as total_assigned_deliveries
        FROM order_delivery od
        WHERE od.courier_id = %s
    """, [courier_id])
    
    delivery_stats = cursor.fetchone()
    
    # Chart data will be fetched separately
    
    cursor.close()
    connection.close()
    
    return {
        'earnings_stats': earnings_stats,
        'delivery_stats': delivery_stats
    }

def get_recent_deliveries(courier_id, limit=5, sort_by='date_delivered', order='desc'):
    """Get recent deliveries for the dashboard"""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    allowed_sort_columns = {
        'date_delivered': 'od.date_delivered',
        'total_amount': 'bo.total_amount',
        'delivery_status': 'od.status'
    }
    
    sort_column = allowed_sort_columns.get(sort_by, 'od.date_delivered')
    order_direction = 'DESC' if order.lower() == 'desc' else 'ASC'
    
    query = f"""
        SELECT 
            od.delivery_id,
            od.order_id,
            od.status as delivery_status,
            od.date_delivered,
            bo.quantity,
            bo.total_amount,
            bo.payment_status,
            p.variant,
            p.color,
            p.price,
            p.shipping_fee,
            pi.product_name,
            pi.product_main_pic,
            buyer_pi.firstname as buyer_firstname,
            buyer_pi.lastname as buyer_lastname,
            buyer_ci.phone as buyer_phone,
            CONCAT(buyer_ai.house_no, ' ', buyer_ai.street, ', ', buyer_ai.barangay, ', ', buyer_ai.city) as delivery_address
        FROM order_delivery od
        JOIN buyer_order bo ON od.order_id = bo.order_id
        JOIN product p ON bo.product_id = p.product_id
        JOIN product_info pi ON p.product_info_id = pi.product_info_id
        JOIN user_account buyer_ua ON bo.buyer_id = buyer_ua.user_id
        JOIN account_personal_info buyer_pi ON buyer_ua.personal_id = buyer_pi.personal_id
        JOIN account_contact_info buyer_ci ON buyer_ua.contact_id = buyer_ci.contact_id
        JOIN account_address_info buyer_ai ON buyer_ua.address_id = buyer_ai.address_id
        WHERE od.courier_id = %s
        ORDER BY {sort_column} {order_direction}
        LIMIT %s
    """
    
    cursor.execute(query, [courier_id, limit])
    deliveries = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return deliveries

# COURIER DASHBOARD
@courier_dashboard_bp.route('/courier/dashboard')
def dashboard():
    if 'courier' not in session:
        flash("You must log in first.", "danger")
        return redirect(url_for('login.login'))
    
    courier_info = session.get('courier', {})
    if not courier_info:
        return render_template('courier_dashboard.html')
    
    # Get filter parameters
    date_filter = request.args.get('date_filter', 'today')
    sort_by = request.args.get('sort_by', 'date_delivered')
    order = request.args.get('order', 'desc')
    custom_date = request.args.get('custom_date', '')
    
    # Get chart-specific filter parameters
    chart_period = request.args.get('chart_period', 'last_7_days')
    chart_custom_date = request.args.get('chart_custom_date', '')
    
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
    
    # Get dashboard data
    stats = get_courier_dashboard_stats(courier_info, date_filter, custom_date_formatted)
    recent_deliveries = get_recent_deliveries(courier_info, 5, sort_by, order)
    chart_data_raw = get_chart_data(courier_info, chart_period, chart_custom_date_formatted)
    
    # Get user information and ensure session data is properly set
    personal = get_personal_info()  
    address = get_address_info()
    contact = get_contact_info()
    valid = get_valid_info()
    
    # Ensure session data exists for template access
    if not session.get('personal_data') and personal:
        session['personal_data'] = {
            'firstname': personal[0], 
            'lastname': personal[1], 
            'age': personal[2],      
            'sex': personal[3],        
            'birthdate': personal[4]  
        }
    
    if not session.get('contact_data') and contact:
        session['contact_data'] = {
            'email': contact[0],
            'phone': contact[1]
        }
    
    session['notif_unread_count'] = get_unread_notifications_count(courier_info)
    session.modified = True
    
    # Prepare chart data
    chart_data = {
        'daily_labels': [item['date'].strftime('%m/%d') for item in chart_data_raw],
        'daily_earnings': [float(item['daily_earnings']) for item in chart_data_raw],
        'daily_deliveries': [item['daily_deliveries'] for item in chart_data_raw]
    }
    
    # Dynamic title and description based on filter
    filter_info = {
        'today': {'title': 'Today\'s Overview', 'description': 'Your delivery performance and earnings for today.'},
        'last_7_days': {'title': 'Last 7 Days Overview', 'description': 'Your delivery performance and earnings for the last 7 days.'},
        'last_30_days': {'title': 'Last 30 Days Overview', 'description': 'Your delivery performance and earnings for the last 30 days.'},
        'this_month': {'title': 'This Month Overview', 'description': 'Your delivery performance and earnings for this month.'}
    }
    
    if custom_date:
        current_filter_info = {
            'title': f'Overview for {custom_date}', 
            'description': f'Your delivery performance and earnings for {custom_date}.'
        }
    else:
        current_filter_info = filter_info.get(date_filter, filter_info['today'])
    
    return render_template('courier_dashboard.html',
                         personal=personal, 
                         address=address, 
                         contact=contact, 
                         valid=valid,
                         stats=stats,
                         recent_deliveries=recent_deliveries,
                         chart_data=json.dumps(chart_data),
                         date_filter=date_filter,
                         sort_by=sort_by,
                         order=order,
                         custom_date=custom_date,
                         chart_period=chart_period,
                         chart_custom_date=chart_custom_date,
                         page_title=current_filter_info['title'],
                         page_description=current_filter_info['description'])

@courier_dashboard_bp.route('/courier/notifications/read', methods=['POST'])
def mark_notifications_read():
    if 'courier' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    courier_id = session.get('courier')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE notifications 
            SET status = 'Read' 
            WHERE recipient_id = %s AND status = 'Unread'
        """, (courier_id,))
        conn.commit()
        session['notif_unread_count'] = 0
        session.modified = True
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cursor.close()
        conn.close()

# Constants for file uploads
PRODUCT_MAIN_PIC_FOLDER = "static/uploads/seller/product_main_pics"
COURIER_PROFILE_PIC_FOLDER = "static/uploads/courier/profile_pics"
COURIER_VALID_ID_FOLDER = "static/uploads/courier/valid_id_pic"

# Routes to serve product images (for the dashboard)
@courier_dashboard_bp.route('/uploads/product_main_pics/<filename>')
def serve_product_main_pic(filename):
    from flask import send_from_directory
    return send_from_directory(PRODUCT_MAIN_PIC_FOLDER, filename)

@courier_dashboard_bp.route('/courier/dashboard/profile_pics/<filename>')
def serve_profile_pic(filename):
    from flask import send_from_directory
    return send_from_directory(COURIER_PROFILE_PIC_FOLDER, filename)

@courier_dashboard_bp.route('/courier/dashboard/valid_ids/<filename>')
def serve_valid_id(filename):
    from flask import send_from_directory
    return send_from_directory(COURIER_VALID_ID_FOLDER, filename)
    
