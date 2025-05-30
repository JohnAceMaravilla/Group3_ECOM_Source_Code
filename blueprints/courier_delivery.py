# IMPORTS
from flask import Blueprint, render_template, flash, session, redirect, url_for, request, jsonify, send_from_directory
from db_connection import get_db_connection
from datetime import datetime, timedelta
import os

courier_delivery_bp = Blueprint('courier_delivery', __name__)

# Constants for image folders
PRODUCT_MAIN_PIC_FOLDER = "static/uploads/seller/product_main_pics"
PRODUCT_IMAGES_FOLDER = "static/uploads/seller/product_images"
PRODUCT_VARIANT_IMAGES_FOLDER = "static/uploads/seller/product_variant_images"

def get_courier_deliveries(courier_id, status_filter='All', sort_by='date_delivered', order='desc', search_query=''):
    """Get deliveries assigned to a specific courier with filtering and sorting"""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Base query
    query = """
        SELECT 
            od.delivery_id,
            od.order_id,
            od.date_delivered,
            od.status as delivery_status,
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
        FROM order_delivery od
        JOIN buyer_order bo ON od.order_id = bo.order_id
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
        WHERE od.courier_id = %s
    """
    
    params = [courier_id]
    
    # Add status filter
    if status_filter != 'All':
        if status_filter == 'For Delivery':
            query += " AND od.status = 'For Delivery'"
        elif status_filter == 'Out for Delivery':
            query += " AND od.status = 'Out for Delivery'"
        elif status_filter == 'Delivered':
            query += " AND od.status = 'Delivered'"
    
    # Add search filter
    if search_query:
        query += """ AND (
            pi.product_name LIKE %s OR
            buyer_pi.firstname LIKE %s OR
            buyer_pi.lastname LIKE %s OR
            seller_pi.firstname LIKE %s OR
            seller_pi.lastname LIKE %s OR
            od.order_id LIKE %s
        )"""
        search_term = f"%{search_query}%"
        params.extend([search_term] * 6)
    
    # Add sorting
    allowed_sort_columns = {
        'date_delivered': 'od.date_delivered',
        'product_name': 'pi.product_name',
        'buyer_name': 'buyer_pi.firstname',
        'seller_name': 'seller_pi.firstname',
        'total_amount': 'bo.total_amount',
        'status': 'od.status'
    }
    
    if sort_by in allowed_sort_columns:
        sort_column = allowed_sort_columns[sort_by]
        order_direction = 'DESC' if order.lower() == 'desc' else 'ASC'
        query += f" ORDER BY {sort_column} {order_direction}"
    else:
        query += " ORDER BY od.date_delivered DESC"
    
    cursor.execute(query, params)
    deliveries = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return deliveries

