from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db_connection import get_db_connection

buyer_product_bp = Blueprint('buyer_product', __name__)

def get_product_details(product_info_id):
    connection = get_db_connection()
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
            api.firstname AS seller_firstname,
            api.lastname AS seller_lastname,
            u.profile_pic AS seller_profile_pic
        FROM product_info pi
        LEFT JOIN product p ON pi.product_info_id = p.product_info_id
        LEFT JOIN shop_listing sl ON p.product_id = sl.product_id
        LEFT JOIN shop s ON sl.shop_id = s.shop_id
        LEFT JOIN shop_info si ON s.shop_info_id = si.shop_info_id
        LEFT JOIN user_account u ON s.seller_id = u.user_id
        LEFT JOIN account_personal_info api ON u.personal_id = api.personal_id
        WHERE pi.product_info_id = %s
    """, (product_info_id,))
    
    product_details = cursor.fetchall()

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

        average_rating = rating_result['average_rating'] or 0
        total_ratings = rating_result['total_ratings'] or 0

    # Build the product list
    products = []
    for detail in product_details:
        product = {
            "product_info_id": detail['product_info_id'],
            "product_name": detail['product_name'],
            "product_description": detail['product_description'],
            "product_main_pic": detail['product_main_pic'],
            "product_category": detail['product_category'],
            "shipping_fee": detail['shipping_fee'],
            "product_id": detail['product_id'],
            "variant": detail['variant'],
            "color": detail['color'],
            "stock": detail['stock'],
            "stock_status": detail['stock_status'],
            "price": detail['price'],
            "product_status": detail['product_status'],
            "date_added": detail['date_added'],
            "shop_id": detail['shop_id'],
            "shop_name": detail['shop_name'],
            "shop_description": detail['shop_description'],
            "shop_pic": detail['shop_pic'],
            "seller_id": detail['seller_id'],
            "seller_name": f"{detail['seller_firstname']} {detail['seller_lastname']}",
            "seller_profile_pic": detail['seller_profile_pic'],
        }
        products.append(product)

    cursor.close()
    connection.close()

    return {
        "products": products,
        "specs": product_specs,
        "images": product_images,
        "average_rating": average_rating,
        "total_ratings": total_ratings
    }

def get_shop_products(shop_id, current_product_info_id, limit=8):
    """Get other products from the same shop"""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT DISTINCT
            pi.product_info_id,
            pi.product_name,
            pi.product_main_pic,
            MIN(p.price) AS min_price,
            MAX(p.price) AS max_price,
            MIN(p.shipping_fee) AS shipping_fee,
            COUNT(DISTINCT p.variant) AS variant_count,
            COUNT(DISTINCT p.color) AS color_count
        FROM product_info pi
        JOIN product p ON pi.product_info_id = p.product_info_id
        JOIN shop_listing sl ON p.product_id = sl.product_id
        WHERE sl.shop_id = %s AND pi.product_info_id != %s
        GROUP BY pi.product_info_id
        LIMIT %s
    """, (shop_id, current_product_info_id, limit))
    
    shop_products = cursor.fetchall()
    cursor.close()
    connection.close()
    
    return shop_products

@buyer_product_bp.route('/product/<int:product_info_id>', methods=['GET'])
def product_page(product_info_id):
    buyer_id = session.get('buyer')

    product_data = get_product_details(product_info_id)

    products = product_data['products']
    specs = product_data['specs']
    images = product_data['images']
    average_rating = product_data['average_rating']
    total_ratings = product_data['total_ratings']

    like_status = get_like_status(buyer_id, product_info_id) if buyer_id else {}
    
    # Get products from the same shop
    shop_products = []
    if products:
        shop_products = get_shop_products(products[0]['shop_id'], product_info_id)

    return render_template(
        'buyer_product.html',
        products=products,
        like_status=like_status,
        specs=specs,
        images=images,
        average_rating=average_rating,
        total_ratings=total_ratings,
        shop_products=shop_products
    )


