# IMPORTS
from flask import Blueprint, render_template, flash, session, redirect, url_for, request, send_from_directory
from db_connection import get_db_connection
from datetime import datetime, timedelta
import os

courier_finance_bp = Blueprint('courier_finance', __name__)

def get_courier_sales(courier_id, date_filter='today', sort_by='date_created', order='desc', search_query='', custom_date=None):
    """Get delivery sales data for a specific courier with filtering and sorting"""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Base query
    query = """
        SELECT 
            cs.sales_id,
            cs.order_id,
            cs.sale as delivery_fee,
            cs.date_created,
            bo.quantity,
            bo.total_amount,
            bo.payment_method,
            bo.payment_status,
            bo.status as order_status,
            bo.date_ordered,
            p.variant,
            p.color,
            p.price,
            p.shipping_fee,
            pi.product_name,
            pi.product_main_pic,
            pi.product_category,
            buyer_pi.firstname as buyer_firstname,
            buyer_pi.lastname as buyer_lastname,
            buyer_ci.email as buyer_email,
            buyer_ci.phone as buyer_phone,
            seller_pi.firstname as seller_firstname,
            seller_pi.lastname as seller_lastname,
            CONCAT(buyer_ai.house_no, ' ', buyer_ai.street, ', ', buyer_ai.barangay, ', ', buyer_ai.city, ', ', buyer_ai.province, ', ', buyer_ai.region) as delivery_address,
            od.status as delivery_status,
            od.date_delivered as delivery_date
        FROM courier_sales cs
        JOIN buyer_order bo ON cs.order_id = bo.order_id
        JOIN product p ON bo.product_id = p.product_id
        JOIN product_info pi ON p.product_info_id = pi.product_info_id
        JOIN user_account buyer_ua ON bo.buyer_id = buyer_ua.user_id
        JOIN account_personal_info buyer_pi ON buyer_ua.personal_id = buyer_pi.personal_id
        JOIN account_contact_info buyer_ci ON buyer_ua.contact_id = buyer_ci.contact_id
        JOIN account_address_info buyer_ai ON buyer_ua.address_id = buyer_ai.address_id
        JOIN user_account seller_ua ON bo.seller_id = seller_ua.user_id
        JOIN account_personal_info seller_pi ON seller_ua.personal_id = seller_pi.personal_id
        LEFT JOIN order_delivery od ON bo.order_id = od.order_id
        WHERE cs.courier_id = %s
    """
    
    params = [courier_id]
    
    # Add date filter
    if custom_date:
        query += " AND DATE(cs.date_created) = %s"
        params.append(custom_date)
    elif date_filter == 'today':
        query += " AND DATE(cs.date_created) = CURDATE()"
    elif date_filter == 'last_3_days':
        query += " AND cs.date_created >= DATE_SUB(CURDATE(), INTERVAL 3 DAY)"
    elif date_filter == 'last_7_days':
        query += " AND cs.date_created >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)"
    elif date_filter == 'last_month':
        query += " AND cs.date_created >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)"
    
    # Add search filter
    if search_query:
        query += """ AND (
            pi.product_name LIKE %s OR
            pi.product_category LIKE %s OR
            p.variant LIKE %s OR
            p.color LIKE %s OR
            buyer_pi.firstname LIKE %s OR
            buyer_pi.lastname LIKE %s OR
            seller_pi.firstname LIKE %s OR
            seller_pi.lastname LIKE %s OR
            bo.order_id LIKE %s OR
            buyer_ai.city LIKE %s OR
            buyer_ai.province LIKE %s OR
            buyer_ai.barangay LIKE %s
        )"""
        search_term = f"%{search_query}%"
        params.extend([search_term] * 12)
    
    # Add sorting
    allowed_sort_columns = {
        'date_created': 'cs.date_created',
        'product_name': 'pi.product_name',
        'order_id': 'bo.order_id',
        'delivery_fee': 'cs.sale',
        'total_amount': 'bo.total_amount',
        'buyer_name': 'buyer_pi.firstname',
        'seller_name': 'seller_pi.firstname'
    }
    
    if sort_by in allowed_sort_columns:
        sort_column = allowed_sort_columns[sort_by]
        order_direction = 'DESC' if order.lower() == 'desc' else 'ASC'
        query += f" ORDER BY {sort_column} {order_direction}"
    else:
        query += " ORDER BY cs.date_created DESC"
    
    cursor.execute(query, params)
    sales = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return sales

