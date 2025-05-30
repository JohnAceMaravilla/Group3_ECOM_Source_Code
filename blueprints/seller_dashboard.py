# IMPORTS
from flask import Blueprint, render_template, flash, session, redirect, url_for, jsonify, request
from blueprints.get_user_info import get_personal_info, get_address_info, get_contact_info, get_valid_info, get_business_info
from db_connection import get_db_connection
from blueprints.seller_notifications import get_unread_notifications_count
from datetime import datetime, timedelta
import json

seller_dashboard_bp = Blueprint('seller_dashboard', __name__)

def get_chart_data(seller_id, chart_period='last_7_days', chart_custom_date=None):
    """Get chart data separately from dashboard stats"""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Base date filter condition for chart
    date_condition = ""
    params = [seller_id]
    
    if chart_custom_date:
        date_condition = " AND DATE(ss.date_created) = %s"
        params.append(chart_custom_date)
    elif chart_period == 'last_7_days':
        date_condition = " AND ss.date_created >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)"
    elif chart_period == 'last_14_days':
        date_condition = " AND ss.date_created >= DATE_SUB(CURDATE(), INTERVAL 14 DAY)"
    elif chart_period == 'last_30_days':
        date_condition = " AND ss.date_created >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)"
    elif chart_period == 'this_month':
        date_condition = " AND MONTH(ss.date_created) = MONTH(CURDATE()) AND YEAR(ss.date_created) = YEAR(CURDATE())"
    
    # Get daily sales for chart
    cursor.execute(f"""
        SELECT 
            DATE(ss.date_created) as date,
            COALESCE(SUM(ss.sale), 0) as daily_sales,
            COUNT(*) as daily_orders
        FROM seller_sales ss
        WHERE ss.seller_id = %s {date_condition}
        GROUP BY DATE(ss.date_created)
        ORDER BY DATE(ss.date_created) ASC
    """, params)
    
    chart_data = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return chart_data

def get_seller_dashboard_stats(seller_id, date_filter='today', custom_date=None):
    """Get comprehensive dashboard statistics for seller"""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Base date filter condition
    date_condition = ""
    params = [seller_id]
    
    if custom_date:
        date_condition = " AND DATE(ss.date_created) = %s"
        params.append(custom_date)
    elif date_filter == 'today':
        date_condition = " AND DATE(ss.date_created) = CURDATE()"
    elif date_filter == 'last_7_days':
        date_condition = " AND ss.date_created >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)"
    elif date_filter == 'last_30_days':
        date_condition = " AND ss.date_created >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)"
    elif date_filter == 'this_month':
        date_condition = " AND MONTH(ss.date_created) = MONTH(CURDATE()) AND YEAR(ss.date_created) = YEAR(CURDATE())"
    
    # Get sales statistics
    cursor.execute(f"""
        SELECT 
            COUNT(*) as total_orders,
            COALESCE(SUM(ss.sale), 0) as total_sales,
            COALESCE(AVG(ss.sale), 0) as average_sale,
            COALESCE(MAX(ss.sale), 0) as highest_sale
        FROM seller_sales ss
        WHERE ss.seller_id = %s {date_condition}
    """, params)
    
    sales_stats = cursor.fetchone()
    
    # Get order status statistics (all time for context)
    cursor.execute("""
        SELECT 
            COUNT(CASE WHEN bo.status = 'Pending' THEN 1 END) as pending_orders,
            COUNT(CASE WHEN bo.status IN ('To Pack', 'Packed') THEN 1 END) as processing_orders,
            COUNT(CASE WHEN bo.status IN ('Shipping', 'Shipped', 'For Delivery', 'Out for Delivery') THEN 1 END) as shipping_orders,
            COUNT(CASE WHEN bo.status IN ('Delivered', 'Received') THEN 1 END) as completed_orders,
            COUNT(*) as total_shop_orders
        FROM buyer_order bo
        WHERE bo.seller_id = %s
    """, [seller_id])
    
    order_stats = cursor.fetchone()
    
    # Get product statistics
    cursor.execute("""
        SELECT 
            COUNT(CASE WHEN p.status = 'Active' AND p.stock > 0 THEN 1 END) as active_products,
            COUNT(CASE WHEN p.status = 'Active' AND p.stock_status = 'Nearly Out of Stock' THEN 1 END) as low_stock_products,
            COUNT(CASE WHEN p.status = 'Active' AND p.stock_status = 'Out of Stock' THEN 1 END) as out_of_stock_products,
            COUNT(CASE WHEN p.status = 'Archived' THEN 1 END) as archived_products
        FROM shop_listing sl
        JOIN product p ON sl.product_id = p.product_id
        WHERE sl.seller_id = %s
    """, [seller_id])
    
    product_stats = cursor.fetchone()
    
    cursor.close()
    connection.close()
    
    return {
        'sales_stats': sales_stats,
        'order_stats': order_stats,
        'product_stats': product_stats
    }

def get_most_sold_products(seller_id, limit=5):
    """Get most sold products for the seller"""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    query = """
        SELECT 
            p.product_id,
            pi.product_name,
            pi.product_main_pic,
            p.variant,
            p.color,
            p.price,
            p.stock,
            p.stock_status,
            COUNT(bo.order_id) as total_orders,
            SUM(bo.quantity) as total_quantity_sold,
            SUM(bo.total_amount) as total_revenue
        FROM shop_listing sl
        JOIN product p ON sl.product_id = p.product_id
        JOIN product_info pi ON p.product_info_id = pi.product_info_id
        LEFT JOIN buyer_order bo ON p.product_id = bo.product_id AND bo.status IN ('Delivered', 'Received')
        WHERE sl.seller_id = %s AND p.status = 'Active'
        GROUP BY p.product_id, pi.product_name, pi.product_main_pic, p.variant, p.color, p.price, p.stock, p.stock_status
        ORDER BY total_quantity_sold DESC, total_revenue DESC
        LIMIT %s
    """
    
    cursor.execute(query, [seller_id, limit])
    products = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return products

