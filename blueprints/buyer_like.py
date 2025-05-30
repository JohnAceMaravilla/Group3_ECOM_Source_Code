from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_from_directory
from db_connection import get_db_connection
import os

buyer_like_bp = Blueprint('buyer_like', __name__)

# Constants for product image folders
PRODUCT_MAIN_PIC_FOLDER = "static/uploads/seller/product_main_pics"

def get_liked_products(buyer_id, sort='recent'):
    """Get all products liked by the buyer"""
    connection = get_db_connection()
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
            COALESCE(AVG(pr.rate), 0) AS Average_Rating
        FROM buyer_like bl
        JOIN product_info pi ON bl.product_info_id = pi.product_info_id
        LEFT JOIN product p ON pi.product_info_id = p.product_info_id
        LEFT JOIN product_rating pr ON p.product_id = pr.product_id
        WHERE bl.buyer_id = %s AND bl.status = 'Liked'
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

    cursor.execute(query, (buyer_id,))
    products = cursor.fetchall()

    # Add liked status (always True for this page)
    for product in products:
        product['liked'] = True

    cursor.close()
    connection.close()
    return products

@buyer_like_bp.route('/buyer/likes')
def buyer_likes():
    """Display all liked products for the buyer"""
    if 'buyer' not in session:
        flash("Please log in to view your liked products.", "danger")
        return redirect(url_for('login.login'))

    buyer_id = session['buyer']
    sort = request.args.get('sort', default='recent', type=str)
    
    # Get liked products
    products = get_liked_products(buyer_id, sort)
    
    return render_template('buyer_like.html', 
                         products=products, 
                         sort=sort)

@buyer_like_bp.route('/buyer/toggle_like_product/<int:product_info_id>', methods=['POST'])
def toggle_like_product(product_info_id):
    """Toggle like/unlike for a product"""
    if 'buyer' not in session:
        flash("Please log in to like or unlike products.", "danger")
        return redirect(url_for('login.login'))

    buyer_id = session['buyer']
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Check if product is already liked
        cursor.execute("""
            SELECT * FROM buyer_like
            WHERE product_info_id = %s AND buyer_id = %s
        """, (product_info_id, buyer_id))
        existing_like = cursor.fetchone()

        if existing_like:
            # Unlike the product
            cursor.execute("""
                DELETE FROM buyer_like
                WHERE product_info_id = %s AND buyer_id = %s
            """, (product_info_id, buyer_id))
            flash("Product removed from your likes!", "success")
        else:
            # Like the product
            cursor.execute("""
                INSERT INTO buyer_like (product_info_id, buyer_id, status)
                VALUES (%s, %s, 'Liked')
            """, (product_info_id, buyer_id))
            flash("Product added to your likes!", "success")

        connection.commit()

    except Exception as e:
        connection.rollback()
        flash(f"Error updating like status: {str(e)}", "danger")
    finally:
        cursor.close()
        connection.close()

    return redirect(request.referrer or url_for('buyer_like.buyer_likes'))

# Route to serve product main images
@buyer_like_bp.route('/buyer/uploads/product_main_pics/<filename>')
def serve_product_main_pic(filename):
    return send_from_directory(PRODUCT_MAIN_PIC_FOLDER, filename)