def get_courier_statistics(courier_id, date_filter='today', custom_date=None):
    """Get delivery statistics for the courier"""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Base query for statistics
    query = """
        SELECT 
            COUNT(*) as total_deliveries,
            SUM(cs.sale) as total_earnings,
            AVG(cs.sale) as average_delivery_fee,
            MIN(cs.sale) as min_delivery_fee,
            MAX(cs.sale) as max_delivery_fee
        FROM courier_sales cs
        WHERE cs.courier_id = %s
    """
    
    params = [courier_id]
    
    # Add date filter
    if custom_date:
        query += " AND DATE(cs.date_created) = %s"
        params.append(custom_date)
    elif date_filter == 'today':
        query += " AND DATE(cs.date_created) = CURDATE()"
    elif date_filter == 'last_3_days':
        query += " AND cs.date_created >= DATE_SUB(CURDATE(), INTERVAL 3 DAY)"
    elif date_filter == 'last_7_days':
        query += " AND cs.date_created >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)"
    elif date_filter == 'last_month':
        query += " AND cs.date_created >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)"
    
    cursor.execute(query, params)
    stats = cursor.fetchone()
    
    cursor.close()
    connection.close()
    
    return stats

@courier_finance_bp.route('/courier/finance')
def finance():
    if 'courier' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Courier':
        flash("Unauthorized access. Couriers only.", "danger")
        return redirect(url_for('login.login'))
    
    courier_id = session['courier']
    
    # Get filter parameters
    date_filter = request.args.get('date_filter', 'today')
    sort_by = request.args.get('sort_by', 'date_created')
    order = request.args.get('order', 'desc')
    search_query = request.args.get('search', '')
    custom_date = request.args.get('custom_date', '')
    
    # Convert custom_date to proper format if provided
    custom_date_formatted = None
    if custom_date:
        try:
            custom_date_formatted = datetime.strptime(custom_date, '%Y-%m-%d').date()
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD format.", "danger")
            custom_date = ''
    
    # Get sales and statistics
    sales = get_courier_sales(courier_id, date_filter, sort_by, order, search_query, custom_date_formatted)
    stats = get_courier_statistics(courier_id, date_filter, custom_date_formatted)
    
    # Dynamic title and description based on filter
    filter_info = {
        'today': {'title': 'Today\'s Deliveries', 'description': 'Your delivery earnings for today.'},
        'last_3_days': {'title': 'Last 3 Days Deliveries', 'description': 'Your delivery earnings for the last 3 days.'},
        'last_7_days': {'title': 'Last 7 Days Deliveries', 'description': 'Your delivery earnings for the last 7 days.'},
        'last_month': {'title': 'Last Month Deliveries', 'description': 'Your delivery earnings for the last month.'}
    }
    
    if custom_date:
        current_filter_info = {
            'title': f'Deliveries for {custom_date}', 
            'description': f'Your delivery earnings for {custom_date}.'
        }
    else:
        current_filter_info = filter_info.get(date_filter, filter_info['today'])
    
    return render_template('courier_finance.html',
                         sales=sales,
                         stats=stats,
                         date_filter=date_filter,
                         sort_by=sort_by,
                         order=order,
                         search_query=search_query,
                         custom_date=custom_date,
                         page_title=current_filter_info['title'],
                         page_description=current_filter_info['description'])

# Constants for file uploads (same as seller_inventory)
PRODUCT_MAIN_PIC_FOLDER = "static/uploads/seller/product_main_pics"

# Routes to serve product images (for the finance page modals)
@courier_finance_bp.route('/uploads/product_main_pics/<filename>')
def serve_product_main_pic(filename):
    return send_from_directory(PRODUCT_MAIN_PIC_FOLDER, filename)
