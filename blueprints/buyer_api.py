from flask import Blueprint, jsonify, request
from flask_cors import CORS
from db_connection import get_db_connection
import base64

buyer_api_bp = Blueprint('buyer_api', __name__, url_prefix='/api/mobile/buyer')

# Enable CORS for mobile app communication
CORS(buyer_api_bp)

def get_best_sellers_mobile(limit=8):
    """Get top selling products for mobile"""
    connection = get_db_connection()
    if not connection:
        return []
    
    cursor = connection.cursor(dictionary=True)
    
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
            COALESCE(order_stats.total_orders, 0) AS total_orders,
            COALESCE(rating_stats.avg_rating, 0) AS avg_rating,
            COALESCE(rating_stats.total_ratings, 0) AS total_ratings
        FROM product_info pi
        LEFT JOIN product p ON pi.product_info_id = p.product_info_id
        LEFT JOIN (
            SELECT p2.product_info_id, COUNT(bo.order_id) AS total_orders
            FROM product p2
            LEFT JOIN buyer_order bo ON p2.product_id = bo.product_id
            WHERE bo.status IN ('Delivered', 'Received')
            GROUP BY p2.product_info_id
        ) order_stats ON pi.product_info_id = order_stats.product_info_id
        LEFT JOIN (
            SELECT p4.product_info_id, AVG(pr.rate) AS avg_rating, COUNT(pr.rating_id) AS total_ratings
            FROM product p4
            LEFT JOIN product_rating pr ON p4.product_id = pr.product_id
            GROUP BY p4.product_info_id
        ) rating_stats ON pi.product_info_id = rating_stats.product_info_id
        WHERE p.status = 'Active'
        GROUP BY pi.product_info_id
        HAVING total_orders > 0
        ORDER BY total_orders DESC, avg_rating DESC
        LIMIT %s
    """
    
    try:
        cursor.execute(query, (limit,))
        products = cursor.fetchall()
        
        # Process products for mobile
        for product in products:
            product['average_rating'] = float(product['avg_rating']) if product['avg_rating'] else 0
            product['total_ratings'] = product['total_ratings'] if product['total_ratings'] else 0
            product['image_base64'] = get_product_image_base64(product['product_main_pic'])
            
        cursor.close()
        connection.close()
        return products
    except Exception as e:
        print(f"Error getting best sellers: {e}")
        cursor.close()
        connection.close()
        return []

def get_highest_rated_mobile(limit=8):
    """Get highest rated products for mobile"""
    connection = get_db_connection()
    if not connection:
        return []
    
    cursor = connection.cursor(dictionary=True)
    
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
            COALESCE(order_stats.total_orders, 0) AS total_orders,
            COALESCE(rating_stats.avg_rating, 0) AS avg_rating,
            COALESCE(rating_stats.total_ratings, 0) AS total_ratings
        FROM product_info pi
        LEFT JOIN product p ON pi.product_info_id = p.product_info_id
        LEFT JOIN (
            SELECT p2.product_info_id, COUNT(bo.order_id) AS total_orders
            FROM product p2
            LEFT JOIN buyer_order bo ON p2.product_id = bo.product_id
            WHERE bo.status IN ('Delivered', 'Received')
            GROUP BY p2.product_info_id
        ) order_stats ON pi.product_info_id = order_stats.product_info_id
        LEFT JOIN (
            SELECT p4.product_info_id, AVG(pr.rate) AS avg_rating, COUNT(pr.rating_id) AS total_ratings
            FROM product p4
            LEFT JOIN product_rating pr ON p4.product_id = pr.product_id
            GROUP BY p4.product_info_id
        ) rating_stats ON pi.product_info_id = rating_stats.product_info_id
        WHERE p.status = 'Active'
        GROUP BY pi.product_info_id
        HAVING total_ratings >= 1 AND avg_rating >= 3.0
        ORDER BY avg_rating DESC, total_ratings DESC
        LIMIT %s
    """
    
    try:
        cursor.execute(query, (limit,))
        products = cursor.fetchall()
        
        # If no products with ratings found, get any active products
        if not products:
            fallback_query = """
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
                    0 AS total_orders,
                    0 AS avg_rating,
                    0 AS total_ratings
                FROM product_info pi
                LEFT JOIN product p ON pi.product_info_id = p.product_info_id
                WHERE p.status = 'Active'
                GROUP BY pi.product_info_id
                ORDER BY p.date_added DESC
                LIMIT %s
            """
            cursor.execute(fallback_query, (limit,))
            products = cursor.fetchall()
        
        # Process products for mobile
        for product in products:
            product['average_rating'] = float(product['avg_rating']) if product['avg_rating'] else 0
            product['total_ratings'] = product['total_ratings'] if product['total_ratings'] else 0
            product['image_base64'] = get_product_image_base64(product['product_main_pic'])
            
        cursor.close()
        connection.close()
        return products
    except Exception as e:
        print(f"Error getting highest rated: {e}")
        cursor.close()
        connection.close()
        return []

