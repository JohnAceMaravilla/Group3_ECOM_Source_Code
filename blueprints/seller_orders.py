# IMPORTS
from flask import Blueprint, render_template, flash, session, redirect, url_for, request, send_from_directory, jsonify
from db_connection import get_db_connection
from datetime import datetime, timedelta
import os

seller_orders_bp = Blueprint('seller_orders', __name__)

# Constants for image folders
PRODUCT_MAIN_PIC_FOLDER = "static/uploads/seller/product_main_pics"
PRODUCT_IMAGES_FOLDER = "static/uploads/seller/product_images"
PRODUCT_VARIANT_IMAGES_FOLDER = "static/uploads/seller/product_variant_images"

def auto_cancel_expired_deliveries():
    """Automatically cancel delivery assignments that haven't been accepted within 8 hours"""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Find deliveries that are 'For Delivery' and older than 8 hours
        cursor.execute("""
            SELECT od.delivery_id, od.order_id, od.courier_id, 
                   bo.buyer_id, bo.seller_id, pi.product_name,
                   buyer_pi.firstname as buyer_firstname, buyer_pi.lastname as buyer_lastname,
                   seller_pi.firstname as seller_firstname, seller_pi.lastname as seller_lastname,
                   courier_pi.firstname as courier_firstname, courier_pi.lastname as courier_lastname
            FROM order_delivery od
            JOIN buyer_order bo ON od.order_id = bo.order_id
            JOIN product p ON bo.product_id = p.product_id
            JOIN product_info pi ON p.product_info_id = pi.product_info_id
            JOIN user_account buyer_ua ON bo.buyer_id = buyer_ua.user_id
            JOIN account_personal_info buyer_pi ON buyer_ua.personal_id = buyer_pi.personal_id
            JOIN user_account seller_ua ON bo.seller_id = seller_ua.user_id
            JOIN account_personal_info seller_pi ON seller_ua.personal_id = seller_pi.personal_id
            JOIN user_account courier_ua ON od.courier_id = courier_ua.user_id
            JOIN account_personal_info courier_pi ON courier_ua.personal_id = courier_pi.personal_id
            WHERE od.status = 'For Delivery' 
            AND od.date_delivered < NOW() - INTERVAL 8 HOUR
        """)
        
        expired_deliveries = cursor.fetchall()
        
        for delivery in expired_deliveries:
            # Delete the expired delivery assignment
            cursor.execute("""
                DELETE FROM order_delivery
                WHERE delivery_id = %s
            """, (delivery['delivery_id'],))
            
            # Update order status back to 'Shipped'
            cursor.execute("""
                UPDATE buyer_order
                SET status = 'Shipped'
                WHERE order_id = %s
            """, (delivery['order_id'],))
            
            # Create notifications
            admin_id = 1
            courier_name = f"{delivery['courier_firstname']} {delivery['courier_lastname']}"
            
            # Notify seller
            seller_notification = f"Delivery assignment for Order #{delivery['order_id']} ({delivery['product_name']}) has been automatically cancelled due to courier {courier_name} not responding within 8 hours. Please assign a new courier for delivery to {delivery['buyer_firstname']} {delivery['buyer_lastname']}."
            cursor.execute("""
                INSERT INTO notifications (recipient_id, sender_id, notification_type, notification_title, content, status)
                VALUES (%s, %s, 'Delivery Alert', 'Delivery Assignment Expired - Order #{order_id}', %s, 'Unread')
            """, (delivery['seller_id'], admin_id, seller_notification.replace('{order_id}', str(delivery['order_id']))))
            
            # Notify courier about missed opportunity
            courier_notification = f"You missed the delivery assignment for Order #{delivery['order_id']} ({delivery['product_name']}) as you did not respond within 8 hours. The assignment has been cancelled and returned to the seller."
            cursor.execute("""
                INSERT INTO notifications (recipient_id, sender_id, notification_type, notification_title, content, status)
                VALUES (%s, %s, 'Delivery Missed', 'Delivery Assignment Expired - Order #{order_id}', %s, 'Unread')
            """, (delivery['courier_id'], admin_id, courier_notification.replace('{order_id}', str(delivery['order_id']))))
        
        connection.commit()
        print(f"Auto-cancelled {len(expired_deliveries)} expired delivery assignments")
        
    except Exception as e:
        connection.rollback()
        print(f"Error auto-cancelling expired deliveries: {e}")
    finally:
        cursor.close()
        connection.close()

