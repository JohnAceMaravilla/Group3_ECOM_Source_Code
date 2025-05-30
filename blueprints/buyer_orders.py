# IMPORTS
from flask import Blueprint, render_template, flash, session, redirect, url_for, request, send_from_directory, jsonify
from db_connection import get_db_connection
from datetime import datetime, timedelta
import os

buyer_orders_bp = Blueprint('buyer_orders', __name__)

# Constants for image folders
PRODUCT_MAIN_PIC_FOLDER = "static/uploads/seller/product_main_pics"
PRODUCT_IMAGES_FOLDER = "static/uploads/seller/product_images"
PRODUCT_VARIANT_IMAGES_FOLDER = "static/uploads/seller/product_variant_images"

def get_buyer_orders(buyer_id, status_filter='All', sort_by='date_ordered', order='desc', search_query=''):
    """Get orders for a specific buyer with filtering and sorting"""
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
            seller_pi.firstname as seller_firstname,
            seller_pi.lastname as seller_lastname,
            seller_ci.email as seller_email,
            seller_ci.phone as seller_phone,
            -- Check if review exists for this specific order by checking if there's a review for this product after this order was received
            (SELECT COUNT(*) 
             FROM product_rating pr 
             WHERE pr.product_id = bo.product_id 
             AND pr.sender_id = bo.buyer_id 
             AND EXISTS (
                 SELECT 1 FROM order_received ore 
                 WHERE ore.order_id = bo.order_id 
                 AND pr.date_rated >= ore.date_received
             )) as has_review
        FROM buyer_order bo
        JOIN product p ON bo.product_id = p.product_id
        JOIN product_info pi ON p.product_info_id = pi.product_info_id
        JOIN shop s ON bo.shop_id = s.shop_id
        JOIN shop_info si ON s.shop_info_id = si.shop_info_id
        JOIN user_account seller_ua ON bo.seller_id = seller_ua.user_id
        JOIN account_personal_info seller_pi ON seller_ua.personal_id = seller_pi.personal_id
        JOIN account_contact_info seller_ci ON seller_ua.contact_id = seller_ci.contact_id
        WHERE bo.buyer_id = %s
    """
    
    params = [buyer_id]
    
    # Add status filter
    if status_filter != 'All':
        if status_filter == 'Pending':
            query += " AND bo.status = 'Pending'"
        elif status_filter == 'To Pack':
            query += " AND bo.status IN ('To Pack', 'Packed')"
        elif status_filter == 'To Ship':
            query += " AND bo.status IN ('Shipping', 'Shipped')"
        elif status_filter == 'To Deliver':
            query += " AND bo.status IN ('For Delivery', 'Out for Delivery', 'Delivered')"
        elif status_filter == 'Completed':
            query += " AND bo.status = 'Received'"
        else:
            query += " AND bo.status = %s"
            params.append(status_filter)
    
    # Add search filter
    if search_query:
        query += """ AND (
            pi.product_name LIKE %s OR
            si.shop_name LIKE %s OR
            seller_pi.firstname LIKE %s OR
            seller_pi.lastname LIKE %s OR
            bo.order_id LIKE %s
        )"""
        search_term = f"%{search_query}%"
        params.extend([search_term] * 5)
    
    # Add sorting
    allowed_sort_columns = {
        'date_ordered': 'bo.date_ordered',
        'product_name': 'pi.product_name',
        'shop_name': 'si.shop_name',
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

def get_order_statistics(buyer_id):
    """Get order statistics for the buyer"""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT 
            COUNT(CASE WHEN status = 'Pending' THEN 1 END) as pending_orders,
            COUNT(CASE WHEN status IN ('To Pack', 'Packed') THEN 1 END) as to_pack_orders,
            COUNT(CASE WHEN status IN ('Shipping', 'Shipped') THEN 1 END) as to_ship_orders,
            COUNT(CASE WHEN status IN ('For Delivery', 'Out for Delivery', 'Delivered') THEN 1 END) as to_deliver_orders,
            COUNT(CASE WHEN status = 'Received' THEN 1 END) as completed_orders,
            COUNT(*) as total_orders
        FROM buyer_order
        WHERE buyer_id = %s
    """, (buyer_id,))
    
    stats = cursor.fetchone()
    cursor.close()
    connection.close()
    
    return stats

