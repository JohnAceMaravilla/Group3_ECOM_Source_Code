# IMPORTS
from flask import Blueprint, render_template, flash, session, redirect, url_for, request, send_from_directory
from db_connection import get_db_connection
from datetime import datetime, timedelta
import os

admin_commision_bp = Blueprint('admin_commission', __name__)

def get_admin_sales(admin_id, user_type_filter='All', date_filter='today', sort_by='date_generated', order='desc', search_query='', custom_date=None):
    """Get admin sales/commission data with filtering and sorting"""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Base query
    query = """
        SELECT 
            ads.sales_id,
            ads.order_id,
            ads.user_id,
            ads.user_type,
            ads.total_sales as commission_amount,
            ads.date_generated,
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
            user_pi.firstname as user_firstname,
            user_pi.lastname as user_lastname,
            user_ci.email as user_email,
            user_ci.phone as user_phone,
            CONCAT(buyer_ai.house_no, ' ', buyer_ai.street, ', ', buyer_ai.barangay, ', ', buyer_ai.city, ', ', buyer_ai.province, ', ', buyer_ai.region) as delivery_address
        FROM admin_sales ads
        JOIN buyer_order bo ON ads.order_id = bo.order_id
        JOIN product p ON bo.product_id = p.product_id
        JOIN product_info pi ON p.product_info_id = pi.product_info_id
        JOIN user_account buyer_ua ON bo.buyer_id = buyer_ua.user_id
        JOIN account_personal_info buyer_pi ON buyer_ua.personal_id = buyer_pi.personal_id
        JOIN account_contact_info buyer_ci ON buyer_ua.contact_id = buyer_ci.contact_id
        JOIN account_address_info buyer_ai ON buyer_ua.address_id = buyer_ai.address_id
        JOIN user_account user_ua ON ads.user_id = user_ua.user_id
        JOIN account_personal_info user_pi ON user_ua.personal_id = user_pi.personal_id
        JOIN account_contact_info user_ci ON user_ua.contact_id = user_ci.contact_id
        WHERE ads.admin_id = %s
    """
    
    params = [admin_id]
    
    # Add user type filter
    if user_type_filter != 'All':
        query += " AND ads.user_type = %s"
        params.append(user_type_filter)
    
    # Add date filter
    if custom_date:
        query += " AND DATE(ads.date_generated) = %s"
        params.append(custom_date)
    elif date_filter == 'today':
        query += " AND DATE(ads.date_generated) = CURDATE()"
    elif date_filter == 'last_3_days':
        query += " AND ads.date_generated >= DATE_SUB(CURDATE(), INTERVAL 3 DAY)"
    elif date_filter == 'last_7_days':
        query += " AND ads.date_generated >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)"
    elif date_filter == 'last_month':
        query += " AND ads.date_generated >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)"
    
    # Add search filter
    if search_query:
        query += """ AND (
            pi.product_name LIKE %s OR
            pi.product_category LIKE %s OR
            p.variant LIKE %s OR
            p.color LIKE %s OR
            buyer_pi.firstname LIKE %s OR
            buyer_pi.lastname LIKE %s OR
            user_pi.firstname LIKE %s OR
            user_pi.lastname LIKE %s OR
            user_ci.email LIKE %s OR
            bo.order_id LIKE %s OR
            buyer_ai.city LIKE %s OR
            buyer_ai.province LIKE %s
        )"""
        search_term = f"%{search_query}%"
        params.extend([search_term] * 12)
    
    # Add sorting
    allowed_sort_columns = {
        'date_generated': 'ads.date_generated',
        'product_name': 'pi.product_name',
        'order_id': 'bo.order_id',
        'commission_amount': 'ads.total_sales',
        'total_amount': 'bo.total_amount',
        'buyer_name': 'buyer_pi.firstname',
        'user_name': 'user_pi.firstname',
        'user_type': 'ads.user_type'
    }
    
    if sort_by in allowed_sort_columns:
        sort_column = allowed_sort_columns[sort_by]
        order_direction = 'DESC' if order.lower() == 'desc' else 'ASC'
        query += f" ORDER BY {sort_column} {order_direction}"
    else:
        query += " ORDER BY ads.date_generated DESC"
    
    cursor.execute(query, params)
    sales = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return sales