def get_order_statistics(seller_id):
    """Get order statistics for the seller"""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT 
            COUNT(CASE WHEN status = 'Pending' THEN 1 END) as pending_orders,
            COUNT(CASE WHEN status = 'To Pack' THEN 1 END) as to_pack_orders,
            COUNT(CASE WHEN status = 'Packed' THEN 1 END) as packed_orders,
            COUNT(CASE WHEN status = 'Shipping' THEN 1 END) as shipping_orders,
            COUNT(CASE WHEN status IN ('Shipped', 'Out for Delivery') THEN 1 END) as shipped_orders,
            COUNT(CASE WHEN status = 'Delivered' THEN 1 END) as delivered_orders,
            COUNT(CASE WHEN status IN ('Delivered', 'Received') THEN 1 END) as completed_orders
        FROM buyer_order
        WHERE seller_id = %s
    """, (seller_id,))
    
    stats = cursor.fetchone()
    cursor.close()
    connection.close()
    
    return stats

def get_seller_orders(seller_id, status_filter='All', sort_by='date_ordered', order='desc', search_query=''):
    """Get orders for a specific seller with filtering and sorting"""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Base query
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
        JOIN user_account buyer_ua ON bo.buyer_id = buyer_ua.user_id
        JOIN account_personal_info buyer_pi ON buyer_ua.personal_id = buyer_pi.personal_id
        JOIN account_contact_info buyer_ci ON buyer_ua.contact_id = buyer_ci.contact_id
        JOIN account_address_info buyer_ai ON buyer_ua.address_id = buyer_ai.address_id
        WHERE bo.seller_id = %s
    """
    
    params = [seller_id]
    
    # Add status filter
    if status_filter != 'All':
        query += " AND bo.status = %s"
        params.append(status_filter)
    
    # Add search filter
    if search_query:
        query += """ AND (
            pi.product_name LIKE %s OR
            buyer_pi.firstname LIKE %s OR
            buyer_pi.lastname LIKE %s OR
            buyer_ci.email LIKE %s OR
            bo.order_id LIKE %s
        )"""
        search_term = f"%{search_query}%"
        params.extend([search_term] * 5)
    
    # Add sorting
    allowed_sort_columns = {
        'date_ordered': 'bo.date_ordered',
        'product_name': 'pi.product_name',
        'buyer_name': 'buyer_pi.firstname',
        'total_amount': 'bo.total_amount',
        'status': 'bo.status'
    }
    
    if sort_by in allowed_sort_columns:
        sort_column = allowed_sort_columns[sort_by]
        order_direction = 'DESC' if order.lower() == 'desc' else 'ASC'
        query += f" ORDER BY {sort_column} {order_direction}"
    else:
        query += " ORDER BY bo.date_ordered DESC"
    
    cursor.execute(query, params)
    orders = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return orders