def calculate_and_record_sales_with_cursor(cursor, order_id):
    """Calculate and record sales, commissions when order is received using existing cursor"""
    try:
        # Get order details with shipping fee from product table
        cursor.execute("""
            SELECT bo.*, p.shipping_fee, od.courier_id
            FROM buyer_order bo
            JOIN product p ON bo.product_id = p.product_id
            LEFT JOIN order_delivery od ON bo.order_id = od.order_id
            WHERE bo.order_id = %s
        """, (order_id,))
        
        order = cursor.fetchone()
        if not order:
            return False
        
        admin_id = 1
        commission_rate = 8.00  # 8% commission as specified
        
        # Calculate amounts - convert Decimal to float for calculations
        total_amount = float(order['total_amount'])
        shipping_fee = float(order['shipping_fee'])
        subtotal = total_amount - shipping_fee  # Seller gets subtotal
        
        seller_commission = (subtotal * commission_rate) / 100
        courier_commission = (shipping_fee * commission_rate) / 100
        
        # Calculate net amounts (after commission)
        seller_net = subtotal - seller_commission
        courier_net = shipping_fee - courier_commission
        
        # Insert admin commission for seller
        cursor.execute("""
            INSERT INTO admin_order_commission (order_id, seller_id, commission_rate, commission_amount, status, date_generated)
            VALUES (%s, %s, %s, %s, 'Pending', NOW())
        """, (order_id, order['seller_id'], commission_rate, seller_commission))
        
        # Insert admin commission for courier (if courier exists)
        # Note: Using seller_id field for courier_id as the table structure requires it
        if order['courier_id']:
            cursor.execute("""
                INSERT INTO admin_order_commission (order_id, seller_id, commission_rate, commission_amount, status, date_generated)
                VALUES (%s, %s, %s, %s, 'Pending', NOW())
            """, (order_id, order['courier_id'], commission_rate, courier_commission))
        
        # Insert admin sales record for seller
        cursor.execute("""
            INSERT INTO admin_sales (admin_id, user_id, user_type, order_id, total_sales, date_generated)
            VALUES (%s, %s, 'Seller', %s, %s, NOW())
        """, (admin_id, order['seller_id'], order_id, seller_commission))
        
        # Insert admin sales record for courier (if courier exists)
        if order['courier_id']:
            cursor.execute("""
                INSERT INTO admin_sales (admin_id, user_id, user_type, order_id, total_sales, date_generated)
                VALUES (%s, %s, 'Courier', %s, %s, NOW())
            """, (admin_id, order['courier_id'], order_id, courier_commission))
        
        # Insert seller sales record
        cursor.execute("""
            INSERT INTO seller_sales (seller_id, order_id, sale, date_created)
            VALUES (%s, %s, %s, NOW())
        """, (order['seller_id'], order_id, seller_net))
        
        # Insert courier sales record (if courier exists)
        if order['courier_id']:
            cursor.execute("""
                INSERT INTO courier_sales (courier_id, order_id, sale, date_created)
                VALUES (%s, %s, %s, NOW())
            """, (order['courier_id'], order_id, courier_net))
        
        # Insert order received record
        cursor.execute("""
            INSERT INTO order_received (order_id, buyer_id, date_received, status)
            VALUES (%s, %s, NOW(), 'Received')
        """, (order_id, order['buyer_id']))
        
        # Get buyer name for notifications
        cursor.execute("""
            SELECT pi.firstname, pi.lastname
            FROM user_account ua
            JOIN account_personal_info pi ON ua.personal_id = pi.personal_id
            WHERE ua.user_id = %s
        """, (order['buyer_id'],))
        
        buyer_info = cursor.fetchone()
        buyer_name = f"{buyer_info['firstname']} {buyer_info['lastname']}" if buyer_info else "Customer"
        
        # Get product name for notifications
        cursor.execute("""
            SELECT pi.product_name
            FROM product p
            JOIN product_info pi ON p.product_info_id = pi.product_info_id
            WHERE p.product_id = %s
        """, (order['product_id'],))
        
        product_info = cursor.fetchone()
        product_name = product_info['product_name'] if product_info else "Product"
        
        admin_id = 1
        
        # Create notification for admin about commission from seller
        admin_notification_content = f"You have received ₱{seller_commission:.2f} commission from Order #{order_id} ({product_name}) by {buyer_name}"
        cursor.execute("""
            INSERT INTO notifications (recipient_id, sender_id, notification_type, notification_title, content, status)
            VALUES (%s, %s, 'Commission Received', 'New Commission from Seller', %s, 'Unread')
        """, (admin_id, order['seller_id'], admin_notification_content))
        
        # Create notification for admin about commission from courier (if courier exists)
        if order['courier_id']:
            courier_notification_content = f"You have received ₱{courier_commission:.2f} commission from Order #{order_id} ({product_name}) delivery by {buyer_name}"
            cursor.execute("""
                INSERT INTO notifications (recipient_id, sender_id, notification_type, notification_title, content, status)
                VALUES (%s, %s, 'Commission Received', 'New Commission from Courier', %s, 'Unread')
            """, (admin_id, order['courier_id'], courier_notification_content))
        
        # Create notification for seller about their sales
        seller_notification_content = f"₱{seller_net:.2f} has been added to your sales from Order #{order_id} ({product_name}) by {buyer_name}. Commission: ₱{seller_commission:.2f}"
        cursor.execute("""
            INSERT INTO notifications (recipient_id, sender_id, notification_type, notification_title, content, status)
            VALUES (%s, %s, 'Sales Added', 'Payment Received & Sales Updated', %s, 'Unread')
        """, (order['seller_id'], admin_id, seller_notification_content))
        
        # Create notification for courier about their sales (if courier exists)
        if order['courier_id']:
            courier_sales_notification = f"₱{courier_net:.2f} has been added to your sales from Order #{order_id} ({product_name}) delivery by {buyer_name}. Commission: ₱{courier_commission:.2f}"
            cursor.execute("""
                INSERT INTO notifications (recipient_id, sender_id, notification_type, notification_title, content, status)
                VALUES (%s, %s, 'Sales Added', 'Delivery Payment Received & Sales Updated', %s, 'Unread')
            """, (order['courier_id'], admin_id, courier_sales_notification))
        
        return True
        
    except Exception as e:
        print(f"Error calculating sales: {e}")
        return False

