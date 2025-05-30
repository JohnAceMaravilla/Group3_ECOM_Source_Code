from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_from_directory
from db_connection import get_db_connection
import os

buyer_search_bp = Blueprint('buyer_search', __name__)

# Constants for product image folders
PRODUCT_MAIN_PIC_FOLDER = "static/uploads/seller/product_main_pics"

def search_products(query, category='', min_price=0, max_price=0, sort='recent', popularity=''):
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
            COALESCE(feedback_stats.total_feedback, 0) AS total_feedback,
            COALESCE(rating_stats.avg_rating, 0) AS avg_rating,
            COALESCE(rating_stats.total_ratings, 0) AS total_ratings
        FROM product_info pi
        LEFT JOIN product p ON pi.product_info_id = p.product_info_id
        LEFT JOIN (
            SELECT p2.product_info_id, COUNT(bo.order_id) AS total_orders
            FROM product p2
            LEFT JOIN buyer_order bo ON p2.product_id = bo.product_id
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
        WHERE 1=1
    """

    filters = []
    
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

    # Handle sorting based on popularity or date
    if popularity == 'top_selling':
        base_query += " ORDER BY total_orders DESC, p.date_added DESC"
    elif popularity == 'most_reviewed':
        base_query += " ORDER BY total_feedback DESC, p.date_added DESC"
    elif popularity == 'highest_rated':
        base_query += " ORDER BY avg_rating DESC, total_ratings DESC, p.date_added DESC"
    elif sort == 'recent':
        base_query += " ORDER BY p.date_added DESC"
    elif sort == 'oldest':
        base_query += " ORDER BY p.date_added ASC"
    else:
        base_query += " ORDER BY p.date_added DESC"

    cursor.execute(base_query, tuple(filters))
    products = cursor.fetchall()

    # Update the rating information from the query results
    for product in products:
        product['Average_Rating'] = float(product['avg_rating']) if product['avg_rating'] else 0
        product['Total_Ratings'] = product['total_ratings'] if product['total_ratings'] else 0

    cursor.close()
    connection.close()
    return products

def get_all_categories():
    """Get all unique product categories for the filter dropdown"""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    cursor.execute("SELECT DISTINCT product_category FROM product_info ORDER BY product_category")
    categories = cursor.fetchall()
    
    cursor.close()
    connection.close()
    return [cat['product_category'] for cat in categories]

@buyer_search_bp.route('/toggle_like_product/<int:product_info_id>', methods=['POST'])
def toggle_like_product(product_info_id):
    if 'buyer' not in session:
        flash("Please log in to like or unlike products.", "danger")
        return redirect(url_for('login.login'))  
    
    buyer_id = session['buyer']  

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM buyer_like
        WHERE product_info_id = %s AND buyer_id = %s
    """, (product_info_id, buyer_id))
    existing_like = cursor.fetchone()

    if existing_like:
        cursor.execute("""
            DELETE FROM buyer_like
            WHERE product_info_id = %s AND buyer_id = %s
        """, (product_info_id, buyer_id))
        connection.commit()
        flash("Product unliked successfully!", "success")
    else:
        cursor.execute("""
            INSERT INTO buyer_like (product_info_id, buyer_id, status)
            VALUES (%s, %s, 'Liked')
        """, (product_info_id, buyer_id))
        connection.commit()
        flash("Product liked successfully!", "success")

    cursor.close()
    connection.close()

    return redirect(request.referrer)  

def is_liked(product_info_id, buyer_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM buyer_like
        WHERE product_info_id = %s AND buyer_id = %s AND status = 'Liked'
    """, (product_info_id, buyer_id))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result is not None

@buyer_search_bp.route('/search', methods=['GET'])
def search_page():
    # Pagination settings
    ITEMS_PER_PAGE = 16
    
    query = request.args.get('query', default='', type=str)
    category = request.args.get('category', default='', type=str)
    min_price = request.args.get('min_price', default=0, type=int)
    max_price = request.args.get('max_price', default=0, type=int)
    sort = request.args.get('sort', default='recent', type=str)
    popularity = request.args.get('popularity', default='', type=str)
    page = request.args.get('page', default=1, type=int)
    
    # Price validation: ensure min_price is not above max_price
    if min_price > 0 and max_price > 0 and min_price > max_price:
        # Swap the values
        min_price, max_price = max_price, min_price
    
    if 'reset' in request.args:
        min_price = 0
        max_price = 0
        sort = 'recent'
        popularity = ''
        category = ''
        page = 1

    # Get all products first
    all_products = search_products(query, category, min_price, max_price, sort, popularity)
    
    # Get all categories for filter dropdown
    all_categories = get_all_categories()
    
    # Calculate pagination
    total_products = len(all_products)
    total_pages = (total_products + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE  # Ceiling division
    
    # Ensure page is within valid range
    if page < 1:
        page = 1
    elif page > total_pages and total_pages > 0:
        page = total_pages
    
    # Get products for current page
    start_index = (page - 1) * ITEMS_PER_PAGE
    end_index = start_index + ITEMS_PER_PAGE
    products = all_products[start_index:end_index]
    
    # Calculate pagination info
    has_prev = page > 1
    has_next = page < total_pages
    prev_page = page - 1 if has_prev else None
    next_page = page + 1 if has_next else None
    
    # Generate page numbers for pagination display
    page_numbers = []
    if total_pages <= 7:
        page_numbers = list(range(1, total_pages + 1))
    else:
        if page <= 4:
            page_numbers = list(range(1, 6)) + ['...', total_pages]
        elif page > total_pages - 4:
            page_numbers = [1, '...'] + list(range(total_pages - 4, total_pages + 1))
        else:
            page_numbers = [1, '...'] + list(range(page - 1, page + 2)) + ['...', total_pages]
    
    buyer_id = session.get('buyer')  
    for product in products:
        product['liked'] = is_liked(product['product_info_id'], buyer_id) if buyer_id else False

    return render_template('buyer_search.html', 
                           products=products, 
                           query=query,
                           category=category,
                           all_categories=all_categories,
                           min_price=min_price, 
                           max_price=max_price, 
                           sort=sort, 
                           popularity=popularity,
                           # Pagination variables
                           page=page,
                           total_pages=total_pages,
                           total_products=total_products,
                           has_prev=has_prev,
                           has_next=has_next,
                           prev_page=prev_page,
                           next_page=next_page,
                           page_numbers=page_numbers)

# Route to serve product main images
@buyer_search_bp.route('/search/uploads/product_main_pics/<filename>')
def serve_product_main_pic(filename):
    return send_from_directory(PRODUCT_MAIN_PIC_FOLDER, filename)