def get_featured_products_mobile(limit=8):
    """Get featured products for mobile (mix of best sellers and highest rated)"""
    connection = get_db_connection()
    if not connection:
        return []
    
    cursor = connection.cursor(dictionary=True)
    
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
            COALESCE(order_stats.total_orders, 0) AS total_orders,
            COALESCE(rating_stats.avg_rating, 0) AS avg_rating,
            COALESCE(rating_stats.total_ratings, 0) AS total_ratings
        FROM product_info pi
        LEFT JOIN product p ON pi.product_info_id = p.product_info_id
        LEFT JOIN (
            SELECT p2.product_info_id, COUNT(bo.order_id) AS total_orders
            FROM product p2
            LEFT JOIN buyer_order bo ON p2.product_id = bo.product_id
            WHERE bo.status IN ('Delivered', 'Received')
            GROUP BY p2.product_info_id
        ) order_stats ON pi.product_info_id = order_stats.product_info_id
        LEFT JOIN (
            SELECT p4.product_info_id, AVG(pr.rate) AS avg_rating, COUNT(pr.rating_id) AS total_ratings
            FROM product p4
            LEFT JOIN product_rating pr ON p4.product_id = pr.product_id
            GROUP BY p4.product_info_id
        ) rating_stats ON pi.product_info_id = rating_stats.product_info_id
        WHERE p.status = 'Active'
        GROUP BY pi.product_info_id
        ORDER BY 
            (COALESCE(order_stats.total_orders, 0) * 0.7 + COALESCE(rating_stats.avg_rating, 0) * 0.3) DESC,
            p.date_added DESC
        LIMIT %s
    """
    
    try:
        cursor.execute(query, (limit,))
        products = cursor.fetchall()
        
        # Process products for mobile
        for product in products:
            product['average_rating'] = float(product['avg_rating']) if product['avg_rating'] else 0
            product['total_ratings'] = product['total_ratings'] if product['total_ratings'] else 0
            product['image_base64'] = get_product_image_base64(product['product_main_pic'])
            
        cursor.close()
        connection.close()
        return products
    except Exception as e:
        print(f"Error getting featured products: {e}")
        cursor.close()
        connection.close()
        return []

def get_product_categories():
    """Get all product categories"""
    connection = get_db_connection()
    if not connection:
        return []
    
    cursor = connection.cursor(dictionary=True)
    
    # Define all standard categories
    standard_categories = [
        'Mobile Phones', 'Laptop', 'Desktop', 'Audio Equipment', 'Video Equipment', 
        'Smart Home Devices', 'Photography', 'Wearable Tech', 'Digital Accessories', 'Others'
    ]
    
    # Get actual product counts for existing categories
    query = """
        SELECT 
            pi.product_category,
            COUNT(DISTINCT pi.product_info_id) AS product_count,
            MIN(p.price) AS min_price
        FROM product_info pi
        LEFT JOIN product p ON pi.product_info_id = p.product_info_id
        WHERE p.status = 'Active'
        GROUP BY pi.product_category
        ORDER BY product_count DESC
    """
    
    try:
        cursor.execute(query)
        existing_categories = {cat['product_category']: cat for cat in cursor.fetchall()}
        
        # Build complete category list with counts
        categories = []
        for category in standard_categories:
            if category in existing_categories:
                categories.append(existing_categories[category])
            else:
                categories.append({
                    'product_category': category,
                    'product_count': 0,
                    'min_price': None
                })
        
        cursor.close()
        connection.close()
        return categories
    except Exception as e:
        print(f"Error getting categories: {e}")
        cursor.close()
        connection.close()
        return []

def get_product_image_base64(image_filename):
    """Convert product image to base64 for mobile transmission"""
    if not image_filename:
        return None
    
    try:
        import os
        image_path = os.path.join("static/uploads/seller/product_main_pics", image_filename)
        if os.path.exists(image_path):
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                return f"data:image/jpeg;base64,{encoded_string}"
    except Exception as e:
        print(f"Error encoding image {image_filename}: {e}")
    
    return None

def is_liked_by_user(product_info_id, user_id):
    """Check if a product is liked by the user"""
    if not user_id:
        return False
        
    connection = get_db_connection()
    if not connection:
        return False
    
    cursor = connection.cursor()
    cursor.execute("""
        SELECT 1 FROM buyer_like
        WHERE product_info_id = %s AND buyer_id = %s AND status = 'Liked'
        LIMIT 1
    """, (product_info_id, user_id))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result is not None

def get_most_reviewed_mobile(limit=8):
    """Get most reviewed products for mobile"""
    connection = get_db_connection()
    if not connection:
        return []
    
    cursor = connection.cursor(dictionary=True)
    
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
            COALESCE(order_stats.total_orders, 0) AS total_orders,
            COALESCE(feedback_stats.total_feedback, 0) AS total_feedback,
            COALESCE(rating_stats.avg_rating, 0) AS avg_rating,
            COALESCE(rating_stats.total_ratings, 0) AS total_ratings
        FROM product_info pi
        LEFT JOIN product p ON pi.product_info_id = p.product_info_id
        LEFT JOIN (
            SELECT p2.product_info_id, COUNT(bo.order_id) AS total_orders
            FROM product p2
            LEFT JOIN buyer_order bo ON p2.product_id = bo.product_id
            WHERE bo.status IN ('Delivered', 'Received')
            GROUP BY p2.product_info_id
        ) order_stats ON pi.product_info_id = order_stats.product_info_id
        LEFT JOIN (
            SELECT p3.product_info_id, COUNT(pf.feedback_id) AS total_feedback
            FROM product p3
            LEFT JOIN product_feedback pf ON p3.product_id = pf.product_id
            GROUP BY p3.product_info_id
        ) feedback_stats ON pi.product_info_id = feedback_stats.product_info_id
        LEFT JOIN (
            SELECT p4.product_info_id, AVG(pr.rate) AS avg_rating, COUNT(pr.rating_id) AS total_ratings
            FROM product p4
            LEFT JOIN product_rating pr ON p4.product_id = pr.product_id
            GROUP BY p4.product_info_id
        ) rating_stats ON pi.product_info_id = rating_stats.product_info_id
        WHERE p.status = 'Active'
        GROUP BY pi.product_info_id
        HAVING total_feedback > 0
        ORDER BY total_feedback DESC, avg_rating DESC
        LIMIT %s
    """
    
    try:
        cursor.execute(query, (limit,))
        products = cursor.fetchall()
        
        # Process products for mobile
        for product in products:
            product['average_rating'] = float(product['avg_rating']) if product['avg_rating'] else 0
            product['total_ratings'] = product['total_ratings'] if product['total_ratings'] else 0
            product['total_feedback'] = product['total_feedback'] if product['total_feedback'] else 0
            product['image_base64'] = get_product_image_base64(product['product_main_pic'])
            
        cursor.close()
        connection.close()
        return products
    except Exception as e:
        print(f"Error getting most reviewed: {e}")
        cursor.close()
        connection.close()
        return []