def calculate_and_record_sales(order_id):
    """Calculate and record sales, commissions when order is received"""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        result = calculate_and_record_sales_with_cursor(cursor, order_id)
        if result:
            connection.commit()
        return result
        
    except Exception as e:
        connection.rollback()
        print(f"Error calculating sales: {e}")
        return False
    finally:
        cursor.close()
        connection.close()

@buyer_orders_bp.route('/buyer/orders')
def orders():
    if 'buyer' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Buyer':
        flash("Unauthorized access. Buyers only.", "danger")
        return redirect(url_for('login.login'))
    
    buyer_id = session['buyer']
    
    # Get filter parameters
    status_filter = request.args.get('status', 'Pending')
    sort_by = request.args.get('sort_by', 'date_ordered')
    order = request.args.get('order', 'desc')
    search_query = request.args.get('search', '')
    
    # Get orders and statistics
    orders = get_buyer_orders(buyer_id, status_filter, sort_by, order, search_query)
    stats = get_order_statistics(buyer_id)
    
    # Dynamic title and description based on status
    status_info = {
        'All': {'title': 'All Orders', 'description': 'View all your order history.'},
        'Pending': {'title': 'Pending Orders', 'description': 'Orders awaiting seller approval.'},
        'To Pack': {'title': 'To Pack', 'description': 'Orders being prepared and packed by sellers.'},
        'To Ship': {'title': 'To Ship', 'description': 'Orders in shipping process.'},
        'To Deliver': {'title': 'To Deliver', 'description': 'Orders out for delivery to you.'},
        'Completed': {'title': 'Completed Orders', 'description': 'Orders that have been received and completed.'}
    }
    
    current_status_info = status_info.get(status_filter, status_info['All'])
    
    return render_template('buyer_orders.html',
                         orders=orders,
                         stats=stats,
                         status_filter=status_filter,
                         sort_by=sort_by,
                         order=order,
                         search_query=search_query,
                         page_title=current_status_info['title'],
                         page_description=current_status_info['description'])