@seller_orders_bp.route('/seller/orders')
def orders():
    if 'seller' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Seller':
        flash("Unauthorized access. Sellers only.", "danger")
        return redirect(url_for('login.login'))
    
    # Auto-cancel expired delivery assignments
    auto_cancel_expired_deliveries()
    
    seller_id = session['seller']
    
    # Get filter parameters
    status_filter = request.args.get('status', 'Pending')
    sort_by = request.args.get('sort_by', 'date_ordered')
    order = request.args.get('order', 'desc')
    search_query = request.args.get('search', '')
    
    # Get orders and statistics
    orders = get_seller_orders(seller_id, status_filter, sort_by, order, search_query)
    stats = get_order_statistics(seller_id)
    
    # Dynamic title and description based on status
    status_info = {
        'All': {'title': 'Orders', 'description': 'Manage all your customer orders.'},
        'Pending': {'title': 'Pending Orders', 'description': 'Review and approve pending customer orders.'},
        'To Pack': {'title': 'Orders To Pack', 'description': 'Pack approved orders for shipment.'},
        'Packed': {'title': 'Packed Orders', 'description': 'Hand-off packed orders to logistics.'},
        'Shipping': {'title': 'Shipping Orders', 'description': 'Track orders in shipping process.'},
        'Shipped': {'title': 'Shipped Orders', 'description': 'Assign couriers for final delivery.'},
        'Out for Delivery': {'title': 'Orders Out for Delivery', 'description': 'Orders currently being delivered by couriers.'},
        'Delivered': {'title': 'Delivered Orders', 'description': 'Orders delivered and awaiting confirmation.'},
        'Received': {'title': 'Received Orders', 'description': 'Orders confirmed as received by customers.'},
        'Rejected': {'title': 'Rejected Orders', 'description': 'Orders that were rejected and need attention.'}
    }
    
    current_status_info = status_info.get(status_filter, status_info['All'])
    
    return render_template('seller_orders.html', 
                         orders=orders,
                         stats=stats,
                         status_filter=status_filter,
                         sort_by=sort_by,
                         order=order,
                         search_query=search_query,
                         page_title=current_status_info['title'],
                         page_description=current_status_info['description'])

@seller_orders_bp.route('/seller/orders/approve/<int:order_id>', methods=['POST'])
def approve_order(order_id):
    if 'seller' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Seller':
        flash("Unauthorized access. Sellers only.", "danger")
        return redirect(url_for('login.login'))
    
    seller_id = session['seller']
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Verify order belongs to seller and is pending
        cursor.execute("""
            SELECT bo.*, pi.product_name, buyer_pi.firstname, buyer_pi.lastname
            FROM buyer_order bo
            JOIN product p ON bo.product_id = p.product_id
            JOIN product_info pi ON p.product_info_id = pi.product_info_id
            JOIN user_account buyer_ua ON bo.buyer_id = buyer_ua.user_id
            JOIN account_personal_info buyer_pi ON buyer_ua.personal_id = buyer_pi.personal_id
            WHERE bo.order_id = %s AND bo.seller_id = %s AND bo.status = 'Pending'
        """, (order_id, seller_id))
        
        order = cursor.fetchone()
        if not order:
            flash("Order not found or cannot be approved.", "danger")
            return redirect(url_for('seller_orders.orders'))
        
        # Update order status to 'To Pack'
        cursor.execute("""
            UPDATE buyer_order
            SET status = 'To Pack'
            WHERE order_id = %s
        """, (order_id,))
        
        # Create notification for buyer
        admin_id = 1
        buyer_name = f"{order['firstname']} {order['lastname']}"
        notification_content = f"Your order for {order['product_name']} has been approved and is now being prepared for packing."
        
        cursor.execute("""
            INSERT INTO notifications (recipient_id, sender_id, notification_type, notification_title, content, status)
            VALUES (%s, %s, 'Order Update', 'Order Approved', %s, 'Unread')
        """, (order['buyer_id'], admin_id, notification_content))
        
        connection.commit()
        flash("Order approved successfully!", "success")
        
    except Exception as e:
        connection.rollback()
        flash("Error approving order. Please try again.", "danger")
        print(f"Approve order error: {e}")
    finally:
        cursor.close()
        connection.close()
    
    # Maintain the current filter status
    current_status = request.args.get('status', 'Pending')
    return redirect(url_for('seller_orders.orders', status=current_status))

