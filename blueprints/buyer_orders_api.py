from flask import Blueprint, jsonify, request
from flask_cors import CORS
from db_connection import get_db_connection
import base64
import os
from datetime import datetime

buyer_orders_api_bp = Blueprint('buyer_orders_api', __name__, url_prefix='/api/mobile/buyer/orders')

# Enable CORS for mobile app communication
CORS(buyer_orders_api_bp)

def get_product_image_base64(image_filename):
    """Get product image as base64 string"""
    if not image_filename:
        return None
    
    try:
        image_path = os.path.join("static", "uploads", "seller", "product_main_pics", image_filename)
        if os.path.exists(image_path):
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                return f"data:image/jpeg;base64,{encoded_string}"
    except Exception as e:
        print(f"Error loading product image {image_filename}: {e}")
    
    return None

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
        
        return True
        
    except Exception as e:
        print(f"Error calculating sales: {e}")
        return False

@buyer_orders_api_bp.route('', methods=['GET'])
def get_orders():
    """Get orders for buyer with filtering and sorting"""
    try:
        user_id = request.args.get('user_id', type=int)
        status_filter = request.args.get('status', default='All', type=str)
        sort_by = request.args.get('sort_by', default='date_ordered', type=str)
        order = request.args.get('order', default='desc', type=str)
        
        if not user_id:
            return jsonify({
                'status': 'error',
                'message': 'User ID required'
            }), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({
                'status': 'error',
                'message': 'Database connection error'
            }), 500

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
                pi.product_info_id,
                pi.product_name,
                pi.product_main_pic,
                pi.product_category,
                si.shop_name,
                seller_pi.firstname as seller_firstname,
                seller_pi.lastname as seller_lastname,
                seller_ci.email as seller_email,
                seller_ci.phone as seller_phone,
                -- Check if review exists for this specific order by checking if there's a review for this product after this order was received
                -- We'll use the logic: if order is received AND there's a review for this product from this user after the order date, then it's reviewed
                (SELECT COUNT(*) 
                 FROM product_rating pr 
                 WHERE pr.product_id = bo.product_id 
                 AND pr.sender_id = bo.buyer_id 
                 AND EXISTS (
                     SELECT 1 FROM order_received ore 
                     WHERE ore.order_id = bo.order_id 
                     AND pr.date_rated >= ore.date_received
                 )) as has_review,
                -- Get rating information (most recent for this product from this user)
                (SELECT pr.rate FROM product_rating pr WHERE pr.product_id = bo.product_id AND pr.sender_id = bo.buyer_id ORDER BY pr.date_rated DESC LIMIT 1) as user_rating,
                (SELECT pr.date_rated FROM product_rating pr WHERE pr.product_id = bo.product_id AND pr.sender_id = bo.buyer_id ORDER BY pr.date_rated DESC LIMIT 1) as rating_date,
                -- Get feedback information (most recent for this product from this user)
                (SELECT pf.feedback FROM product_feedback pf WHERE pf.product_id = bo.product_id AND pf.sender_id = bo.buyer_id ORDER BY pf.date_feedback DESC LIMIT 1) as user_feedback,
                (SELECT pf.date_feedback FROM product_feedback pf WHERE pf.product_id = bo.product_id AND pf.sender_id = bo.buyer_id ORDER BY pf.date_feedback DESC LIMIT 1) as feedback_date
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
        
        params = [user_id]
        
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

        # Process orders and add base64 images
        processed_orders = []
        for order in orders:
            processed_order = {
                'order_id': order['order_id'],
                'product_info_id': order['product_info_id'],
                'product_name': order['product_name'],
                'product_category': order['product_category'],
                'variant': order['variant'],
                'color': order['color'],
                'quantity': order['quantity'],
                'price': float(order['price']),
                'shipping_fee': float(order['shipping_fee']),
                'total_amount': float(order['total_amount']),
                'payment_method': order['payment_method'],
                'payment_status': order['payment_status'],
                'status': order['status'],
                'date_ordered': order['date_ordered'].isoformat() if order['date_ordered'] else None,
                'shop_name': order['shop_name'],
                'seller_firstname': order['seller_firstname'],
                'seller_lastname': order['seller_lastname'],
                'seller_email': order['seller_email'],
                'seller_phone': order['seller_phone'],
                'has_review': order['has_review'] > 0,
                'user_rating': order['user_rating'],
                'rating_date': order['rating_date'].isoformat() if order['rating_date'] else None,
                'user_feedback': order['user_feedback'],
                'feedback_date': order['feedback_date'].isoformat() if order['feedback_date'] else None,
                'image_base64': get_product_image_base64(order['product_main_pic'])
            }
            processed_orders.append(processed_order)

        cursor.close()
        connection.close()

        return jsonify({
            'status': 'success',
            'data': processed_orders,
            'count': len(processed_orders)
        }), 200

    except Exception as e:
        print(f"Get orders error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load orders'
        }), 500

