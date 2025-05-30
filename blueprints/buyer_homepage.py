# IMPORTS
from flask import Blueprint, render_template, session, redirect, url_for
from blueprints.get_user_info import get_personal_info, get_address_info, get_contact_info, get_valid_info, get_business_info
from db_connection import get_db_connection

buyer_homepage_bp = Blueprint('buyer_homepage', __name__)

def get_best_sellers(limit=8):
    """Get top selling products"""
    connection = get_db_connection()
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
    
    cursor.execute(query, (limit,))
    products = cursor.fetchall()
    
    # Update the rating information
    for product in products:
        product['Average_Rating'] = float(product['avg_rating']) if product['avg_rating'] else 0
        product['Total_Ratings'] = product['total_ratings'] if product['total_ratings'] else 0
    
    cursor.close()
    connection.close()
    return products

def get_highest_rated(limit=8):
    """Get highest rated products (prioritizes products with ratings, but shows all if needed)"""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # First try to get products with ratings
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
    
    cursor.execute(query, (limit,))
    products = cursor.fetchall()
    
    # If no products with ratings found, get any active products
    if not products:
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
            ORDER BY avg_rating DESC, p.date_added DESC
            LIMIT %s
        """
        
        cursor.execute(query, (limit,))
        products = cursor.fetchall()
    
    # Update the rating information
    for product in products:
        product['Average_Rating'] = float(product['avg_rating']) if product['avg_rating'] else 0
        product['Total_Ratings'] = product['total_ratings'] if product['total_ratings'] else 0
    
    cursor.close()
    connection.close()
    return products

def get_most_reviewed(limit=8):
    """Get most reviewed products"""
    connection = get_db_connection()
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
    
    cursor.execute(query, (limit,))
    products = cursor.fetchall()
    
    # Update the rating information
    for product in products:
        product['Average_Rating'] = float(product['avg_rating']) if product['avg_rating'] else 0
        product['Total_Ratings'] = product['total_ratings'] if product['total_ratings'] else 0
    
    cursor.close()
    connection.close()
    return products

def is_liked(product_info_id, buyer_id):
    """Check if a product is liked by the buyer"""
    if not buyer_id:
        return False
        
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

# Homepage
@buyer_homepage_bp.route('/')
def show_buyer_homepage():
    buyer_info = session.get('buyer', {})
    buyer_id = session.get('buyer')
    
    # Get top products data
    best_sellers = get_best_sellers(8)
    highest_rated = get_highest_rated(8)
    most_reviewed = get_most_reviewed(8)
    
    # Add liked status for each product if user is logged in
    for product_list in [best_sellers, highest_rated, most_reviewed]:
        for product in product_list:
            product['liked'] = is_liked(product['product_info_id'], buyer_id)
    
    if buyer_info:
        personal = get_personal_info()  
        address = get_address_info()
        contact = get_contact_info()
        valid = get_valid_info()
        business = get_business_info()

        return render_template('buyer_homepage.html', 
                             personal=personal, 
                             address=address, 
                             contact=contact, 
                             valid=valid, 
                             business=business,
                             best_sellers=best_sellers,
                             highest_rated=highest_rated,
                             most_reviewed=most_reviewed)
    else:
        return render_template('buyer_homepage.html',
                             best_sellers=best_sellers,
                             highest_rated=highest_rated,
                             most_reviewed=most_reviewed)

# Route to serve product main images
from flask import send_from_directory
import os

PRODUCT_MAIN_PIC_FOLDER = "static/uploads/seller/product_main_pics"

@buyer_homepage_bp.route('/homepage/uploads/product_main_pics/<filename>')
def serve_product_main_pic(filename):
    return send_from_directory(PRODUCT_MAIN_PIC_FOLDER, filename)