@seller_orders_bp.route('/seller/orders/reject/<int:order_id>', methods=['POST'])
def reject_order(order_id):
    if 'seller' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Seller':
        flash("Unauthorized access. Sellers only.", "danger")
        return redirect(url_for('login.login'))
    
    seller_id = session['seller']
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Verify order belongs to seller and is pending
        cursor.execute("""
            SELECT bo.*, pi.product_name, buyer_pi.firstname, buyer_pi.lastname
            FROM buyer_order bo
            JOIN product p ON bo.product_id = p.product_id
            JOIN product_info pi ON p.product_info_id = pi.product_info_id
            JOIN user_account buyer_ua ON bo.buyer_id = buyer_ua.user_id
            JOIN account_personal_info buyer_pi ON buyer_ua.personal_id = buyer_pi.personal_id
            WHERE bo.order_id = %s AND bo.seller_id = %s AND bo.status = 'Pending'
        """, (order_id, seller_id))
        
        order = cursor.fetchone()
        if not order:
            flash("Order not found or cannot be rejected.", "danger")
            return redirect(url_for('seller_orders.orders'))
        
        # Update order status to 'Rejected'
        cursor.execute("""
            UPDATE buyer_order
            SET status = 'Rejected'
            WHERE order_id = %s
        """, (order_id,))
        
        # Restore product stock
        cursor.execute("""
            UPDATE product
            SET stock = stock + %s,
                stock_status = CASE
                    WHEN stock + %s > 10 THEN 'Active'
                    WHEN stock + %s > 0 THEN 'Nearly Out of Stock'
                    ELSE 'Out of Stock'
                END
            WHERE product_id = %s
        """, (order['quantity'], order['quantity'], order['quantity'], order['product_id']))
        
        # Create notification for buyer
        admin_id = 1
        buyer_name = f"{order['firstname']} {order['lastname']}"
        notification_content = f"Unfortunately, your order for {order['product_name']} has been rejected. The amount will be refunded if payment was made."
        
        cursor.execute("""
            INSERT INTO notifications (recipient_id, sender_id, notification_type, notification_title, content, status)
            VALUES (%s, %s, 'Order Update', 'Order Rejected', %s, 'Unread')
        """, (order['buyer_id'], admin_id, notification_content))
        
        connection.commit()
        flash("Order rejected successfully!", "success")
        
    except Exception as e:
        connection.rollback()
        flash("Error rejecting order. Please try again.", "danger")
        print(f"Reject order error: {e}")
    finally:
        cursor.close()
        connection.close()
    
    # Maintain the current filter status
    current_status = request.args.get('status', 'Pending')
    return redirect(url_for('seller_orders.orders', status=current_status))

@seller_orders_bp.route('/seller/orders/pack/<int:order_id>', methods=['POST'])
def mark_as_packed(order_id):
    if 'seller' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Seller':
        flash("Unauthorized access. Sellers only.", "danger")
        return redirect(url_for('login.login'))
    
    seller_id = session['seller']
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Verify order belongs to seller and is in 'To Pack' status
        cursor.execute("""
            SELECT bo.*, pi.product_name, buyer_pi.firstname, buyer_pi.lastname
            FROM buyer_order bo
            JOIN product p ON bo.product_id = p.product_id
            JOIN product_info pi ON p.product_info_id = pi.product_info_id
            JOIN user_account buyer_ua ON bo.buyer_id = buyer_ua.user_id
            JOIN account_personal_info buyer_pi ON buyer_ua.personal_id = buyer_pi.personal_id
            WHERE bo.order_id = %s AND bo.seller_id = %s AND bo.status = 'To Pack'
        """, (order_id, seller_id))
        
        order = cursor.fetchone()
        if not order:
            flash("Order not found or cannot be marked as packed.", "danger")
            return redirect(url_for('seller_orders.orders'))
        
        # Update order status to 'Packed'
        cursor.execute("""
            UPDATE buyer_order
            SET status = 'Packed'
            WHERE order_id = %s
        """, (order_id,))
        
        # Insert into order_packing table
        cursor.execute("""
            INSERT INTO order_packing (order_id, status, date_packed)
            VALUES (%s, 'Packed', NOW())
        """, (order_id,))
        
        # Create notification for buyer
        admin_id = 1
        notification_content = f"Your order for {order['product_name']} has been packed and is ready for shipment."
        
        cursor.execute("""
            INSERT INTO notifications (recipient_id, sender_id, notification_type, notification_title, content, status)
            VALUES (%s, %s, 'Order Update', 'Order Packed', %s, 'Unread')
        """, (order['buyer_id'], admin_id, notification_content))
        
        connection.commit()
        flash("Order marked as packed successfully!", "success")
        
    except Exception as e:
        connection.rollback()
        flash("Error marking order as packed. Please try again.", "danger")
        print(f"Pack order error: {e}")
    finally:
        cursor.close()
        connection.close()
    
    # Maintain the current filter status
    current_status = request.args.get('status', 'To Pack')
    return redirect(url_for('seller_orders.orders', status=current_status))

