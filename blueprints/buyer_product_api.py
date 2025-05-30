from flask import Blueprint, jsonify, request
from flask_cors import CORS
from db_connection import get_db_connection
import base64
import os

buyer_product_api_bp = Blueprint('buyer_product_api', __name__, url_prefix='/api/mobile/buyer/product')

# Enable CORS for mobile app communication
CORS(buyer_product_api_bp)

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

def get_additional_image_base64(image_filename):
    """Get additional product image as base64 string"""
    if not image_filename:
        return None
    
    try:
        image_path = os.path.join("static", "uploads", "seller", "product_images", image_filename)
        if os.path.exists(image_path):
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                return f"data:image/jpeg;base64,{encoded_string}"
    except Exception as e:
        print(f"Error loading additional image {image_filename}: {e}")
    
    return None

def get_shop_image_base64(image_filename):
    """Get shop image as base64 string"""
    if not image_filename:
        return None
    
    try:
        image_path = os.path.join("static", "uploads", "seller", "shop_profile", image_filename)
        if os.path.exists(image_path):
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                return f"data:image/jpeg;base64,{encoded_string}"
    except Exception as e:
        print(f"Error loading shop image {image_filename}: {e}")
    
    return None

def is_liked_by_user(product_info_id, user_id):
    """Check if product is liked by user"""
    if not user_id:
        return False
        
    connection = get_db_connection()
    if not connection:
        return False
    
    cursor = connection.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT * FROM buyer_like
            WHERE product_info_id = %s AND buyer_id = %s AND status = 'Liked'
        """, (product_info_id, user_id))
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        return result is not None
    except Exception as e:
        print(f"Error checking like status: {e}")
        cursor.close()
        connection.close()
        return False

@buyer_product_api_bp.route('/<int:product_info_id>', methods=['GET'])
def get_product_details(product_info_id):
    """Get complete product details for mobile app"""
    try:
        user_id = request.args.get('user_id', type=int)
        
        connection = get_db_connection()
        if not connection:
            return jsonify({
                'status': 'error',
                'message': 'Database connection error'
            }), 500

        cursor = connection.cursor(dictionary=True)

        # Fetch product and variant details
        cursor.execute("""
            SELECT 
                pi.product_info_id,
                pi.product_category,
                pi.product_name,
                pi.product_description,
                pi.product_main_pic,
                p.product_id,
                p.variant,
                p.color,
                p.stock,
                p.stock_status,
                p.price,
                p.shipping_fee,
                p.status AS product_status,
                p.date_added,
                s.shop_id,
                si.shop_name,
                si.shop_description,
                si.shop_pic,
                u.user_id AS seller_id,
                CONCAT(api.firstname, ' ', api.lastname) AS seller_name,
                u.profile_pic AS seller_profile_pic
            FROM product_info pi
            LEFT JOIN product p ON pi.product_info_id = p.product_info_id
            LEFT JOIN shop_listing sl ON p.product_id = sl.product_id
            LEFT JOIN shop s ON sl.shop_id = s.shop_id
            LEFT JOIN shop_info si ON s.shop_info_id = si.shop_info_id
            LEFT JOIN user_account u ON s.seller_id = u.user_id
            LEFT JOIN account_personal_info api ON u.personal_id = api.personal_id
            WHERE pi.product_info_id = %s AND p.status = 'Active'
        """, (product_info_id,))
        
        product_details = cursor.fetchall()

        if not product_details:
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'error',
                'message': 'Product not found'
            }), 404

        # Fetch product specs
        cursor.execute("""
            SELECT specs_type, specs_content
            FROM product_specs
            WHERE product_info_id = %s
        """, (product_info_id,))
        product_specs = cursor.fetchall()

        # Fetch product images
        cursor.execute("""
            SELECT product_image
            FROM product_images
            WHERE product_info_id = %s
        """, (product_info_id,))
        product_images = cursor.fetchall()

        # Fetch rating info
        cursor.execute("""
            SELECT product_id
            FROM product
            WHERE product_info_id = %s
        """, (product_info_id,))
        product_ids = [row['product_id'] for row in cursor.fetchall()]

        average_rating = 0
        total_ratings = 0

        if product_ids:
            format_ids = ','.join(['%s'] * len(product_ids))
            rating_query = f"""
                SELECT 
                    ROUND(AVG(rate), 1) AS average_rating,
                    COUNT(*) AS total_ratings
                FROM product_rating
                WHERE product_id IN ({format_ids})
            """
            cursor.execute(rating_query, tuple(product_ids))
            rating_result = cursor.fetchone()

            average_rating = float(rating_result['average_rating']) if rating_result['average_rating'] else 0
            total_ratings = rating_result['total_ratings'] if rating_result['total_ratings'] else 0

        # Build the product list with variants
        variants = {}
        shop_info = None
        
        for detail in product_details:
            if shop_info is None:
                shop_info = {
                    'shop_id': detail['shop_id'],
                    'shop_name': detail['shop_name'],
                    'shop_description': detail['shop_description'],
                    'shop_pic': detail['shop_pic'],
                    'shop_image_base64': get_shop_image_base64(detail['shop_pic']),
                    'seller_id': detail['seller_id'],
                    'seller_name': detail['seller_name'],
                    'seller_profile_pic': detail['seller_profile_pic']
                }
            
            variant_key = detail['variant']
            if variant_key not in variants:
                variants[variant_key] = []
            
            variants[variant_key].append({
                'product_id': detail['product_id'],
                'color': detail['color'],
                'stock': detail['stock'],
                'stock_status': detail['stock_status'],
                'price': float(detail['price']),
                'shipping_fee': float(detail['shipping_fee'])
            })

        # Process images
        processed_images = []
        for img in product_images:
            image_base64 = get_additional_image_base64(img['product_image'])
            if image_base64:
                processed_images.append({
                    'filename': img['product_image'],
                    'image_base64': image_base64
                })

        # Get shop products
        shop_products = []
        if shop_info:
            cursor.execute("""
                SELECT DISTINCT
                    pi.product_info_id,
                    pi.product_name,
                    pi.product_main_pic,
                    MIN(p.price) AS min_price,
                    MAX(p.price) AS max_price,
                    MIN(p.shipping_fee) AS shipping_fee,
                    COUNT(DISTINCT p.variant) AS variant_count,
                    COUNT(DISTINCT p.color) AS color_count,
                    COALESCE(bo.total_orders, 0) AS total_orders
                FROM product_info pi
                JOIN product p ON pi.product_info_id = p.product_info_id
                JOIN shop_listing sl ON p.product_id = sl.product_id
                LEFT JOIN (
                    SELECT p2.product_info_id, COUNT(*) AS total_orders
                    FROM buyer_order bo2
                    JOIN product p2 ON bo2.product_id = p2.product_id
                    WHERE bo2.status IN ('Delivered', 'Received')
                    GROUP BY p2.product_info_id
                ) bo ON pi.product_info_id = bo.product_info_id
                WHERE sl.shop_id = %s AND pi.product_info_id != %s AND p.status = 'Active'
                GROUP BY pi.product_info_id
                LIMIT 8
            """, (shop_info['shop_id'], product_info_id))
            
            shop_products_raw = cursor.fetchall()
            for prod in shop_products_raw:
                shop_products.append({
                    'product_info_id': prod['product_info_id'],
                    'product_name': prod['product_name'],
                    'image_base64': get_product_image_base64(prod['product_main_pic']),
                    'min_price': float(prod['min_price']),
                    'max_price': float(prod['max_price']),
                    'shipping_fee': float(prod['shipping_fee']),
                    'variant_count': prod['variant_count'],
                    'color_count': prod['color_count'],
                    'total_orders': prod['total_orders'],
                    'is_liked': is_liked_by_user(prod['product_info_id'], user_id) if user_id else False
                })

        cursor.close()
        connection.close()

        # Build response
        product_info = product_details[0]
        response_data = {
            'product_info_id': product_info['product_info_id'],
            'product_name': product_info['product_name'],
            'product_description': product_info['product_description'],
            'product_category': product_info['product_category'],
            'main_image_base64': get_product_image_base64(product_info['product_main_pic']),
            'variants': variants,
            'specs': product_specs,
            'images': processed_images,
            'average_rating': average_rating,
            'total_ratings': total_ratings,
            'is_liked': is_liked_by_user(product_info_id, user_id) if user_id else False,
            'shop': shop_info,
            'shop_products': shop_products
        }

        return jsonify({
            'status': 'success',
            'data': response_data
        }), 200

    except Exception as e:
        print(f"Product details error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load product details'
        }), 500

@buyer_product_api_bp.route('/products/<int:product_id>/like', methods=['POST'])
def toggle_product_like(product_id):
    """Toggle product like status"""
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

        # Get product_info_id from product_id
        cursor.execute("""
            SELECT product_info_id FROM product WHERE product_id = %s
        """, (product_id,))
        product_result = cursor.fetchone()
        
        if not product_result:
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'error',
                'message': 'Product not found'
            }), 404
            
        product_info_id = product_result['product_info_id']

        # Check if already liked
        cursor.execute("""
            SELECT * FROM buyer_like
            WHERE product_info_id = %s AND buyer_id = %s
        """, (product_info_id, user_id))
        existing_like = cursor.fetchone()

        if existing_like:
            # Remove like
            cursor.execute("""
                DELETE FROM buyer_like
                WHERE product_info_id = %s AND buyer_id = %s
            """, (product_info_id, user_id))
            is_liked = False
            message = "Removed from favorites"
        else:
            # Add like
            cursor.execute("""
                INSERT INTO buyer_like (product_info_id, buyer_id, status)
                VALUES (%s, %s, 'Liked')
            """, (product_info_id, user_id))
            is_liked = True
            message = "Added to favorites"

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({
            'status': 'success',
            'message': message,
            'data': {
                'is_liked': is_liked
            }
        }), 200

    except Exception as e:
        print(f"Toggle like error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to update like status'
        }), 500

@buyer_product_api_bp.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    """Add product to cart"""
    try:
        data = request.get_json()
        
        user_id = data.get('user_id')
        product_info_id = data.get('product_info_id')
        variant = data.get('variant')
        color = data.get('color')
        quantity = data.get('quantity', 1)

        if not all([user_id, product_info_id, variant, color]) or quantity <= 0:
            return jsonify({
                'status': 'error',
                'message': 'Missing required fields or invalid quantity'
            }), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({
                'status': 'error',
                'message': 'Database connection error'
            }), 500

        cursor = connection.cursor(dictionary=True)

        # Find the specific product_id based on variant and color
        cursor.execute("""
            SELECT product_id, stock, price, shipping_fee
            FROM product
            WHERE product_info_id = %s AND variant = %s AND color = %s AND status = 'Active'
        """, (product_info_id, variant, color))
        
        product = cursor.fetchone()
        
        if not product:
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'error',
                'message': 'Selected variant and color combination not found'
            }), 404

        if product['stock'] < quantity:
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'error',
                'message': f'Insufficient stock. Only {product["stock"]} items available'
            }), 400

        # Check if item already exists in cart
        cursor.execute("""
            SELECT cart_id, quantity FROM buyer_cart
            WHERE buyer_id = %s AND product_id = %s AND status = 'On cart'
        """, (user_id, product['product_id']))
        
        existing_cart_item = cursor.fetchone()
        
        total_amount = float(product['price']) * quantity

        if existing_cart_item:
            # Update existing cart item
            new_quantity = existing_cart_item['quantity'] + quantity
            new_total_amount = float(product['price']) * new_quantity
            
            cursor.execute("""
                UPDATE buyer_cart
                SET quantity = %s, total_amount = %s
                WHERE cart_id = %s
            """, (new_quantity, new_total_amount, existing_cart_item['cart_id']))
        else:
            # Insert new cart item
            cursor.execute("""
                INSERT INTO buyer_cart (product_id, buyer_id, quantity, total_amount, status)
                VALUES (%s, %s, %s, %s, 'On cart')
            """, (product['product_id'], user_id, quantity, total_amount))

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({
            'status': 'success',
            'message': 'Product added to cart successfully'
        }), 200

    except Exception as e:
        print(f"Add to cart error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to add product to cart'
        }), 500

@buyer_product_api_bp.route('/<int:product_info_id>/like', methods=['POST'])
def toggle_product_info_like(product_info_id):
    """Toggle product like status by product_info_id"""
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

        # Check if already liked
        cursor.execute("""
            SELECT * FROM buyer_like
            WHERE product_info_id = %s AND buyer_id = %s
        """, (product_info_id, user_id))
        existing_like = cursor.fetchone()

        if existing_like:
            # Remove like
            cursor.execute("""
                DELETE FROM buyer_like
                WHERE product_info_id = %s AND buyer_id = %s
            """, (product_info_id, user_id))
            is_liked = False
            message = "Removed from favorites"
        else:
            # Add like
            cursor.execute("""
                INSERT INTO buyer_like (product_info_id, buyer_id, status)
                VALUES (%s, %s, 'Liked')
            """, (product_info_id, user_id))
            is_liked = True
            message = "Added to favorites"

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({
            'status': 'success',
            'message': message,
            'data': {
                'is_liked': is_liked
            }
        }), 200

    except Exception as e:
        print(f"Toggle like error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to update like status'
        }), 500