def get_recent_orders(seller_id, limit=5, sort_by='date_ordered', order='desc'):
    """Get recent orders for the dashboard"""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    allowed_sort_columns = {
        'date_ordered': 'bo.date_ordered',
        'total_amount': 'bo.total_amount',
        'status': 'bo.status'
    }
    
    sort_column = allowed_sort_columns.get(sort_by, 'bo.date_ordered')
    order_direction = 'DESC' if order.lower() == 'desc' else 'ASC'
    
    query = f"""
        SELECT 
            bo.order_id,
            bo.quantity,
            bo.total_amount,
            bo.payment_status,
            bo.status,
            bo.date_ordered,
            p.variant,
            p.color,
            p.price,
            pi.product_name,
            pi.product_main_pic,
            buyer_pi.firstname as buyer_firstname,
            buyer_pi.lastname as buyer_lastname,
            buyer_ci.phone as buyer_phone,
            CONCAT(buyer_ai.house_no, ' ', buyer_ai.street, ', ', buyer_ai.barangay, ', ', buyer_ai.city) as buyer_address
        FROM buyer_order bo
        JOIN product p ON bo.product_id = p.product_id
        JOIN product_info pi ON p.product_info_id = pi.product_info_id
        JOIN user_account buyer_ua ON bo.buyer_id = buyer_ua.user_id
        JOIN account_personal_info buyer_pi ON buyer_ua.personal_id = buyer_pi.personal_id
        JOIN account_contact_info buyer_ci ON buyer_ua.contact_id = buyer_ci.contact_id
        JOIN account_address_info buyer_ai ON buyer_ua.address_id = buyer_ai.address_id
        WHERE bo.seller_id = %s
        ORDER BY {sort_column} {order_direction}
        LIMIT %s
    """
    
    cursor.execute(query, [seller_id, limit])
    orders = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return orders

@seller_dashboard_bp.route('/seller/dashboard')
def dashboard():
    
    if 'seller' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Seller':
        flash("Unauthorized access. Sellers only.", "danger")
        return redirect(url_for('login.login'))
    
    seller_info = session.get('seller', {})
    if not seller_info:
        return render_template('seller_dashboard.html')
    
    # Get filter parameters
    date_filter = request.args.get('date_filter', 'today')
    sort_by = request.args.get('sort_by', 'date_ordered')
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
    stats = get_seller_dashboard_stats(seller_info, date_filter, custom_date_formatted)
    most_sold_products = get_most_sold_products(seller_info, 5)
    recent_orders = get_recent_orders(seller_info, 5, sort_by, order)
    chart_data_raw = get_chart_data(seller_info, chart_period, chart_custom_date_formatted)
    
    # Get user information
    personal = get_personal_info()  
    address = get_address_info()
    contact = get_contact_info()
    valid = get_valid_info()
    business = get_business_info()
    session['notif_unread_count'] = get_unread_notifications_count(seller_info)
    session.modified = True 
    
    # Prepare chart data
    chart_data = {
        'daily_labels': [item['date'].strftime('%m/%d') for item in chart_data_raw],
        'daily_sales': [float(item['daily_sales']) for item in chart_data_raw],
        'daily_orders': [item['daily_orders'] for item in chart_data_raw]
    }
    
    # Dynamic title and description based on filter
    filter_info = {
        'today': {'title': 'Today\'s Overview', 'description': 'Your shop performance and sales for today.'},
        'last_7_days': {'title': 'Last 7 Days Overview', 'description': 'Your shop performance and sales for the last 7 days.'},
        'last_30_days': {'title': 'Last 30 Days Overview', 'description': 'Your shop performance and sales for the last 30 days.'},
        'this_month': {'title': 'This Month Overview', 'description': 'Your shop performance and sales for this month.'}
    }
    
    if custom_date:
        current_filter_info = {
            'title': f'Overview for {custom_date}', 
            'description': f'Your shop performance and sales for {custom_date}.'
        }
    else:
        current_filter_info = filter_info.get(date_filter, filter_info['today'])

    return render_template('seller_dashboard.html', 
                         personal=personal, 
                         address=address, 
                         contact=contact, 
                         valid=valid, 
                         business=business,
                         stats=stats,
                         most_sold_products=most_sold_products,
                         recent_orders=recent_orders,
                         chart_data=json.dumps(chart_data),
                         date_filter=date_filter,
                         sort_by=sort_by,
                         order=order,
                         custom_date=custom_date,
                         chart_period=chart_period,
                         chart_custom_date=chart_custom_date,
                         page_title=current_filter_info['title'],
                         page_description=current_filter_info['description'])

@seller_dashboard_bp.route('/seller/notifications/read', methods=['POST'])
def mark_notifications_read():
    if 'seller' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    seller_id = session.get('seller')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE notifications 
            SET status = 'Read' 
            WHERE recipient_id = %s AND status = 'Unread'
        """, (seller_id,))
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

# Routes to serve product images (for the dashboard)
@seller_dashboard_bp.route('/uploads/product_main_pics/<filename>')
def serve_product_main_pic(filename):
    from flask import send_from_directory
    return send_from_directory(PRODUCT_MAIN_PIC_FOLDER, filename)
    