@seller_orders_bp.route('/seller/orders/handoff/<int:order_id>', methods=['POST'])
def handoff_to_logistics(order_id):
    if 'seller' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Seller':
        flash("Unauthorized access. Sellers only.", "danger")
        return redirect(url_for('login.login'))
    
    seller_id = session['seller']
    logistic_name = request.form.get('logistic_name', 'Standard Shipping')
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Verify order belongs to seller and is packed
        cursor.execute("""
            SELECT bo.*, pi.product_name, buyer_pi.firstname, buyer_pi.lastname
            FROM buyer_order bo
            JOIN product p ON bo.product_id = p.product_id
            JOIN product_info pi ON p.product_info_id = pi.product_info_id
            JOIN user_account buyer_ua ON bo.buyer_id = buyer_ua.user_id
            JOIN account_personal_info buyer_pi ON buyer_ua.personal_id = buyer_pi.personal_id
            WHERE bo.order_id = %s AND bo.seller_id = %s AND bo.status = 'Packed'
        """, (order_id, seller_id))
        
        order = cursor.fetchone()
        if not order:
            flash("Order not found or cannot be handed off.", "danger")
            return redirect(url_for('seller_orders.orders'))
        
        # Update order status to 'Shipping'
        cursor.execute("""
            UPDATE buyer_order
            SET status = 'Shipping'
            WHERE order_id = %s
        """, (order_id,))
        
        # Insert into order_shipping table (date_shipped is NULL initially)
        cursor.execute("""
            INSERT INTO order_shipping (order_id, logistic_name, date_shipping, date_shipped, status)
            VALUES (%s, %s, NOW(), NULL, 'Shipping')
        """, (order_id, logistic_name))
        
        # Create notification for buyer
        admin_id = 1
        notification_content = f"Your order for {order['product_name']} has been handed off to {logistic_name} and is now in shipping process."
        
        cursor.execute("""
            INSERT INTO notifications (recipient_id, sender_id, notification_type, notification_title, content, status)
            VALUES (%s, %s, 'Order Update', 'Order in Shipping', %s, 'Unread')
        """, (order['buyer_id'], admin_id, notification_content))
        
        connection.commit()
        flash("Order handed off to logistics successfully!", "success")
        
    except Exception as e:
        connection.rollback()
        flash("Error handing off order. Please try again.", "danger")
        print(f"Handoff order error: {e}")
    finally:
        cursor.close()
        connection.close()
    
    # Maintain the current filter status
    current_status = request.args.get('status', 'Packed')
    return redirect(url_for('seller_orders.orders', status=current_status))