# API Endpoints

@buyer_api_bp.route('/homepage', methods=['GET'])
def get_homepage_data():
    """Get all homepage data for mobile app"""
    try:
        # Get user_id from query params (if authenticated)
        user_id = request.args.get('user_id', type=int)
        
        # Get all homepage sections - REMOVED featured_products, ADDED most_reviewed
        best_sellers = get_best_sellers_mobile(8)
        highest_rated = get_highest_rated_mobile(8)
        most_reviewed = get_most_reviewed_mobile(8)
        categories = get_product_categories()
        
        # Add liked status for authenticated users
        if user_id:
            for product_list in [best_sellers, highest_rated, most_reviewed]:
                for product in product_list:
                    product['is_liked'] = is_liked_by_user(product['product_info_id'], user_id)
        
        # Convert prices to proper format
        for product_list in [best_sellers, highest_rated, most_reviewed]:
            for product in product_list:
                # Ensure prices are returned as floats
                if product.get('min_price'):
                    product['min_price'] = float(product['min_price'])
                if product.get('max_price'):
                    product['max_price'] = float(product['max_price'])
                if product.get('average_rating'):
                    product['average_rating'] = float(product['average_rating'])
        
        return jsonify({
            'status': 'success',
            'data': {
                'best_sellers': best_sellers,
                'highest_rated': highest_rated,
                'most_reviewed': most_reviewed,
                'categories': categories,  # Return all categories
                'banners': [
                    {
                        'id': 1,
                        'title': 'Welcome to Fenamaz!',
                        'subtitle': 'Discover amazing tech products',
                        'image_url': None
                    }
                ]
            }
        }), 200
        
    except Exception as e:
        print(f"Homepage error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load homepage data'
        }), 500