def get_like_status(buyer_id, product_info_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM buyer_like
        WHERE buyer_id = %s AND product_info_id = %s
    """, (buyer_id, product_info_id))
    like_status = cursor.fetchone()
    cursor.close()
    connection.close()
    return like_status is not None


@buyer_product_bp.route('/like_product/<int:product_info_id>', methods=['POST'])
def like_product(product_info_id):
    if 'buyer' not in session:
        flash("Please log in to like or unlike products.", "danger")
        return redirect(url_for('login.login'))

    buyer_id = session['buyer']
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM buyer_like
        WHERE buyer_id = %s AND product_info_id = %s
    """, (buyer_id, product_info_id))
    existing_like = cursor.fetchone()

    if not existing_like:
        cursor.execute("""
            INSERT INTO buyer_like (buyer_id, product_info_id, status)
            VALUES (%s, %s, 'Liked')
        """, (buyer_id, product_info_id))
        flash("Product liked successfully!", "success")
    else:
        flash("You have already liked this product.", "warning")

    connection.commit()
    cursor.close()
    connection.close()
    
    return redirect(url_for('buyer_product.product_page', product_info_id=product_info_id))


@buyer_product_bp.route('/unlike_product/<int:product_info_id>', methods=['POST'])
def unlike_product(product_info_id):
    if 'buyer' not in session:
        flash("Please log in to like or unlike products.", "danger")
        return redirect(url_for('login.login'))

    buyer_id = session['buyer']
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM buyer_like
        WHERE buyer_id = %s AND product_info_id = %s
    """, (buyer_id, product_info_id))
    existing_like = cursor.fetchone()

    if existing_like:
        cursor.execute("""
            DELETE FROM buyer_like
            WHERE buyer_id = %s AND product_info_id = %s
        """, (buyer_id, product_info_id))
        flash("Product unliked successfully!", "success")
    else:
        flash("You have not liked this product.", "warning")

    connection.commit()
    cursor.close()
    connection.close()

    return redirect(url_for('buyer_product.product_page', product_info_id=product_info_id))


@buyer_product_bp.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'buyer' not in session:
        flash("Please log in to add products to cart.", "danger")
        return redirect(url_for('login.login'))

    buyer_id = session['buyer']
    variant = request.form.get('variant')
    color = request.form.get('color')
    quantity = request.form.get('quantity', type=int)
    product_info_id = request.form.get('product_info_id', type=int)

    if not variant or not color or not quantity or quantity <= 0:
        flash("Please select variant, color, and valid quantity.", "danger")
        return redirect(url_for('buyer_product.product_page', product_info_id=product_info_id))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Find the specific product_id based on variant and color
    cursor.execute("""
        SELECT product_id, stock, price, shipping_fee
        FROM product
        WHERE product_info_id = %s AND variant = %s AND color = %s
    """, (product_info_id, variant, color))
    
    product = cursor.fetchone()
    
    if not product:
        flash("Selected variant and color combination not found.", "danger")
        cursor.close()
        connection.close()
        return redirect(url_for('buyer_product.product_page', product_info_id=product_info_id))

    if product['stock'] < quantity:
        flash(f"Insufficient stock. Only {product['stock']} items available.", "danger")
        cursor.close()
        connection.close()
        return redirect(url_for('buyer_product.product_page', product_info_id=product_info_id))

    # Check if item already exists in cart
    cursor.execute("""
        SELECT cart_id, quantity FROM buyer_cart
        WHERE buyer_id = %s AND product_id = %s AND status = 'On cart'
    """, (buyer_id, product['product_id']))
    
    existing_cart_item = cursor.fetchone()
    
    total_amount = product['price'] * quantity

    if existing_cart_item:
        # Update existing cart item
        new_quantity = existing_cart_item['quantity'] + quantity
        new_total_amount = product['price'] * new_quantity
        
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
        """, (product['product_id'], buyer_id, quantity, total_amount))

    connection.commit()
    cursor.close()
    connection.close()

    flash("Product added to cart successfully!", "success")
    return redirect(url_for('buyer_product.product_page', product_info_id=product_info_id))
