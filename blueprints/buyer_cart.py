from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from db_connection import get_db_connection
from datetime import datetime

buyer_cart_bp = Blueprint('buyer_cart', __name__)

def get_cart_items(buyer_id):
    """Get all cart items for a buyer grouped by shop"""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
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
    """, (buyer_id,))
    
    cart_items = cursor.fetchall()
    
    # Group items by shop
    shops = {}
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
        item_total = item['price'] * item['quantity']
        item['item_total'] = item_total
        
        shops[shop_id]['items'].append(item)
        shops[shop_id]['subtotal'] += item_total
        
        # Use the shipping fee from the first item (since all items in same product_info have same shipping fee)
        if shops[shop_id]['shipping_fee'] == 0:
            shops[shop_id]['shipping_fee'] = item['shipping_fee']
    
    cursor.close()
    connection.close()
    
    return list(shops.values())

def get_buyer_address(buyer_id):
    """Get buyer's address information"""
    connection = get_db_connection()
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
    """, (buyer_id,))
    
    buyer_info = cursor.fetchone()
    cursor.close()
    connection.close()
    
    return buyer_info

@buyer_cart_bp.route('/buyer/cart')
def view_cart():
    """Display buyer's cart"""
    if 'buyer' not in session:
        flash("Please log in to view your cart.", "danger")
        return redirect(url_for('login.login'))
    
    buyer_id = session['buyer']
    shops = get_cart_items(buyer_id)
    buyer_address = get_buyer_address(buyer_id)
    
    # Calculate totals
    total_items = sum(len(shop['items']) for shop in shops) if shops else 0
    subtotal = sum(shop['subtotal'] for shop in shops) if shops else 0
    total_shipping = sum(shop['shipping_fee'] for shop in shops) if shops else 0
    grand_total = subtotal + total_shipping
    
    return render_template('buyer_cart.html', 
                         shops=shops,
                         total_items=total_items,
                         subtotal=subtotal,
                         total_shipping=total_shipping,
                         grand_total=grand_total,
                         buyer_address=buyer_address)

@buyer_cart_bp.route('/buyer/cart/update_quantity', methods=['POST'])
def update_quantity():
    """Update quantity of cart item"""
    if 'buyer' not in session:
        flash("Please log in to update cart.", "danger")
        return redirect(url_for('login.login'))
    
    cart_id = request.form.get('cart_id')
    new_quantity = request.form.get('quantity')
    
    if not cart_id or not new_quantity:
        flash("Invalid data provided.", "danger")
        return redirect(url_for('buyer_cart.view_cart'))
    
    try:
        new_quantity = int(new_quantity)
        if new_quantity <= 0:
            flash("Quantity must be greater than 0.", "danger")
            return redirect(url_for('buyer_cart.view_cart'))
    except ValueError:
        flash("Invalid quantity format.", "danger")
        return redirect(url_for('buyer_cart.view_cart'))
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Get cart item and product details
        cursor.execute("""
            SELECT bc.*, p.price, p.stock, p.stock_status, pi.product_name
            FROM buyer_cart bc
            JOIN product p ON bc.product_id = p.product_id
            JOIN product_info pi ON p.product_info_id = pi.product_info_id
            WHERE bc.cart_id = %s AND bc.buyer_id = %s
        """, (cart_id, session['buyer']))
        
        cart_item = cursor.fetchone()
        
        if not cart_item:
            flash("Cart item not found.", "danger")
            return redirect(url_for('buyer_cart.view_cart'))
        
        # Check stock availability
        if new_quantity > cart_item['stock']:
            flash(f"Only {cart_item['stock']} items available for {cart_item['product_name']}.", "warning")
            return redirect(url_for('buyer_cart.view_cart'))
        
        if cart_item['stock_status'] == 'Out of Stock':
            flash(f"{cart_item['product_name']} is out of stock.", "danger")
            return redirect(url_for('buyer_cart.view_cart'))
        
        # Update cart item
        new_total = cart_item['price'] * new_quantity
        cursor.execute("""
            UPDATE buyer_cart
            SET quantity = %s, total_amount = %s
            WHERE cart_id = %s
        """, (new_quantity, new_total, cart_id))
        
        connection.commit()
        flash("Cart updated successfully!", "success")
        
    except Exception as e:
        connection.rollback()
        flash("Error updating cart. Please try again.", "danger")
    finally:
        cursor.close()
        connection.close()
    
    return redirect(url_for('buyer_cart.view_cart'))