@seller_orders_bp.route('/seller/orders/ship/<int:order_id>', methods=['POST'])
def mark_as_shipped(order_id):
    if 'seller' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Seller':
        flash("Unauthorized access. Sellers only.", "danger")
        return redirect(url_for('login.login'))
    
    seller_id = session['seller']
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Verify order belongs to seller and is shipping
        cursor.execute("""
            SELECT bo.*, pi.product_name, buyer_pi.firstname, buyer_pi.lastname
            FROM buyer_order bo
            JOIN product p ON bo.product_id = p.product_id
            JOIN product_info pi ON p.product_info_id = pi.product_info_id
            JOIN user_account buyer_ua ON bo.buyer_id = buyer_ua.user_id
            JOIN account_personal_info buyer_pi ON buyer_ua.personal_id = buyer_pi.personal_id
            WHERE bo.order_id = %s AND bo.seller_id = %s AND bo.status = 'Shipping'
        """, (order_id, seller_id))
        
        order = cursor.fetchone()
        if not order:
            flash("Order not found or cannot be marked as shipped.", "danger")
            return redirect(url_for('seller_orders.orders'))
        
        # Update order status to 'Shipped'
        cursor.execute("""
            UPDATE buyer_order
            SET status = 'Shipped'
            WHERE order_id = %s
        """, (order_id,))
        
        # Update order_shipping table with date_shipped
        cursor.execute("""
            UPDATE order_shipping
            SET date_shipped = NOW(), status = 'Shipped'
            WHERE order_id = %s
        """, (order_id,))
        
        # Create notification for buyer
        admin_id = 1
        notification_content = f"Your order for {order['product_name']} has been shipped and is on its way to you."
        
        cursor.execute("""
            INSERT INTO notifications (recipient_id, sender_id, notification_type, notification_title, content, status)
            VALUES (%s, %s, 'Order Update', 'Order Shipped', %s, 'Unread')
        """, (order['buyer_id'], admin_id, notification_content))
        
        connection.commit()
        flash("Order marked as shipped successfully!", "success")
        
    except Exception as e:
        connection.rollback()
        flash("Error marking order as shipped. Please try again.", "danger")
        print(f"Ship order error: {e}")
    finally:
        cursor.close()
        connection.close()
    
    # Maintain the current filter status
    current_status = request.args.get('status', 'Shipping')
    return redirect(url_for('seller_orders.orders', status=current_status))

@seller_orders_bp.route('/seller/orders/assign_courier/<int:order_id>', methods=['POST'])
def assign_courier(order_id):
    if 'seller' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Seller':
        flash("Unauthorized access. Sellers only.", "danger")
        return redirect(url_for('login.login'))
    
    seller_id = session['seller']
    courier_id = request.form.get('courier_id')
    
    if not courier_id:
        flash("Please select a courier.", "danger")
        return redirect(url_for('seller_orders.orders'))
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Verify order belongs to seller and is shipped
        cursor.execute("""
            SELECT bo.*, pi.product_name, buyer_pi.firstname, buyer_pi.lastname
            FROM buyer_order bo
            JOIN product p ON bo.product_id = p.product_id
            JOIN product_info pi ON p.product_info_id = pi.product_info_id
            JOIN user_account buyer_ua ON bo.buyer_id = buyer_ua.user_id
            JOIN account_personal_info buyer_pi ON buyer_ua.personal_id = buyer_pi.personal_id
            WHERE bo.order_id = %s AND bo.seller_id = %s AND bo.status = 'Shipped'
        """, (order_id, seller_id))
        
        order = cursor.fetchone()
        if not order:
            flash("Order not found or cannot assign courier.", "danger")
            return redirect(url_for('seller_orders.orders'))
        
        # Update order status to 'For Delivery'
        cursor.execute("""
            UPDATE buyer_order
            SET status = 'For Delivery'
            WHERE order_id = %s
        """, (order_id,))
        
        # Insert into order_delivery table
        cursor.execute("""
            INSERT INTO order_delivery (order_id, courier_id, date_delivered, status)
            VALUES (%s, %s, NOW(), 'For Delivery')
        """, (order_id, courier_id))
        
        # Get courier info for notification
        cursor.execute("""
            SELECT pi.firstname, pi.lastname
            FROM user_account ua
            JOIN account_personal_info pi ON ua.personal_id = pi.personal_id
            WHERE ua.user_id = %s
        """, (courier_id,))
        courier_info = cursor.fetchone()
        
        # Create notification for buyer
        admin_id = 1
        courier_name = f"{courier_info['firstname']} {courier_info['lastname']}" if courier_info else "a courier"
        notification_content = f"Your order #{order_id} for {order['product_name']} has been assigned to courier {courier_name} and is awaiting acceptance for delivery."
        
        cursor.execute("""
            INSERT INTO notifications (recipient_id, sender_id, notification_type, notification_title, content, status)
            VALUES (%s, %s, 'Order Update', 'Courier Assigned', %s, 'Unread')
        """, (order['buyer_id'], admin_id, notification_content))
        
        # Create notification for courier
        courier_notification = f"You have been assigned to deliver Order #{order_id} for {order['product_name']} to {order['firstname']} {order['lastname']}. Please accept or decline this delivery assignment within 8 hours."
        courier_notification_title = f"New Delivery Assignment - Order #{order_id}";
        cursor.execute("""
            INSERT INTO notifications (recipient_id, sender_id, notification_type, notification_title, content, status)
            VALUES (%s, %s, 'Delivery Assignment', %s, %s, 'Unread')
        """, (courier_id, admin_id, courier_notification_title, courier_notification.replace(f"Order #{order_id}", f"Order #{order_id}")))
        
        connection.commit()
        flash("Courier assigned successfully!", "success")
        
    except Exception as e:
        connection.rollback()
        flash("Error assigning courier. Please try again.", "danger")
        print(f"Assign courier error: {e}")
    finally:
        cursor.close()
        connection.close()
    
    # Maintain the current filter status
    current_status = request.args.get('status', 'Shipped')
    return redirect(url_for('seller_orders.orders', status=current_status))