def get_delivery_statistics(courier_id):
    """Get delivery statistics for the courier"""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT 
            COUNT(CASE WHEN status = 'For Delivery' THEN 1 END) as for_delivery_count,
            COUNT(CASE WHEN status = 'Out for Delivery' THEN 1 END) as out_delivery_count,
            COUNT(CASE WHEN status = 'Delivered' THEN 1 END) as delivered_count,
            COUNT(*) as total_deliveries
        FROM order_delivery
        WHERE courier_id = %s
    """, (courier_id,))
    
    stats = cursor.fetchone()
    cursor.close()
    connection.close()
    
    return stats

@courier_delivery_bp.route('/courier/delivery')
def delivery():
    if 'courier' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Courier':
        flash("Unauthorized access. Couriers only.", "danger")
        return redirect(url_for('login.login'))
    
    # Auto-cancel expired delivery assignments
    from blueprints.seller_orders import auto_cancel_expired_deliveries
    auto_cancel_expired_deliveries()
    
    courier_id = session['courier']
    
    # Get filter parameters
    status_filter = request.args.get('status', 'For Delivery')
    sort_by = request.args.get('sort_by', 'date_delivered')
    order = request.args.get('order', 'desc')
    search_query = request.args.get('search', '')
    
    # Get deliveries and statistics
    deliveries = get_courier_deliveries(courier_id, status_filter, sort_by, order, search_query)
    stats = get_delivery_statistics(courier_id)
    
    # Dynamic title and description based on status
    status_info = {
        'All': {'title': 'All Deliveries', 'description': 'Manage all your delivery assignments.'},
        'For Delivery': {'title': 'Pending Deliveries', 'description': 'Accept or decline delivery assignments.'},
        'Out for Delivery': {'title': 'Active Deliveries', 'description': 'Complete your ongoing deliveries.'},
        'Delivered': {'title': 'Completed Deliveries', 'description': 'View your completed delivery history.'}
    }
    
    current_status_info = status_info.get(status_filter, status_info['All'])
    
    return render_template('courier_delivery.html',
                         deliveries=deliveries,
                         stats=stats,
                         status_filter=status_filter,
                         sort_by=sort_by,
                         order=order,
                         search_query=search_query,
                         page_title=current_status_info['title'],
                         page_description=current_status_info['description'])

@courier_delivery_bp.route('/courier/delivery/accept/<int:delivery_id>', methods=['POST'])
def accept_delivery(delivery_id):
    if 'courier' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Courier':
        flash("Unauthorized access. Couriers only.", "danger")
        return redirect(url_for('login.login'))
    
    courier_id = session['courier']
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Verify delivery belongs to courier and is pending
        cursor.execute("""
            SELECT od.*, bo.buyer_id, bo.seller_id, pi.product_name,
                   buyer_pi.firstname as buyer_firstname, buyer_pi.lastname as buyer_lastname,
                   seller_pi.firstname as seller_firstname, seller_pi.lastname as seller_lastname
            FROM order_delivery od
            JOIN buyer_order bo ON od.order_id = bo.order_id
            JOIN product p ON bo.product_id = p.product_id
            JOIN product_info pi ON p.product_info_id = pi.product_info_id
            JOIN user_account buyer_ua ON bo.buyer_id = buyer_ua.user_id
            JOIN account_personal_info buyer_pi ON buyer_ua.personal_id = buyer_pi.personal_id
            JOIN user_account seller_ua ON bo.seller_id = seller_ua.user_id
            JOIN account_personal_info seller_pi ON seller_ua.personal_id = seller_pi.personal_id
            WHERE od.delivery_id = %s AND od.courier_id = %s AND od.status = 'For Delivery'
        """, (delivery_id, courier_id))
        
        delivery = cursor.fetchone()
        if not delivery:
            flash("Delivery not found or cannot be accepted.", "danger")
            return redirect(url_for('courier_delivery.delivery'))
        
        # Update delivery status to 'Out for Delivery'
        cursor.execute("""
            UPDATE order_delivery
            SET status = 'Out for Delivery'
            WHERE delivery_id = %s
        """, (delivery_id,))
        
        # Update order status to 'Out for Delivery'
        cursor.execute("""
            UPDATE buyer_order
            SET status = 'Out for Delivery'
            WHERE order_id = %s
        """, (delivery['order_id'],))
        
        # Create notifications
        admin_id = 1
        courier_name = f"{session.get('firstname', '')} {session.get('lastname', '')}"
        
        # Notify buyer
        buyer_notification = f"Great news! Your order #{delivery['order_id']} for {delivery['product_name']} is now out for delivery with courier {courier_name}."
        cursor.execute("""
            INSERT INTO notifications (recipient_id, sender_id, notification_type, notification_title, content, status)
            VALUES (%s, %s, 'Delivery Update', 'Order Out for Delivery', %s, 'Unread')
        """, (delivery['buyer_id'], admin_id, buyer_notification))
        
        # Notify seller
        seller_notification = f"Order #{delivery['order_id']} for {delivery['product_name']} has been accepted by courier {courier_name} and is now out for delivery to {delivery['buyer_firstname']} {delivery['buyer_lastname']}."
        cursor.execute("""
            INSERT INTO notifications (recipient_id, sender_id, notification_type, notification_title, content, status)
            VALUES (%s, %s, 'Delivery Update', 'Order Out for Delivery', %s, 'Unread')
        """, (delivery['seller_id'], admin_id, seller_notification))
        
        connection.commit()
        flash("Delivery accepted successfully! You can now proceed with the delivery.", "success")
        
    except Exception as e:
        connection.rollback()
        flash("Error accepting delivery. Please try again.", "danger")
        print(f"Accept delivery error: {e}")
    finally:
        cursor.close()
        connection.close()
    
    # Maintain the current filter status
    current_status = request.args.get('status', 'For Delivery')
    return redirect(url_for('courier_delivery.delivery', status=current_status))

@courier_delivery_bp.route('/courier/delivery/decline/<int:delivery_id>', methods=['POST'])
def decline_delivery(delivery_id):
    if 'courier' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Courier':
        flash("Unauthorized access. Couriers only.", "danger")
        return redirect(url_for('login.login'))
    
    courier_id = session['courier']
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Verify delivery belongs to courier and is pending
        cursor.execute("""
            SELECT od.*, bo.buyer_id, bo.seller_id, pi.product_name,
                   buyer_pi.firstname as buyer_firstname, buyer_pi.lastname as buyer_lastname,
                   seller_pi.firstname as seller_firstname, seller_pi.lastname as seller_lastname
            FROM order_delivery od
            JOIN buyer_order bo ON od.order_id = bo.order_id
            JOIN product p ON bo.product_id = p.product_id
            JOIN product_info pi ON p.product_info_id = pi.product_info_id
            JOIN user_account buyer_ua ON bo.buyer_id = buyer_ua.user_id
            JOIN account_personal_info buyer_pi ON buyer_ua.personal_id = buyer_pi.personal_id
            JOIN user_account seller_ua ON bo.seller_id = seller_ua.user_id
            JOIN account_personal_info seller_pi ON seller_ua.personal_id = seller_pi.personal_id
            WHERE od.delivery_id = %s AND od.courier_id = %s AND od.status = 'For Delivery'
        """, (delivery_id, courier_id))
        
        delivery = cursor.fetchone()
        if not delivery:
            flash("Delivery not found or cannot be declined.", "danger")
            return redirect(url_for('courier_delivery.delivery'))
        
        # Delete the delivery assignment
        cursor.execute("""
            DELETE FROM order_delivery
            WHERE delivery_id = %s
        """, (delivery_id,))
        
        # Update order status back to 'Shipped'
        cursor.execute("""
            UPDATE buyer_order
            SET status = 'Shipped'
            WHERE order_id = %s
        """, (delivery['order_id'],))
        
        # Create notifications
        admin_id = 1
        courier_name = f"{session.get('firstname', '')} {session.get('lastname', '')}"
        
        # Notify seller
        seller_notification = f"Courier {courier_name} has declined the delivery assignment for Order #{delivery['order_id']} ({delivery['product_name']}). Please assign a new courier for delivery to {delivery['buyer_firstname']} {delivery['buyer_lastname']}."
        cursor.execute("""
            INSERT INTO notifications (recipient_id, sender_id, notification_type, notification_title, content, status)
            VALUES (%s, %s, 'Delivery Alert', 'Courier Declined Delivery - Order #{delivery_order_id}', %s, 'Unread')
        """, (delivery['seller_id'], admin_id, seller_notification.replace('{delivery_order_id}', str(delivery['order_id']))))
        
        connection.commit()
        flash("Delivery declined. The seller will be notified to assign a new courier.", "info")
        
    except Exception as e:
        connection.rollback()
        flash("Error declining delivery. Please try again.", "danger")
        print(f"Decline delivery error: {e}")
    finally:
        cursor.close()
        connection.close()
    
    # Maintain the current filter status
    current_status = request.args.get('status', 'For Delivery')
    return redirect(url_for('courier_delivery.delivery', status=current_status))

@courier_delivery_bp.route('/courier/delivery/complete/<int:delivery_id>', methods=['POST'])
def mark_delivered(delivery_id):
    if 'courier' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Courier':
        flash("Unauthorized access. Couriers only.", "danger")
        return redirect(url_for('login.login'))
    
    courier_id = session['courier']
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Verify delivery belongs to courier and is out for delivery
        cursor.execute("""
            SELECT od.*, bo.buyer_id, bo.seller_id, pi.product_name,
                   buyer_pi.firstname as buyer_firstname, buyer_pi.lastname as buyer_lastname,
                   seller_pi.firstname as seller_firstname, seller_pi.lastname as seller_lastname
            FROM order_delivery od
            JOIN buyer_order bo ON od.order_id = bo.order_id
            JOIN product p ON bo.product_id = p.product_id
            JOIN product_info pi ON p.product_info_id = pi.product_info_id
            JOIN user_account buyer_ua ON bo.buyer_id = buyer_ua.user_id
            JOIN account_personal_info buyer_pi ON buyer_ua.personal_id = buyer_pi.personal_id
            JOIN user_account seller_ua ON bo.seller_id = seller_ua.user_id
            JOIN account_personal_info seller_pi ON seller_ua.personal_id = seller_pi.personal_id
            WHERE od.delivery_id = %s AND od.courier_id = %s AND od.status = 'Out for Delivery'
        """, (delivery_id, courier_id))
        
        delivery = cursor.fetchone()
        if not delivery:
            flash("Delivery not found or cannot be marked as delivered.", "danger")
            return redirect(url_for('courier_delivery.delivery'))
        
        # Update delivery status to 'Delivered'
        cursor.execute("""
            UPDATE order_delivery
            SET status = 'Delivered'
            WHERE delivery_id = %s
        """, (delivery_id,))
        
        # Update order status to 'Delivered' and payment status to 'Paid'
        cursor.execute("""
            UPDATE buyer_order
            SET status = 'Delivered', payment_status = 'Paid'
            WHERE order_id = %s
        """, (delivery['order_id'],))
        
        # Create notifications
        admin_id = 1
        courier_name = f"{session.get('firstname', '')} {session.get('lastname', '')}"
        
        # Insert into order_received table
        cursor.execute("""
            INSERT INTO order_received (order_id, buyer_id, date_received, status)
            VALUES (%s, %s, NOW(), 'Received')
        """, (delivery['order_id'], delivery['buyer_id']))
        
        # Insert into order_completed table
        cursor.execute("""
            INSERT INTO order_completed (order_id, date_completed, status)
            VALUES (%s, NOW(), 'Completed')
        """, (delivery['order_id'],))
        
        # Notify buyer
        buyer_notification = f"Your order #{delivery['order_id']} for {delivery['product_name']} has been successfully delivered and payment has been confirmed. Thank you for your purchase!"
        cursor.execute("""
            INSERT INTO notifications (recipient_id, sender_id, notification_type, notification_title, content, status)
            VALUES (%s, %s, 'Order Complete', 'Order Delivered & Payment Confirmed', %s, 'Unread')
        """, (delivery['buyer_id'], admin_id, buyer_notification))
        
        # Notify seller
        seller_notification = f"Order #{delivery['order_id']} for {delivery['product_name']} has been successfully delivered to {delivery['buyer_firstname']} {delivery['buyer_lastname']} by courier {courier_name}. Payment has been confirmed and the order is now complete."
        cursor.execute("""
            INSERT INTO notifications (recipient_id, sender_id, notification_type, notification_title, content, status)
            VALUES (%s, %s, 'Order Complete', 'Order Delivered & Payment Confirmed', %s, 'Unread')
        """, (delivery['seller_id'], admin_id, seller_notification))
        
        connection.commit()
        flash("Delivery completed successfully! Payment has been confirmed and order is complete.", "success")
        
    except Exception as e:
        connection.rollback()
        flash("Error marking delivery as completed. Please try again.", "danger")
        print(f"Mark delivered error: {e}")
    finally:
        cursor.close()
        connection.close()
    
    # Maintain the current filter status
    current_status = request.args.get('status', 'Out for Delivery')
    return redirect(url_for('courier_delivery.delivery', status=current_status))

# Routes to serve product images
@courier_delivery_bp.route('/uploads/product_main_pics/<filename>')
def serve_product_main_pic(filename):
    return send_from_directory(PRODUCT_MAIN_PIC_FOLDER, filename)

@courier_delivery_bp.route('/uploads/product_images/<filename>')
def serve_product_image(filename):
    return send_from_directory(PRODUCT_IMAGES_FOLDER, filename)

@courier_delivery_bp.route('/uploads/product_variant_images/<filename>')
def serve_product_variant_image(filename):
    return send_from_directory(PRODUCT_VARIANT_IMAGES_FOLDER, filename)