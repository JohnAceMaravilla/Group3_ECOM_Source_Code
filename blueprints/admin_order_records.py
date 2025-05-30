# IMPORTS
from flask import Blueprint, render_template, flash, session, redirect, url_for, request, send_from_directory, jsonify
from db_connection import get_db_connection
from datetime import datetime, timedelta
import os
import math

admin_order_records_bp = Blueprint('admin_order_records', __name__)

# Constants for image folders
PRODUCT_MAIN_PIC_FOLDER = "static/uploads/seller/product_main_pics"
PRODUCT_IMAGES_FOLDER = "static/uploads/seller/product_images"
PRODUCT_VARIANT_IMAGES_FOLDER = "static/uploads/seller/product_variant_images"

def get_all_orders(status_filter='All', sort_by='date_ordered', order='desc', search_query='', page=1, per_page=10):
    """Get all orders for admin records with filtering, sorting, and pagination"""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Base query for counting total records
    count_query = """
        SELECT COUNT(*) as total
        FROM buyer_order bo
        JOIN product p ON bo.product_id = p.product_id
        JOIN product_info pi ON p.product_info_id = pi.product_info_id
        JOIN shop s ON bo.shop_id = s.shop_id
        JOIN shop_info si ON s.shop_info_id = si.shop_info_id
        JOIN user_account seller_ua ON bo.seller_id = seller_ua.user_id
        JOIN account_personal_info seller_pi ON seller_ua.personal_id = seller_pi.personal_id
        JOIN account_contact_info seller_ci ON seller_ua.contact_id = seller_ci.contact_id
        JOIN user_account buyer_ua ON bo.buyer_id = buyer_ua.user_id
        JOIN account_personal_info buyer_pi ON buyer_ua.personal_id = buyer_pi.personal_id
        JOIN account_contact_info buyer_ci ON buyer_ua.contact_id = buyer_ci.contact_id
        JOIN account_address_info buyer_ai ON buyer_ua.address_id = buyer_ai.address_id
        WHERE 1=1
    """
    
    # Base query for data
    query = """
        SELECT 
            bo.order_id,
            bo.quantity,
            bo.total_amount,
            bo.payment_method,
            bo.payment_status,
            bo.status,
            bo.date_ordered,
            p.variant,
            p.color,
            p.price,
            p.shipping_fee,
            pi.product_name,
            pi.product_main_pic,
            pi.product_category,
            si.shop_name,
            seller_pi.firstname as seller_firstname,
            seller_pi.lastname as seller_lastname,
            seller_ci.email as seller_email,
            seller_ci.phone as seller_phone,
            buyer_pi.firstname as buyer_firstname,
            buyer_pi.lastname as buyer_lastname,
            buyer_ci.email as buyer_email,
            buyer_ci.phone as buyer_phone,
            buyer_ai.house_no,
            buyer_ai.street,
            buyer_ai.barangay,
            buyer_ai.city,
            buyer_ai.province,
            buyer_ai.region
        FROM buyer_order bo
        JOIN product p ON bo.product_id = p.product_id
        JOIN product_info pi ON p.product_info_id = pi.product_info_id
        JOIN shop s ON bo.shop_id = s.shop_id
        JOIN shop_info si ON s.shop_info_id = si.shop_info_id
        JOIN user_account seller_ua ON bo.seller_id = seller_ua.user_id
        JOIN account_personal_info seller_pi ON seller_ua.personal_id = seller_pi.personal_id
        JOIN account_contact_info seller_ci ON seller_ua.contact_id = seller_ci.contact_id
        JOIN user_account buyer_ua ON bo.buyer_id = buyer_ua.user_id
        JOIN account_personal_info buyer_pi ON buyer_ua.personal_id = buyer_pi.personal_id
        JOIN account_contact_info buyer_ci ON buyer_ua.contact_id = buyer_ci.contact_id
        JOIN account_address_info buyer_ai ON buyer_ua.address_id = buyer_ai.address_id
        WHERE 1=1
    """
    
    params = []
    count_params = []
    
    # Add status filter
    if status_filter != 'All':
        query += " AND bo.status = %s"
        count_query += " AND bo.status = %s"
        params.append(status_filter)
        count_params.append(status_filter)
    
    # Add search filter
    if search_query:
        search_condition = """ AND (
            pi.product_name LIKE %s OR
            buyer_pi.firstname LIKE %s OR
            buyer_pi.lastname LIKE %s OR
            seller_pi.firstname LIKE %s OR
            seller_pi.lastname LIKE %s OR
            buyer_ci.email LIKE %s OR
            seller_ci.email LIKE %s OR
            bo.order_id LIKE %s OR
            si.shop_name LIKE %s
        )"""
        query += search_condition
        count_query += search_condition
        search_term = f"%{search_query}%"
        params.extend([search_term] * 9)
        count_params.extend([search_term] * 9)
    
    # Get total count
    cursor.execute(count_query, count_params)
    total_records = cursor.fetchone()['total']
    
    # Add sorting
    allowed_sort_columns = {
        'date_ordered': 'bo.date_ordered',
        'product_name': 'pi.product_name',
        'buyer_name': 'buyer_pi.firstname',
        'seller_name': 'seller_pi.firstname',
        'total_amount': 'bo.total_amount',
        'status': 'bo.status',
        'shop_name': 'si.shop_name'
    }
    
    if sort_by in allowed_sort_columns:
        sort_column = allowed_sort_columns[sort_by]
        order_direction = 'DESC' if order.lower() == 'desc' else 'ASC'
        query += f" ORDER BY {sort_column} {order_direction}"
    else:
        query += " ORDER BY bo.date_ordered DESC"
    
    # Add pagination
    offset = (page - 1) * per_page
    query += f" LIMIT {per_page} OFFSET {offset}"
    
    cursor.execute(query, params)
    orders = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    # Calculate pagination info
    total_pages = math.ceil(total_records / per_page)
    has_prev = page > 1
    has_next = page < total_pages
    
    return {
        'orders': orders,
        'total_records': total_records,
        'total_pages': total_pages,
        'current_page': page,
        'per_page': per_page,
        'has_prev': has_prev,
        'has_next': has_next
    }