@buyer_cart_bp.route('/buyer/cart/remove_item', methods=['POST'])
def remove_item():
    """Remove item from cart"""
    if 'buyer' not in session:
        flash("Please log in to remove items.", "danger")
        return redirect(url_for('login.login'))
    
    cart_id = request.form.get('cart_id')
    
    if not cart_id:
        flash("Invalid cart item.", "danger")
        return redirect(url_for('buyer_cart.view_cart'))
    
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute("""
            DELETE FROM buyer_cart
            WHERE cart_id = %s AND buyer_id = %s
        """, (cart_id, session['buyer']))
        
        connection.commit()
        
        if cursor.rowcount > 0:
            flash("Item removed from cart successfully!", "success")
        else:
            flash("Item not found in cart.", "warning")
            
    except Exception as e:
        connection.rollback()
        flash("Error removing item from cart.", "danger")
    finally:
        cursor.close()
        connection.close()
    
    return redirect(url_for('buyer_cart.view_cart'))

@buyer_cart_bp.route('/buyer/cart/checkout', methods=['POST'])
def checkout():
    """Process checkout for all items in cart"""
    if 'buyer' not in session:
        flash("Please log in to checkout.", "danger")
        return redirect(url_for('login.login'))
    
    buyer_id = session['buyer']
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
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
        """, (buyer_id,))
        
        cart_items = cursor.fetchall()
        
        if not cart_items:
            flash("Your cart is empty.", "warning")
            return redirect(url_for('buyer_cart.view_cart'))
        
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
            for error in validation_errors:
                flash(error, "danger")
            return redirect(url_for('buyer_cart.view_cart'))
        
        # Create orders for each item
        order_count = 0
        
        for item in valid_items:
            # Calculate final amount: item total + shipping fee
            final_amount = item['total_amount'] + item['shipping_fee']
            
            cursor.execute("""
                INSERT INTO buyer_order (
                    shop_id, seller_id, product_id, buyer_id, quantity, 
                    total_amount, payment_method, payment_status, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                item['shop_id'],
                item['seller_id'],
                item['product_id'],
                buyer_id,
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
        """, (buyer_id,))
        buyer_info = cursor.fetchone()
        buyer_name = f"{buyer_info['firstname']} {buyer_info['lastname']}"
        
        # Create notifications
        admin_id = 1
        
        # Notification for buyer
        cursor.execute("""
            INSERT INTO notifications (recipient_id, sender_id, notification_type, notification_title, content, status)
            VALUES (%s, %s, 'Order Confirmation', 'Order Placed Successfully', 
                    'Your order has been placed successfully. Orders will be processed soon.', 'Unread')
        """, (buyer_id, admin_id))
        
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
        
        flash(f"Order placed successfully! {order_count} items ordered.", "success")
        
    except Exception as e:
        connection.rollback()
        flash("Checkout failed. Please try again.", "danger")
        print(f"Checkout error: {e}")
    finally:
        cursor.close()
        connection.close()
    
    return redirect(url_for('buyer_cart.view_cart'))

@buyer_cart_bp.route('/buyer/cart/clear')
def clear_cart():
    """Clear all items from cart"""
    if 'buyer' not in session:
        flash("Please log in to clear cart.", "danger")
        return redirect(url_for('login.login'))
    
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute("""
            DELETE FROM buyer_cart
            WHERE buyer_id = %s AND status = 'On cart'
        """, (session['buyer'],))
        
        connection.commit()
        flash("Cart cleared successfully!", "success")
        
    except Exception as e:
        connection.rollback()
        flash("Error clearing cart.", "danger")
    finally:
        cursor.close()
        connection.close()
    
    return redirect(url_for('buyer_cart.view_cart'))


