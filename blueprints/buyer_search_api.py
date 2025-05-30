from flask import Blueprint, request, jsonify
from db_connection import get_db_connection
import base64
import os

buyer_search_api_bp = Blueprint('buyer_search_api', __name__)

def search_products_mobile(query='', category='', min_price=0, max_price=0, sort='recent', user_id=None, limit=20, offset=0):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Base query with search functionality
    base_query = """
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
            p.date_added,
            COALESCE(order_stats.total_orders, 0) AS total_orders,
            COALESCE(rating_stats.avg_rating, 0) AS average_rating,
            COALESCE(rating_stats.total_ratings, 0) AS total_ratings
    """
    
    # Add like status if user is logged in
    if user_id:
        base_query += """,
            CASE WHEN bl.like_id IS NOT NULL THEN true ELSE false END AS is_liked
        """
    
    base_query += """
        FROM product_info pi
        LEFT JOIN product p ON pi.product_info_id = p.product_info_id
        LEFT JOIN (
            SELECT p2.product_info_id, COUNT(bo.order_id) AS total_orders
            FROM product p2
            LEFT JOIN buyer_order bo ON p2.product_id = bo.product_id
            GROUP BY p2.product_info_id
        ) order_stats ON pi.product_info_id = order_stats.product_info_id
        LEFT JOIN (
            SELECT p4.product_info_id, AVG(pr.rate) AS avg_rating, COUNT(pr.rating_id) AS total_ratings
            FROM product p4
            LEFT JOIN product_rating pr ON p4.product_id = pr.product_id
            GROUP BY p4.product_info_id
        ) rating_stats ON pi.product_info_id = rating_stats.product_info_id
    """
    
    # Add like join if user is logged in
    if user_id:
        base_query += """
            LEFT JOIN buyer_like bl ON pi.product_info_id = bl.product_info_id 
                AND bl.buyer_id = %s AND bl.status = 'Liked'
        """
    
    base_query += " WHERE p.status = 'Active'"

    filters = []
    
    # Add user_id as first parameter if needed
    if user_id:
        filters.append(user_id)
    
    # Search query filter
    if query:
        base_query += " AND (pi.product_name LIKE %s OR pi.product_description LIKE %s OR pi.product_category LIKE %s)"
        search_term = f"%{query}%"
        filters.extend([search_term, search_term, search_term])
    
    # Category filter
    if category:
        base_query += " AND pi.product_category = %s"
        filters.append(category)
    
    # Price filters
    if min_price > 0:
        base_query += " AND p.price >= %s"
        filters.append(min_price)
    
    if max_price > 0:
        base_query += " AND p.price <= %s"
        filters.append(max_price)
    
    base_query += " GROUP BY pi.product_info_id"

    # Sorting
    if sort == 'price_low':
        base_query += " ORDER BY min_price ASC"
    elif sort == 'price_high':
        base_query += " ORDER BY max_price DESC"
    elif sort == 'rating':
        base_query += " ORDER BY average_rating DESC, total_ratings DESC"
    elif sort == 'popular':
        base_query += " ORDER BY total_orders DESC"
    else:  # recent
        base_query += " ORDER BY p.date_added DESC"
    
    # Add pagination
    base_query += " LIMIT %s OFFSET %s"
    filters.extend([limit, offset])

    cursor.execute(base_query, tuple(filters))
    products = cursor.fetchall()

    # Process products to add image data
    for product in products:
        if product['product_main_pic']:
            image_path = os.path.join('static/uploads/seller/product_main_pics', product['product_main_pic'])
            if os.path.exists(image_path):
                try:
                    with open(image_path, 'rb') as img_file:
                        img_data = img_file.read()
                        product['image_base64'] = f"data:image/jpeg;base64,{base64.b64encode(img_data).decode('utf-8')}"
                except Exception as e:
                    product['image_base64'] = None
            else:
                product['image_base64'] = None
        else:
            product['image_base64'] = None

    cursor.close()
    connection.close()
    return products

def get_all_categories_mobile():
    """Get all unique product categories for the filter dropdown"""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Define all standard categories
    standard_categories = [
        'Mobile Phones', 'Laptop', 'Desktop', 'Audio Equipment', 'Video Equipment', 
        'Smart Home Devices', 'Photography', 'Wearable Tech', 'Digital Accessories', 'Others'
    ]
    
    # Get actual product counts for existing categories
    cursor.execute("""
        SELECT DISTINCT pi.product_category, COUNT(p.product_id) as product_count
        FROM product_info pi
        LEFT JOIN product p ON pi.product_info_id = p.product_info_id
        WHERE p.status = 'Active'
        GROUP BY pi.product_category
        ORDER BY pi.product_category
    """)
    existing_categories = {cat['product_category']: cat['product_count'] for cat in cursor.fetchall()}
    
    # Build complete category list with counts
    categories = []
    for category in standard_categories:
        categories.append({
            'product_category': category,
            'product_count': existing_categories.get(category, 0)
        })
    
    cursor.close()
    connection.close()
    return categories

@buyer_search_api_bp.route('/api/mobile/buyer/search', methods=['GET'])
def search_products_api():
    try:
        # Get query parameters
        query = request.args.get('q', '', type=str)
        category = request.args.get('category', '', type=str)
        min_price = request.args.get('min_price', 0, type=float)
        max_price = request.args.get('max_price', 0, type=float)
        sort = request.args.get('sort', 'recent', type=str)
        user_id = request.args.get('user_id', type=int)
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Search products
        products = search_products_mobile(
            query=query,
            category=category,
            min_price=min_price,
            max_price=max_price,
            sort=sort,
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        
        return jsonify({
            'status': 'success',
            'data': products,
            'count': len(products),
            'query': query,
            'category': category
        })
        
    except Exception as e:
        print(f"Search error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to search products'
        }), 500

@buyer_search_api_bp.route('/api/mobile/buyer/search/categories', methods=['GET'])
def get_search_categories_api():
    try:
        categories = get_all_categories_mobile()
        
        return jsonify({
            'status': 'success',
            'data': categories
        })
        
    except Exception as e:
        print(f"Get categories error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to get categories'
        }), 500