@admin_order_records_bp.route('/admin/order_records')
def order_records():
    
    if 'admin' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Admin':
        flash("Unauthorized access. Admins only.", "danger")
        return redirect(url_for('login.login'))
    
    # Get filter parameters
    status_filter = request.args.get('status', 'All')
    sort_by = request.args.get('sort_by', 'date_ordered')
    order = request.args.get('order', 'desc')
    search_query = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Items per page
    
    # Get orders with pagination
    result = get_all_orders(status_filter, sort_by, order, search_query, page, per_page)
    
    # Dynamic title and description based on status
    status_info = {
        'All': {'title': 'Order Records', 'description': 'View and manage all platform order records.'},
        'Pending': {'title': 'Pending Order Records', 'description': 'View all pending orders awaiting seller approval.'},
        'To Pack': {'title': 'Orders To Pack Records', 'description': 'View all orders ready for packing.'},
        'Packed': {'title': 'Packed Order Records', 'description': 'View all packed orders ready for shipment.'},
        'Shipping': {'title': 'Shipping Order Records', 'description': 'View all orders currently in shipping process.'},
        'Shipped': {'title': 'Shipped Order Records', 'description': 'View all shipped orders awaiting courier assignment.'},
        'For Delivery': {'title': 'Orders For Delivery Records', 'description': 'View all orders assigned to couriers.'},
        'Out for Delivery': {'title': 'Orders Out for Delivery Records', 'description': 'View all orders currently being delivered.'},
        'Delivered': {'title': 'Delivered Order Records', 'description': 'View all delivered orders awaiting confirmation.'},
        'Received': {'title': 'Received Order Records', 'description': 'View all orders confirmed as received by customers.'},
        'Rejected': {'title': 'Rejected Order Records', 'description': 'View all rejected orders requiring attention.'}
    }
    
    current_status_info = status_info.get(status_filter, status_info['All'])
    
    return render_template('admin_order_records.html', 
                         orders=result['orders'],
                         pagination=result,
                         status_filter=status_filter,
                         sort_by=sort_by,
                         order=order,
                         search_query=search_query,
                         page_title=current_status_info['title'],
                         page_description=current_status_info['description'])

# Routes to serve product images
@admin_order_records_bp.route('/uploads/product_main_pics/<filename>')
def serve_product_main_pic(filename):
    return send_from_directory(PRODUCT_MAIN_PIC_FOLDER, filename)

@admin_order_records_bp.route('/uploads/product_images/<filename>')
def serve_product_image(filename):
    return send_from_directory(PRODUCT_IMAGES_FOLDER, filename)

@admin_order_records_bp.route('/uploads/product_variant_images/<filename>')
def serve_product_variant_image(filename):
    return send_from_directory(PRODUCT_VARIANT_IMAGES_FOLDER, filename)