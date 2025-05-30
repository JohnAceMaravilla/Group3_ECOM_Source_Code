from flask import Blueprint, jsonify, request
from flask_cors import CORS
from db_connection import get_db_connection
import base64
import os
from datetime import datetime

buyer_cart_api_bp = Blueprint('buyer_cart_api', __name__, url_prefix='/api/mobile/buyer/cart')

# Enable CORS for mobile app communication
CORS(buyer_cart_api_bp)

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

@buyer_cart_api_bp.route('', methods=['GET'])
def get_cart_items():
    """Get all cart items for a buyer grouped by shop"""
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

        # Get cart items with shop and product details
        cursor.execute("""
            SELECT 
                bc.cart_id,
                bc.product_id,
                bc.quantity,
                bc.total_amount,
                bc.date_added,
                p.variant,
                p.color,
                p.price,
                p.shipping_fee,
                p.stock,
                p.stock_status,
                pi.product_info_id,
                pi.product_name,
                pi.product_main_pic,
                pi.product_category,
                s.shop_id,
                si.shop_name,
                sl.seller_id
            FROM buyer_cart bc
            JOIN product p ON bc.product_id = p.product_id
            JOIN product_info pi ON p.product_info_id = pi.product_info_id
            JOIN shop_listing sl ON p.product_id = sl.product_id
            JOIN shop s ON sl.shop_id = s.shop_id
            JOIN shop_info si ON s.shop_info_id = si.shop_info_id
            WHERE bc.buyer_id = %s AND bc.status = 'On cart'
            ORDER BY si.shop_name, bc.date_added DESC
        """, (user_id,))
        
        cart_items = cursor.fetchall()

        # Group items by shop
        shops = {}
        total_items = 0
        subtotal = 0
        total_shipping = 0

        for item in cart_items:
            shop_id = item['shop_id']
            if shop_id not in shops:
                shops[shop_id] = {
                    'shop_id': shop_id,
                    'shop_name': item['shop_name'],
                    'seller_id': item['seller_id'],
                    'items': [],
                    'subtotal': 0,
                    'shipping_fee': 0
                }
            
            # Calculate item total (price * quantity)
            item_total = float(item['price']) * item['quantity']
            
            # Process item data
            processed_item = {
                'cart_id': item['cart_id'],
                'product_id': item['product_id'],
                'product_info_id': item['product_info_id'],
                'product_name': item['product_name'],
                'variant': item['variant'],
                'color': item['color'],
                'quantity': item['quantity'],
                'price': float(item['price']),
                'shipping_fee': float(item['shipping_fee']),
                'stock': item['stock'],
                'stock_status': item['stock_status'],
                'item_total': item_total,
                'date_added': item['date_added'].isoformat() if item['date_added'] else None,
                'image_base64': get_product_image_base64(item['product_main_pic'])
            }
            
            shops[shop_id]['items'].append(processed_item)
            shops[shop_id]['subtotal'] += item_total
            
            # Use the shipping fee from the first item (since all items in same shop share shipping)
            if shops[shop_id]['shipping_fee'] == 0:
                shops[shop_id]['shipping_fee'] = float(item['shipping_fee'])
            
            total_items += 1
            subtotal += item_total

        # Calculate total shipping (one shipping fee per shop)
        for shop in shops.values():
            total_shipping += shop['shipping_fee']

        grand_total = subtotal + total_shipping

        cursor.close()
        connection.close()

        return jsonify({
            'status': 'success',
            'data': {
                'shops': list(shops.values()),
                'summary': {
                    'total_items': total_items,
                    'subtotal': subtotal,
                    'total_shipping': total_shipping,
                    'grand_total': grand_total
                }
            }
        }), 200

    except Exception as e:
        print(f"Get cart items error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load cart items'
        }), 500