@buyer_orders_api_bp.route('/statistics', methods=['GET'])
def get_order_statistics():
    """Get order statistics for the buyer"""
    try:
        user_id = request.args.get('user_id', type=int)
        
        if not user_id:
            return jsonify({
                'status': 'error',
                'message': 'User ID required'
            }), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({
                'status': 'error',
                'message': 'Database connection error'
            }), 500

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
        """, (user_id,))
        
        stats = cursor.fetchone()
        cursor.close()
        connection.close()

        return jsonify({
            'status': 'success',
            'data': {
                'pending_orders': stats['pending_orders'] or 0,
                'to_pack_orders': stats['to_pack_orders'] or 0,
                'to_ship_orders': stats['to_ship_orders'] or 0,
                'to_deliver_orders': stats['to_deliver_orders'] or 0,
                'completed_orders': stats['completed_orders'] or 0,
                'total_orders': stats['total_orders'] or 0
            }
        }), 200

    except Exception as e:
        print(f"Get order statistics error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load order statistics'
        }), 500

@buyer_orders_api_bp.route('/submit-review', methods=['POST'])
def submit_review():
    """Submit a review for an order"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        order_id = data.get('order_id')
        rating = data.get('rating')
        review_text = data.get('review_text', '').strip()
        
        if not all([user_id, order_id, rating]):
            return jsonify({
                'status': 'error',
                'message': 'User ID, order ID, and rating are required'
            }), 400

        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                return jsonify({
                    'status': 'error',
                    'message': 'Rating must be between 1 and 5 stars'
                }), 400
        except ValueError:
            return jsonify({
                'status': 'error',
                'message': 'Invalid rating value'
            }), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({
                'status': 'error',
                'message': 'Database connection error'
            }), 500

        cursor = connection.cursor(dictionary=True)

        # Verify order belongs to buyer and is received
        cursor.execute("""
            SELECT bo.*, pi.product_name, seller_pi.firstname, seller_pi.lastname
            FROM buyer_order bo
            JOIN product p ON bo.product_id = p.product_id
            JOIN product_info pi ON p.product_info_id = pi.product_info_id
            JOIN user_account seller_ua ON bo.seller_id = seller_ua.user_id
            JOIN account_personal_info seller_pi ON seller_ua.personal_id = seller_pi.personal_id
            WHERE bo.order_id = %s AND bo.buyer_id = %s AND bo.status = 'Received'
        """, (order_id, user_id))
        
        order = cursor.fetchone()
        if not order:
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'error',
                'message': 'Order not found or cannot be reviewed'
            }), 404
        
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
        """, (order['product_id'], user_id, order_id))
        
        if cursor.fetchone()['count'] > 0:
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'error',
                'message': 'You have already reviewed this order'
            }), 400
        
        # Insert rating
        cursor.execute("""
            INSERT INTO product_rating (shop_id, product_id, sender_id, rate, date_rated)
            VALUES (%s, %s, %s, %s, NOW())
        """, (order['shop_id'], order['product_id'], user_id, rating))
        
        # Insert feedback if provided
        if review_text:
            cursor.execute("""
                INSERT INTO product_feedback (shop_id, product_id, sender_id, feedback, date_feedback)
                VALUES (%s, %s, %s, %s, NOW())
            """, (order['shop_id'], order['product_id'], user_id, review_text))
        
        # Get buyer name for notification
        cursor.execute("""
            SELECT pi.firstname, pi.lastname
            FROM user_account ua
            JOIN account_personal_info pi ON ua.personal_id = pi.personal_id
            WHERE ua.user_id = %s
        """, (user_id,))
        
        buyer_info = cursor.fetchone()
        buyer_name = f"{buyer_info['firstname']} {buyer_info['lastname']}" if buyer_info else "Customer"
        
        # Create notification for seller
        admin_id = 1
        stars = "★" * rating + "☆" * (5 - rating)
        notification_content = f"{buyer_name} left a {rating}-star review ({stars}) for Order #{order_id} ({order['product_name']})"
        if review_text:
            notification_content += f": \"{review_text[:100]}{'...' if len(review_text) > 100 else ''}\""
        
        cursor.execute("""
            INSERT INTO notifications (recipient_id, sender_id, notification_type, notification_title, content, status)
            VALUES (%s, %s, 'New Review', 'Customer Review Received', %s, 'Unread')
        """, (order['seller_id'], admin_id, notification_content))
        
        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({
            'status': 'success',
            'message': 'Thank you for your review!'
        }), 200

    except Exception as e:
        print(f"Submit review error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to submit review'
        }), 500

@buyer_orders_api_bp.route('/mark-received', methods=['POST'])
def mark_received():
    """Mark order as received"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        order_id = data.get('order_id')
        
        if not all([user_id, order_id]):
            return jsonify({
                'status': 'error',
                'message': 'User ID and order ID are required'
            }), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({
                'status': 'error',
                'message': 'Database connection error'
            }), 500

        cursor = connection.cursor(dictionary=True)

        # Verify order belongs to buyer and is delivered
        cursor.execute("""
            SELECT bo.*, pi.product_name, seller_pi.firstname, seller_pi.lastname
            FROM buyer_order bo
            JOIN product p ON bo.product_id = p.product_id
            JOIN product_info pi ON p.product_info_id = pi.product_info_id
            JOIN user_account seller_ua ON bo.seller_id = seller_ua.user_id
            JOIN account_personal_info seller_pi ON seller_ua.personal_id = seller_pi.personal_id
            WHERE bo.order_id = %s AND bo.buyer_id = %s AND bo.status = 'Delivered'
        """, (order_id, user_id))
        
        order = cursor.fetchone()
        if not order:
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'error',
                'message': 'Order not found or cannot be marked as received'
            }), 404
        
        # Update order status to Received
        cursor.execute("""
            UPDATE buyer_order 
            SET status = 'Received', payment_status = 'Paid'
            WHERE order_id = %s
        """, (order_id,))
        
        # Calculate and record sales/commissions
        calculate_and_record_sales_with_cursor(cursor, order_id)
        
        # Get buyer name for notification
        cursor.execute("""
            SELECT pi.firstname, pi.lastname
            FROM user_account ua
            JOIN account_personal_info pi ON ua.personal_id = pi.personal_id
            WHERE ua.user_id = %s
        """, (user_id,))
        
        buyer_info = cursor.fetchone()
        buyer_name = f"{buyer_info['firstname']} {buyer_info['lastname']}" if buyer_info else "Customer"
        
        # Create notification for seller
        admin_id = 1
        notification_content = f"{buyer_name} has received Order #{order_id} ({order['product_name']}). Payment has been confirmed and the order is now complete."
        
        cursor.execute("""
            INSERT INTO notifications (recipient_id, sender_id, notification_type, notification_title, content, status)
            VALUES (%s, %s, 'Order Received', 'Order Received & Payment Confirmed', %s, 'Unread')
        """, (order['seller_id'], admin_id, notification_content))
        
        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({
            'status': 'success',
            'message': 'Order marked as received successfully! Payment has been confirmed.'
        }), 200

    except Exception as e:
        print(f"Mark received error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to mark order as received'
        }), 500