@seller_orders_bp.route('/seller/orders/get_couriers/<int:order_id>')
def get_available_couriers(order_id):
    """Get available couriers for a specific order based on buyer's location"""
    if 'seller' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Seller':
        return jsonify({'couriers': []})
    
    seller_id = session['seller']
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Get buyer's location for this order
        cursor.execute("""
            SELECT buyer_ai.city, buyer_ai.province, buyer_ai.region
            FROM buyer_order bo
            JOIN user_account buyer_ua ON bo.buyer_id = buyer_ua.user_id
            JOIN account_address_info buyer_ai ON buyer_ua.address_id = buyer_ai.address_id
            WHERE bo.order_id = %s AND bo.seller_id = %s
        """, (order_id, seller_id))
        
        buyer_location = cursor.fetchone()
        if not buyer_location:
            return jsonify({'couriers': []})
        
        # Get couriers in the same location
        cursor.execute("""
            SELECT ua.user_id, pi.firstname, pi.lastname, ci.phone
            FROM user_account ua
            JOIN account_personal_info pi ON ua.personal_id = pi.personal_id
            JOIN account_contact_info ci ON ua.contact_id = ci.contact_id
            JOIN account_address_info ai ON ua.address_id = ai.address_id
            WHERE ua.user_role = 'Courier' 
            AND ua.status = 'Approved'
            AND ai.city = %s 
            AND ai.province = %s 
            AND ai.region = %s
        """, (buyer_location['city'], buyer_location['province'], buyer_location['region']))
        
        couriers = cursor.fetchall()
        
        return jsonify({'couriers': couriers})
        
    except Exception as e:
        print(f"Get couriers error: {e}")
        return jsonify({'couriers': []})
    finally:
        cursor.close()
        connection.close()

# Routes to serve product images
@seller_orders_bp.route('/uploads/product_main_pics/<filename>')
def serve_product_main_pic(filename):
    return send_from_directory(PRODUCT_MAIN_PIC_FOLDER, filename)

@seller_orders_bp.route('/uploads/product_images/<filename>')
def serve_product_image(filename):
    return send_from_directory(PRODUCT_IMAGES_FOLDER, filename)

@seller_orders_bp.route('/uploads/product_variant_images/<filename>')
def serve_product_variant_image(filename):
    return send_from_directory(PRODUCT_VARIANT_IMAGES_FOLDER, filename)