@buyer_cart_api_bp.route('/update-quantity', methods=['POST'])
def update_quantity():
    """Update quantity of cart item"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        cart_id = data.get('cart_id')
        new_quantity = data.get('quantity')
        
        if not all([user_id, cart_id, new_quantity]) or new_quantity <= 0:
            return jsonify({
                'status': 'error',
                'message': 'Invalid data provided. Quantity must be greater than 0.'
            }), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({
                'status': 'error',
                'message': 'Database connection error'
            }), 500

        cursor = connection.cursor(dictionary=True)

        # Get cart item and product details
        cursor.execute("""
            SELECT bc.*, p.price, p.stock, p.stock_status, pi.product_name
            FROM buyer_cart bc
            JOIN product p ON bc.product_id = p.product_id
            JOIN product_info pi ON p.product_info_id = pi.product_info_id
            WHERE bc.cart_id = %s AND bc.buyer_id = %s AND bc.status = 'On cart'
        """, (cart_id, user_id))
        
        cart_item = cursor.fetchone()
        
        if not cart_item:
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'error',
                'message': 'Cart item not found'
            }), 404
        
        # Check stock availability
        if new_quantity > cart_item['stock']:
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'error',
                'message': f'Only {cart_item["stock"]} items available for {cart_item["product_name"]}'
            }), 400
        
        if cart_item['stock_status'] == 'Out of Stock':
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'error',
                'message': f'{cart_item["product_name"]} is out of stock'
            }), 400
        
        # Update cart item
        new_total = float(cart_item['price']) * new_quantity
        cursor.execute("""
            UPDATE buyer_cart
            SET quantity = %s, total_amount = %s
            WHERE cart_id = %s
        """, (new_quantity, new_total, cart_id))
        
        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({
            'status': 'success',
            'message': 'Cart updated successfully'
        }), 200

    except Exception as e:
        print(f"Update quantity error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to update cart'
        }), 500

@buyer_cart_api_bp.route('/remove-item', methods=['DELETE'])
def remove_item():
    """Remove item from cart"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        cart_id = data.get('cart_id')
        
        if not all([user_id, cart_id]):
            return jsonify({
                'status': 'error',
                'message': 'User ID and cart ID required'
            }), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({
                'status': 'error',
                'message': 'Database connection error'
            }), 500

        cursor = connection.cursor()

        cursor.execute("""
            DELETE FROM buyer_cart
            WHERE cart_id = %s AND buyer_id = %s AND status = 'On cart'
        """, (cart_id, user_id))
        
        connection.commit()
        
        if cursor.rowcount > 0:
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'success',
                'message': 'Item removed from cart successfully'
            }), 200
        else:
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'error',
                'message': 'Item not found in cart'
            }), 404

    except Exception as e:
        print(f"Remove item error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to remove item from cart'
        }), 500

