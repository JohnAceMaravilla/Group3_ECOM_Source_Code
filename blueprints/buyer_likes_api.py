from flask import Blueprint, jsonify, request
from flask_cors import CORS
from db_connection import get_db_connection
import base64
import os

buyer_likes_api_bp = Blueprint('buyer_likes_api', __name__, url_prefix='/api/mobile/buyer/likes')

# Enable CORS for mobile app communication
CORS(buyer_likes_api_bp)

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

@buyer_likes_api_bp.route('', methods=['GET'])
def get_liked_products():
    """Get all products liked by the buyer with sorting"""
    try:
        user_id = request.args.get('user_id', type=int)
        sort = request.args.get('sort', default='recent', type=str)
        
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

        # Base query to get liked products with product details
        query = """
            SELECT 
                pi.product_info_id,
                pi.product_category,
                pi.product_name,
                pi.product_description,
                pi.product_main_pic,
                MIN(p.price) AS min_price,
                MAX(p.price) AS max_price,
                COUNT(DISTINCT p.variant) AS variant_count,
                COUNT(DISTINCT p.color) AS color_count,
                bl.date_liked,
                COALESCE(AVG(pr.rate), 0) AS average_rating,
                COUNT(DISTINCT pr.rating_id) AS total_ratings,
                COALESCE(bo.total_orders, 0) AS total_orders
            FROM buyer_like bl
            JOIN product_info pi ON bl.product_info_id = pi.product_info_id
            LEFT JOIN product p ON pi.product_info_id = p.product_info_id
            LEFT JOIN product_rating pr ON p.product_id = pr.product_id
            LEFT JOIN (
                SELECT p2.product_info_id, COUNT(*) AS total_orders
                FROM buyer_order bo2
                JOIN product p2 ON bo2.product_id = p2.product_id
                WHERE bo2.status IN ('Delivered', 'Received')
                GROUP BY p2.product_info_id
            ) bo ON pi.product_info_id = bo.product_info_id
            WHERE bl.buyer_id = %s AND bl.status = 'Liked' AND p.status = 'Active'
            GROUP BY pi.product_info_id, pi.product_category, pi.product_name, 
                     pi.product_description, pi.product_main_pic, bl.date_liked
        """

        # Add sorting
        if sort == 'recent':
            query += " ORDER BY bl.date_liked DESC"
        elif sort == 'oldest':
            query += " ORDER BY bl.date_liked ASC"
        elif sort == 'name_asc':
            query += " ORDER BY pi.product_name ASC"
        elif sort == 'name_desc':
            query += " ORDER BY pi.product_name DESC"
        elif sort == 'price_low':
            query += " ORDER BY MIN(p.price) ASC"
        elif sort == 'price_high':
            query += " ORDER BY MIN(p.price) DESC"
        else:
            query += " ORDER BY bl.date_liked DESC"  # Default to recent

        cursor.execute(query, (user_id,))
        products = cursor.fetchall()

        # Process products and add base64 images
        processed_products = []
        for product in products:
            processed_product = {
                'product_info_id': product['product_info_id'],
                'product_category': product['product_category'],
                'product_name': product['product_name'],
                'product_description': product['product_description'],
                'min_price': float(product['min_price']) if product['min_price'] else 0,
                'max_price': float(product['max_price']) if product['max_price'] else 0,
                'variant_count': product['variant_count'] or 0,
                'color_count': product['color_count'] or 0,
                'average_rating': float(product['average_rating']) if product['average_rating'] else 0,
                'total_ratings': product['total_ratings'] or 0,
                'total_orders': product['total_orders'] or 0,
                'date_liked': product['date_liked'].isoformat() if product['date_liked'] else None,
                'is_liked': True,  # Always true for liked products
                'image_base64': get_product_image_base64(product['product_main_pic'])
            }
            processed_products.append(processed_product)

        cursor.close()
        connection.close()

        return jsonify({
            'status': 'success',
            'data': processed_products,
            'count': len(processed_products)
        }), 200

    except Exception as e:
        print(f"Get liked products error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load liked products'
        }), 500

@buyer_likes_api_bp.route('/<int:product_info_id>', methods=['DELETE'])
def remove_like(product_info_id):
    """Remove a product from likes"""
    try:
        data = request.get_json()
        user_id = data.get('user_id') if data else None
        
        # Also check query parameters
        if not user_id:
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

        # Check if the like exists
        cursor.execute("""
            SELECT * FROM buyer_like
            WHERE product_info_id = %s AND buyer_id = %s AND status = 'Liked'
        """, (product_info_id, user_id))
        existing_like = cursor.fetchone()

        if not existing_like:
            cursor.close()
            connection.close()
            return jsonify({
                'status': 'error',
                'message': 'Product not found in your likes'
            }), 404

        # Remove the like
        cursor.execute("""
            DELETE FROM buyer_like
            WHERE product_info_id = %s AND buyer_id = %s
        """, (product_info_id, user_id))

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({
            'status': 'success',
            'message': 'Product removed from likes'
        }), 200

    except Exception as e:
        print(f"Remove like error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to remove product from likes'
        }), 500