@buyer_api_bp.route('/products/featured', methods=['GET'])
def get_featured_products():
    """Get featured products"""
    try:
        limit = request.args.get('limit', 8, type=int)
        user_id = request.args.get('user_id', type=int)
        
        products = get_featured_products_mobile(limit)
        
        # Add liked status for authenticated users and convert prices
        if user_id:
            for product in products:
                product['is_liked'] = is_liked_by_user(product['product_info_id'], user_id)
        
        # Convert prices to proper format
        for product in products:
            if product.get('min_price'):
                product['min_price'] = float(product['min_price'])
            if product.get('max_price'):
                product['max_price'] = float(product['max_price'])
            if product.get('average_rating'):
                product['average_rating'] = float(product['average_rating'])
        
        return jsonify({
            'status': 'success',
            'data': products
        }), 200
        
    except Exception as e:
        print(f"Featured products error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load featured products'
        }), 500

@buyer_api_bp.route('/products/best-sellers', methods=['GET'])
def get_best_sellers():
    """Get best selling products"""
    try:
        limit = request.args.get('limit', 8, type=int)
        user_id = request.args.get('user_id', type=int)
        
        products = get_best_sellers_mobile(limit)
        
        # Add liked status for authenticated users and convert prices
        if user_id:
            for product in products:
                product['is_liked'] = is_liked_by_user(product['product_info_id'], user_id)
        
        # Convert prices to proper format
        for product in products:
            if product.get('min_price'):
                product['min_price'] = float(product['min_price'])
            if product.get('max_price'):
                product['max_price'] = float(product['max_price'])
            if product.get('average_rating'):
                product['average_rating'] = float(product['average_rating'])
        
        return jsonify({
            'status': 'success',
            'data': products
        }), 200
        
    except Exception as e:
        print(f"Best sellers error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load best sellers'
        }), 500

@buyer_api_bp.route('/products/highest-rated', methods=['GET'])
def get_highest_rated():
    """Get highest rated products"""
    try:
        limit = request.args.get('limit', 8, type=int)
        user_id = request.args.get('user_id', type=int)
        
        products = get_highest_rated_mobile(limit)
        
        # Add liked status for authenticated users and convert prices
        if user_id:
            for product in products:
                product['is_liked'] = is_liked_by_user(product['product_info_id'], user_id)
        
        # Convert prices to proper format
        for product in products:
            if product.get('min_price'):
                product['min_price'] = float(product['min_price'])
            if product.get('max_price'):
                product['max_price'] = float(product['max_price'])
            if product.get('average_rating'):
                product['average_rating'] = float(product['average_rating'])
        
        return jsonify({
            'status': 'success',
            'data': products
        }), 200
        
    except Exception as e:
        print(f"Highest rated error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load highest rated products'
        }), 500