def get_admin_statistics(admin_id, user_type_filter='All', date_filter='today', custom_date=None):
    """Get admin commission statistics"""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Base query for statistics
    query = """
        SELECT 
            COUNT(*) as total_commissions,
            SUM(ads.total_sales) as total_earnings,
            AVG(ads.total_sales) as average_commission,
            MIN(ads.total_sales) as min_commission,
            MAX(ads.total_sales) as max_commission,
            COUNT(CASE WHEN ads.user_type = 'Seller' THEN 1 END) as seller_commissions,
            COUNT(CASE WHEN ads.user_type = 'Courier' THEN 1 END) as courier_commissions,
            SUM(CASE WHEN ads.user_type = 'Seller' THEN ads.total_sales ELSE 0 END) as seller_earnings,
            SUM(CASE WHEN ads.user_type = 'Courier' THEN ads.total_sales ELSE 0 END) as courier_earnings
        FROM admin_sales ads
        WHERE ads.admin_id = %s
    """
    
    params = [admin_id]
    
    # Add user type filter
    if user_type_filter != 'All':
        query += " AND ads.user_type = %s"
        params.append(user_type_filter)
    
    # Add date filter
    if custom_date:
        query += " AND DATE(ads.date_generated) = %s"
        params.append(custom_date)
    elif date_filter == 'today':
        query += " AND DATE(ads.date_generated) = CURDATE()"
    elif date_filter == 'last_3_days':
        query += " AND ads.date_generated >= DATE_SUB(CURDATE(), INTERVAL 3 DAY)"
    elif date_filter == 'last_7_days':
        query += " AND ads.date_generated >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)"
    elif date_filter == 'last_month':
        query += " AND ads.date_generated >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)"
    
    cursor.execute(query, params)
    stats = cursor.fetchone()
    
    cursor.close()
    connection.close()
    
    return stats

@admin_commision_bp.route('/admin/commission')
def commission():
    if 'admin' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Admin':
        flash("Unauthorized access. Admins only.", "danger")
        return redirect(url_for('login.login'))
    
    admin_id = session['admin']
    
    # Get filter parameters
    user_type_filter = request.args.get('user_type', 'All')
    date_filter = request.args.get('date_filter', 'today')
    sort_by = request.args.get('sort_by', 'date_generated')
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
    sales = get_admin_sales(admin_id, user_type_filter, date_filter, sort_by, order, search_query, custom_date_formatted)
    stats = get_admin_statistics(admin_id, user_type_filter, date_filter, custom_date_formatted)
    
    # Dynamic title and description based on filter
    filter_info = {
        'today': {'title': 'Today\'s Commissions', 'description': 'Your commission earnings for today.'},
        'last_3_days': {'title': 'Last 3 Days Commissions', 'description': 'Your commission earnings for the last 3 days.'},
        'last_7_days': {'title': 'Last 7 Days Commissions', 'description': 'Your commission earnings for the last 7 days.'},
        'last_month': {'title': 'Last Month Commissions', 'description': 'Your commission earnings for the last month.'}
    }
    
    if custom_date:
        current_filter_info = {
            'title': f'Commissions for {custom_date}', 
            'description': f'Your commission earnings for {custom_date}.'
        }
    else:
        current_filter_info = filter_info.get(date_filter, filter_info['today'])
    
    # Add user type to title if filtered
    if user_type_filter != 'All':
        current_filter_info['title'] = f"{user_type_filter} {current_filter_info['title']}"
        current_filter_info['description'] = f"Your commission earnings from {user_type_filter.lower()}s for the selected period."
    
    return render_template('admin_commission.html',
                         sales=sales,
                         stats=stats,
                         user_type_filter=user_type_filter,
                         date_filter=date_filter,
                         sort_by=sort_by,
                         order=order,
                         search_query=search_query,
                         custom_date=custom_date,
                         page_title=current_filter_info['title'],
                         page_description=current_filter_info['description'])

# Constants for file uploads
PRODUCT_MAIN_PIC_FOLDER = "static/uploads/seller/product_main_pics"

# Routes to serve product images (for the commission page modals)
@admin_commision_bp.route('/uploads/product_main_pics/<filename>')
def serve_product_main_pic(filename):
    return send_from_directory(PRODUCT_MAIN_PIC_FOLDER, filename)