@buyer_cart_api_bp.route('/clear', methods=['DELETE'])
def clear_cart():
    """Clear all items from cart"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
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

        cursor = connection.cursor()

        cursor.execute("""
            DELETE FROM buyer_cart
            WHERE buyer_id = %s AND status = 'On cart'
        """, (user_id,))
        
        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({
            'status': 'success',
            'message': 'Cart cleared successfully'
        }), 200

    except Exception as e:
        print(f"Clear cart error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to clear cart'
        }), 500

@buyer_cart_api_bp.route('/buyer-address', methods=['GET'])
def get_buyer_address():
    """Get buyer's address information"""
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
                pi.firstname, pi.lastname,
                ai.house_no, ai.street, ai.barangay, ai.city, ai.province, ai.region,
                ci.phone
            FROM user_account ua
            JOIN account_personal_info pi ON ua.personal_id = pi.personal_id
            JOIN account_address_info ai ON ua.address_id = ai.address_id
            JOIN account_contact_info ci ON ua.contact_id = ci.contact_id
            WHERE ua.user_id = %s AND ua.user_role = 'Buyer'
        """, (user_id,))
        
        buyer_info = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if not buyer_info:
            return jsonify({
                'status': 'error',
                'message': 'Buyer address not found'
            }), 404

        return jsonify({
            'status': 'success',
            'data': buyer_info
        }), 200

    except Exception as e:
        print(f"Get buyer address error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load buyer address'
        }), 500

@buyer_cart_api_bp.route('/checkout', methods=['POST'])
def checkout():
    """Process checkout for all items in cart"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
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

        # Get all cart items for this buyer
        cursor.execute("""
            SELECT 
                bc.*,
                p.stock,
                p.stock_status,
                p.price,
                p.shipping_fee,
                pi.product_name,
                sl.shop_id,
                sl.seller_id
            FROM buyer_cart bc
            JOIN product p ON bc.product_id = p.product_id
            JOIN product_info pi ON p.product_info_id = pi.product_info_id
            JOIN shop_listing sl ON p.product_id = sl.product_id
            WHERE bc.buyer_id = %s AND bc.status = 'On cart'
        """, (user_id,))
        
        cart_items = cursor.fetchall()
        
        if not cart_items:
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'error',
                'message': 'Your cart is empty'
            }), 400
        
        # Validate all items and check stock
        validation_errors = []
        valid_items = []
        
        for item in cart_items:
            if item['stock'] < item['quantity']:
                validation_errors.append(f"{item['product_name']}: Only {item['stock']} items available")
                continue
            
            if item['stock_status'] == 'Out of Stock':
                validation_errors.append(f"{item['product_name']}: Out of stock")
                continue
            
            valid_items.append(item)
        
        if validation_errors:
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'error',
                'message': 'Some items in your cart are unavailable',
                'errors': validation_errors
            }), 400
        
        # Create orders for each item
        order_count = 0
        
        for item in valid_items:
            # Calculate final amount: item total + shipping fee
            final_amount = float(item['total_amount']) + float(item['shipping_fee'])
            
            cursor.execute("""
                INSERT INTO buyer_order (
                    shop_id, seller_id, product_id, buyer_id, quantity, 
                    total_amount, payment_method, payment_status, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                item['shop_id'],
                item['seller_id'],
                item['product_id'],
                user_id,
                item['quantity'],
                final_amount,
                'Cash on Delivery',
                'Unpaid',
                'Pending'
            ))
            
            order_count += 1
            
            # Update product stock
            cursor.execute("""
                UPDATE product
                SET stock = stock - %s,
                    stock_status = CASE
                        WHEN stock - %s <= 0 THEN 'Out of Stock'
                        WHEN stock - %s <= 10 THEN 'Nearly Out of Stock'
                        ELSE 'Active'
                    END
                WHERE product_id = %s
            """, (item['quantity'], item['quantity'], item['quantity'], item['product_id']))
            
            # Remove item from cart
            cursor.execute("""
                UPDATE buyer_cart
                SET status = 'Checked Out'
                WHERE cart_id = %s
            """, (item['cart_id'],))
        
        # Get buyer information for notifications
        cursor.execute("""
            SELECT pi.firstname, pi.lastname
            FROM user_account ua
            JOIN account_personal_info pi ON ua.personal_id = pi.personal_id
            WHERE ua.user_id = %s
        """, (user_id,))
        buyer_info = cursor.fetchone()
        buyer_name = f"{buyer_info['firstname']} {buyer_info['lastname']}"
        
        # Create notifications
        admin_id = 1
        
        # Notification for buyer
        cursor.execute("""
            INSERT INTO notifications (recipient_id, sender_id, notification_type, notification_title, content, status)
            VALUES (%s, %s, 'Order Confirmation', 'Order Placed Successfully', 
                    'Your order has been placed successfully. Orders will be processed soon.', 'Unread')
        """, (user_id, admin_id))
        
        # Notifications for sellers (get unique sellers and their ordered items)
        seller_orders = {}
        for item in valid_items:
            seller_id = item['seller_id']
            if seller_id not in seller_orders:
                seller_orders[seller_id] = []
            seller_orders[seller_id].append(item['product_name'])
        
        for seller_id, product_names in seller_orders.items():
            products_text = ", ".join(product_names[:3])  # Show first 3 products
            if len(product_names) > 3:
                products_text += f" and {len(product_names) - 3} more items"
            
            notification_content = f"{buyer_name} has placed an order for: {products_text}. Please check your orders section to process the order."
            
            cursor.execute("""
                INSERT INTO notifications (recipient_id, sender_id, notification_type, notification_title, content, status)
                VALUES (%s, %s, 'New Order', %s, %s, 'Unread')
            """, (seller_id, admin_id, f'New Order Received - {buyer_name}', notification_content))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({
            'status': 'success',
            'message': f'Order placed successfully! {order_count} items ordered.',
            'order_count': order_count
        }), 200

    except Exception as e:
        print(f"Checkout error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Checkout failed. Please try again.'
        }), 500