@buyer_orders_bp.route('/buyer/orders/submit_review/<int:order_id>', methods=['POST'])
def submit_review(order_id):
    if 'buyer' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Buyer':
        flash("Unauthorized access. Buyers only.", "danger")
        return redirect(url_for('login.login'))
    
    buyer_id = session['buyer']
    rating = request.form.get('rating')
    review_text = request.form.get('review_text', '').strip()
    
    if not rating:
        flash("Please provide a rating.", "danger")
        return redirect(url_for('buyer_orders.orders', status='Completed'))
    
    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            flash("Rating must be between 1 and 5 stars.", "danger")
            return redirect(url_for('buyer_orders.orders', status='To Review'))
    except ValueError:
        flash("Invalid rating value.", "danger")
        return redirect(url_for('buyer_orders.orders', status='To Review'))
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Verify order belongs to buyer and is received
        cursor.execute("""
            SELECT bo.*, pi.product_name, seller_pi.firstname, seller_pi.lastname
            FROM buyer_order bo
            JOIN product p ON bo.product_id = p.product_id
            JOIN product_info pi ON p.product_info_id = pi.product_info_id
            JOIN user_account seller_ua ON bo.seller_id = seller_ua.user_id
            JOIN account_personal_info seller_pi ON seller_ua.personal_id = seller_pi.personal_id
            WHERE bo.order_id = %s AND bo.buyer_id = %s AND bo.status = 'Received'
        """, (order_id, buyer_id))
        
        order = cursor.fetchone()
        if not order:
            flash("Order not found or cannot be reviewed.", "danger")
            return redirect(url_for('buyer_orders.orders'))
        
        # Check if this specific order has already been reviewed by checking if there's a review after this order was received
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM product_rating pr
            WHERE pr.product_id = %s 
            AND pr.sender_id = %s
            AND EXISTS (
                SELECT 1 FROM order_received ore 
                WHERE ore.order_id = %s 
                AND pr.date_rated >= ore.date_received
            )
        """, (order['product_id'], buyer_id, order_id))
        
        if cursor.fetchone()['count'] > 0:
            flash("You have already reviewed this order.", "warning")
            return redirect(url_for('buyer_orders.orders', status='Completed'))
        
        # Insert rating
        cursor.execute("""
            INSERT INTO product_rating (shop_id, product_id, sender_id, rate, date_rated)
            VALUES (%s, %s, %s, %s, NOW())
        """, (order['shop_id'], order['product_id'], buyer_id, rating))
        
        # Insert feedback if provided
        if review_text:
            cursor.execute("""
                INSERT INTO product_feedback (shop_id, product_id, sender_id, feedback, date_feedback)
                VALUES (%s, %s, %s, %s, NOW())
            """, (order['shop_id'], order['product_id'], buyer_id, review_text))
        
        # Create notification for seller
        admin_id = 1
        buyer_name = f"{session.get('firstname', '')} {session.get('lastname', '')}"
        stars = "★" * rating + "☆" * (5 - rating)
        notification_content = f"{buyer_name} left a {rating}-star review ({stars}) for Order #{order_id} ({order['product_name']})"
        if review_text:
            notification_content += f": \"{review_text[:100]}{'...' if len(review_text) > 100 else ''}\""
        
        cursor.execute("""
            INSERT INTO notifications (recipient_id, sender_id, notification_type, notification_title, content, status)
            VALUES (%s, %s, 'New Review', 'Customer Review Received', %s, 'Unread')
        """, (order['seller_id'], admin_id, notification_content))
        
        connection.commit()
        flash("Thank you for your review!", "success")
        
    except Exception as e:
        connection.rollback()
        flash("Error submitting review. Please try again.", "danger")
        print(f"Submit review error: {e}")
    finally:
        cursor.close()
        connection.close()
    
    return redirect(url_for('buyer_orders.orders', status='Completed'))

@buyer_orders_bp.route('/buyer/orders/mark_received/<int:order_id>', methods=['POST'])
def mark_received(order_id):
    if 'buyer' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Buyer':
        flash("Unauthorized access. Buyers only.", "danger")
        return redirect(url_for('login.login'))
    
    buyer_id = session['buyer']
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Verify order belongs to buyer and is delivered
        cursor.execute("""
            SELECT bo.*, pi.product_name, seller_pi.firstname, seller_pi.lastname
            FROM buyer_order bo
            JOIN product p ON bo.product_id = p.product_id
            JOIN product_info pi ON p.product_info_id = pi.product_info_id
            JOIN user_account seller_ua ON bo.seller_id = seller_ua.user_id
            JOIN account_personal_info seller_pi ON seller_ua.personal_id = seller_pi.personal_id
            WHERE bo.order_id = %s AND bo.buyer_id = %s AND bo.status = 'Delivered'
        """, (order_id, buyer_id))
        
        order = cursor.fetchone()
        if not order:
            flash("Order not found or cannot be marked as received.", "danger")
            return redirect(url_for('buyer_orders.orders'))
        
        # Update order status to Received
        cursor.execute("""
            UPDATE buyer_order 
            SET status = 'Received', payment_status = 'Paid'
            WHERE order_id = %s
        """, (order_id,))
        
        # Calculate and record sales/commissions
        calculate_and_record_sales_with_cursor(cursor, order_id)
        
        # Create notification for seller
        admin_id = 1
        
        # Get buyer name from database instead of session
        cursor.execute("""
            SELECT pi.firstname, pi.lastname
            FROM user_account ua
            JOIN account_personal_info pi ON ua.personal_id = pi.personal_id
            WHERE ua.user_id = %s
        """, (buyer_id,))
        
        buyer_info = cursor.fetchone()
        buyer_name = f"{buyer_info['firstname']} {buyer_info['lastname']}" if buyer_info else "Customer"
        
        notification_content = f"{buyer_name} has received Order #{order_id} ({order['product_name']}). Payment has been confirmed and the order is now complete."
        
        cursor.execute("""
            INSERT INTO notifications (recipient_id, sender_id, notification_type, notification_title, content, status)
            VALUES (%s, %s, 'Order Received', 'Order Received & Payment Confirmed', %s, 'Unread')
        """, (order['seller_id'], admin_id, notification_content))
        
        connection.commit()
        flash("Order marked as received successfully! Payment has been confirmed.", "success")
        
    except Exception as e:
        connection.rollback()
        flash("Error marking order as received. Please try again.", "danger")
        print(f"Mark received error: {e}")
    finally:
        cursor.close()
        connection.close()
    
    return redirect(url_for('buyer_orders.orders', status='Completed'))

# Routes to serve product images
@buyer_orders_bp.route('/uploads/product_main_pics/<filename>')
def serve_product_main_pic(filename):
    return send_from_directory(PRODUCT_MAIN_PIC_FOLDER, filename)

@buyer_orders_bp.route('/uploads/product_images/<filename>')
def serve_product_image(filename):
    return send_from_directory(PRODUCT_IMAGES_FOLDER, filename)

@buyer_orders_bp.route('/uploads/product_variant_images/<filename>')
def serve_product_variant_image(filename):
    return send_from_directory(PRODUCT_VARIANT_IMAGES_FOLDER, filename)