@buyer_api_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get product categories"""
    try:
        categories = get_product_categories()
        
        return jsonify({
            'status': 'success',
            'data': categories
        }), 200
        
    except Exception as e:
        print(f"Categories error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load categories'
        }), 500

@buyer_api_bp.route('/products/search', methods=['GET'])
def search_products():
    """Search products"""
    try:
        query = request.args.get('q', '').strip()
        category = request.args.get('category', '').strip()
        limit = request.args.get('limit', 20, type=int)
        user_id = request.args.get('user_id', type=int)
        
        if not query and not category:
            return jsonify({
                'status': 'error',
                'message': 'Search query or category is required'
            }), 400
        
        connection = get_db_connection()
        if not connection:
            return jsonify({
                'status': 'error',
                'message': 'Database connection error'
            }), 500
        
        cursor = connection.cursor(dictionary=True)
        
        # Build search query
        where_conditions = ["p.status = 'Active'"]
        params = []
        
        if query:
            where_conditions.append("(pi.product_name LIKE %s OR pi.product_description LIKE %s)")
            params.extend([f"%{query}%", f"%{query}%"])
        
        if category:
            where_conditions.append("pi.product_category = %s")
            params.append(category)
        
        search_query = f"""
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
                COALESCE(rating_stats.avg_rating, 0) AS avg_rating,
                COALESCE(rating_stats.total_ratings, 0) AS total_ratings
            FROM product_info pi
            LEFT JOIN product p ON pi.product_info_id = p.product_info_id
            LEFT JOIN (
                SELECT p4.product_info_id, AVG(pr.rate) AS avg_rating, COUNT(pr.rating_id) AS total_ratings
                FROM product p4
                LEFT JOIN product_rating pr ON p4.product_id = pr.product_id
                GROUP BY p4.product_info_id
            ) rating_stats ON pi.product_info_id = rating_stats.product_info_id
            WHERE {' AND '.join(where_conditions)}
            GROUP BY pi.product_info_id
            ORDER BY avg_rating DESC, pi.product_name ASC
            LIMIT %s
        """
        
        params.append(limit)
        cursor.execute(search_query, params)
        products = cursor.fetchall()
        
        # Process products for mobile
        for product in products:
            product['average_rating'] = float(product['avg_rating']) if product['avg_rating'] else 0
            product['total_ratings'] = product['total_ratings'] if product['total_ratings'] else 0
            product['image_base64'] = get_product_image_base64(product['product_main_pic'])
            
            # Convert prices to proper format
            if product.get('min_price'):
                product['min_price'] = float(product['min_price'])
            if product.get('max_price'):
                product['max_price'] = float(product['max_price'])
            
            # Add liked status for authenticated users
            if user_id:
                product['is_liked'] = is_liked_by_user(product['product_info_id'], user_id)
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'status': 'success',
            'data': products,
            'count': len(products)
        }), 200
        
    except Exception as e:
        print(f"Search error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Search failed'
        }), 500

@buyer_api_bp.route('/products/<int:product_id>/like', methods=['POST'])
def toggle_product_like(product_id):
    """Toggle product like status"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({
                'status': 'error',
                'message': 'User ID is required'
            }), 400
        
        connection = get_db_connection()
        if not connection:
            return jsonify({
                'status': 'error',
                'message': 'Database connection error'
            }), 500
        
        cursor = connection.cursor()
        
        # Check if already liked
        cursor.execute("""
            SELECT like_id, status FROM buyer_like
            WHERE product_info_id = %s AND buyer_id = %s
        """, (product_id, user_id))
        existing_like = cursor.fetchone()
        
        if existing_like:
            # Toggle existing like
            new_status = 'Unliked' if existing_like[1] == 'Liked' else 'Liked'
            cursor.execute("""
                UPDATE buyer_like 
                SET status = %s, date_liked = NOW()
                WHERE like_id = %s
            """, (new_status, existing_like[0]))
        else:
            # Create new like
            cursor.execute("""
                INSERT INTO buyer_like (product_info_id, buyer_id, status, date_liked)
                VALUES (%s, %s, 'Liked', NOW())
            """, (product_id, user_id))
            new_status = 'Liked'
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({
            'status': 'success',
            'data': {
                'is_liked': new_status == 'Liked'
            }
        }), 200
        
    except Exception as e:
        print(f"Like toggle error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to toggle like'
        }), 500

@buyer_api_bp.route('/products/most-reviewed', methods=['GET'])
def get_most_reviewed():
    """Get most reviewed products"""
    try:
        limit = request.args.get('limit', 8, type=int)
        user_id = request.args.get('user_id', type=int)
        
        products = get_most_reviewed_mobile(limit)
        
        # Add liked status for authenticated users and convert prices
        if user_id:
            for product in products:
                product['is_liked'] = is_liked_by_user(product['product_info_id'], user_id)
        
        # Convert prices to proper format
        for product in products:
            if product.get('min_price'):
                product['min_price'] = float(product['min_price'])
            if product.get('max_price'):
                product['max_price'] = float(product['max_price'])
            if product.get('average_rating'):
                product['average_rating'] = float(product['average_rating'])
        
        return jsonify({
            'status': 'success',
            'data': products
        }), 200
        
    except Exception as e:
        print(f"Most reviewed products error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load most reviewed products'
        }), 500

@buyer_api_bp.route('/products/category/<category>', methods=['GET'])
def get_products_by_category(category):
    """Get products by category for mobile app"""
    try:
        # Get query parameters
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        min_price = request.args.get('min_price', 0, type=float)
        max_price = request.args.get('max_price', 0, type=float)
        sort = request.args.get('sort', 'recent')
        user_id = request.args.get('user_id', type=int)
        
        connection = get_db_connection()
        if not connection:
            return jsonify({
                'status': 'error',
                'message': 'Database connection error'
            }), 500
        
        cursor = connection.cursor(dictionary=True)
        
        # Build the query with filters
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
                COALESCE(order_stats.total_orders, 0) AS total_orders,
                COALESCE(rating_stats.avg_rating, 0) AS avg_rating,
                COALESCE(rating_stats.total_ratings, 0) AS total_ratings
            FROM product_info pi
            LEFT JOIN product p ON pi.product_info_id = p.product_info_id
            LEFT JOIN (
                SELECT p2.product_info_id, COUNT(bo.order_id) AS total_orders
                FROM product p2
                LEFT JOIN buyer_order bo ON p2.product_id = bo.product_id
                WHERE bo.status IN ('Delivered', 'Received')
                GROUP BY p2.product_info_id
            ) order_stats ON pi.product_info_id = order_stats.product_info_id
            LEFT JOIN (
                SELECT p4.product_info_id, AVG(pr.rate) AS avg_rating, COUNT(pr.rating_id) AS total_ratings
                FROM product p4
                LEFT JOIN product_rating pr ON p4.product_id = pr.product_id
                GROUP BY p4.product_info_id
            ) rating_stats ON pi.product_info_id = rating_stats.product_info_id
            WHERE pi.product_category = %s AND p.status = 'Active'
        """
        
        params = [category]
        
        # Add price filters
        if min_price > 0:
            query += " AND p.price >= %s"
            params.append(min_price)
        
        if max_price > 0:
            query += " AND p.price <= %s"
            params.append(max_price)
        
        query += " GROUP BY pi.product_info_id"
        
        # Add sorting
        if sort == 'price_low':
            query += " ORDER BY min_price ASC"
        elif sort == 'price_high':
            query += " ORDER BY min_price DESC"
        elif sort == 'rating':
            query += " ORDER BY avg_rating DESC, total_ratings DESC"
        elif sort == 'popular':
            query += " ORDER BY total_orders DESC"
        else:  # recent
            query += " ORDER BY p.date_added DESC"
        
        query += " LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        products = cursor.fetchall()
        
        # Process products for mobile
        for product in products:
            product['average_rating'] = float(product['avg_rating']) if product['avg_rating'] else 0
            product['total_ratings'] = product['total_ratings'] if product['total_ratings'] else 0
            product['image_base64'] = get_product_image_base64(product['product_main_pic'])
            
            # Convert prices to proper format
            if product.get('min_price'):
                product['min_price'] = float(product['min_price'])
            if product.get('max_price'):
                product['max_price'] = float(product['max_price'])
            
            # Add liked status for authenticated users
            if user_id:
                product['is_liked'] = is_liked_by_user(product['product_info_id'], user_id)
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'status': 'success',
            'data': products,
            'count': len(products),
            'category': category
        }), 200
        
    except Exception as e:
        print(f"Category products error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load category products'
        }), 500
