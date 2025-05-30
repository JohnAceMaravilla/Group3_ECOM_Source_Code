# IMPORTS
from flask import Blueprint, render_template, flash, session, redirect, url_for, request, send_from_directory
from db_connection import get_db_connection
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
import os
import secrets
import mysql.connector
import re

seller_inventory_bp = Blueprint('seller_inventory', __name__)

# Constants for file uploads
PRODUCT_MAIN_PIC_FOLDER = "static/uploads/seller/product_main_pics"
PRODUCT_IMAGES_FOLDER = "static/uploads/seller/product_images"
PRODUCT_VARIANT_IMAGES_FOLDER = "static/uploads/seller/product_variant_images"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Ensure folders exist
for folder in [PRODUCT_MAIN_PIC_FOLDER, PRODUCT_IMAGES_FOLDER, PRODUCT_VARIANT_IMAGES_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

def save_uploaded_file(file, folder):
    """Save uploaded file and return filename"""
    if file and file.filename:
        temp_token = secrets.token_urlsafe(16)
        filename = f"{temp_token}_{secure_filename(file.filename)}"
        file_path = os.path.join(folder, filename)
        file.save(file_path)
        return filename
    return None

# SELLER INVENTORY
@seller_inventory_bp.route('/seller/inventory')
def inventory():
    if 'seller' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Seller':
        flash("Unauthorized access. Sellers only.", "danger")
        return redirect(url_for('login.login'))

    seller_id = session['seller']
    
    # Get filter & search parameters from URL
    sort_by = request.args.get('sort_by', 'date_added')
    order = request.args.get('order', 'desc')  
    status_filter = request.args.get('status', 'All') 
    search_query = request.args.get('search', '')  
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Base Query
    query = """
    SELECT 
        p.product_id, p.product_info_id, pi.product_name, pi.product_category, pi.product_description, pi.product_main_pic,
        p.variant, p.color, p.stock, p.stock_status, p.price, p.shipping_fee, p.status, p.date_added
    FROM shop s
    JOIN shop_listing sl ON s.shop_id = sl.shop_id
    JOIN product p ON sl.product_id = p.product_id
    JOIN product_info pi ON p.product_info_id = pi.product_info_id
    WHERE s.seller_id = %s
    """

    params = [seller_id]

    # Add FILTERING by status
    if status_filter and status_filter != 'All':
        query += " AND p.stock_status = %s"
        params.append(status_filter)

    # Add MULTI-FIELD SEARCH
    if search_query:
        query += """
        AND (pi.product_name LIKE %s 
             OR pi.product_category LIKE %s
             OR p.variant LIKE %s
             OR p.color LIKE %s
             OR p.stock LIKE %s
             OR p.price LIKE %s
             OR p.status LIKE %s)
        """
        search_param = f"%{search_query}%"
        params.extend([search_param] * 7)  # Apply search across all specified fields

    # Add SORTING
    valid_sort_fields = {
        "date_added": "p.date_added",
        "product_name": "pi.product_name",
        "product_category": "pi.product_category",
        "variant": "p.variant",
        "color": "p.color",
        "stock": "p.stock",
        "price": "p.price"
    }
    sort_column = valid_sort_fields.get(sort_by, "p.date_added")  # Default: sort by date_added
    order_direction = "DESC" if order == "desc" else "ASC"
    query += f" ORDER BY {sort_column} {order_direction}"

    # Execute Query
    cursor.execute(query, params)
    products = cursor.fetchall()

    # Get inventory statistics
    cursor.execute("""
        SELECT 
            COUNT(*) as total_products,
            SUM(CASE WHEN p.stock_status = 'Active' THEN 1 ELSE 0 END) as active_products,
            SUM(CASE WHEN p.stock_status = 'Out of Stock' THEN 1 ELSE 0 END) as out_of_stock_products,
            SUM(CASE WHEN p.stock_status = 'Nearly Out of Stock' THEN 1 ELSE 0 END) as nearly_out_of_stock_products,
            SUM(CASE WHEN p.status = 'Archived' THEN 1 ELSE 0 END) as archived_products
        FROM shop s
        JOIN shop_listing sl ON s.shop_id = sl.shop_id
        JOIN product p ON sl.product_id = p.product_id
        WHERE s.seller_id = %s
    """, (seller_id,))
    stats = cursor.fetchone()

    # Fetch Additional Data (Specs, Images, Variant Images)
    for product in products:
        product_info_id = product["product_info_id"]
        product_id = product["product_id"]

        # Get Product Specs
        cursor.execute("SELECT specs_type, specs_content FROM product_specs WHERE product_info_id = %s", (product_info_id,))
        product["specs"] = cursor.fetchall()

        # Get Product Images
        cursor.execute("SELECT product_image FROM product_images WHERE product_info_id = %s", (product_info_id,))
        product["images"] = [img["product_image"] for img in cursor.fetchall()]
        
        # Get Variant-Specific Images 
        cursor.execute("SELECT product_image FROM product_variant_images WHERE product_id = %s", (product_id,))
        product["variant_images"] = [img["product_image"] for img in cursor.fetchall()]

    cursor.close()
    connection.close()

    return render_template(
        'seller_inventory.html', 
        products=products, 
        sort_by=sort_by, 
        order=order, 
        status_filter=status_filter, 
        search_query=search_query,
        stats=stats
    )


# VALIDATION FUNCTIONS
def validate_product_name(name):
    """Validate that product name contains only letters, numbers, spaces, and basic punctuation"""
    if not name or len(name.strip()) < 2:
        return False, "Product name must be at least 2 characters long"
    if len(name) > 100:
        return False, "Product name must be less than 100 characters"
    if not re.match(r'^[A-Za-z0-9\s\-_.,()&/]+$', name):
        return False, "Product name contains invalid characters"
    return True, "Valid product name"

def validate_price(price):
    """Validate product price"""
    try:
        price_float = float(price)
        if price_float <= 0:
            return False, "Price must be greater than zero"
        if price_float > 999999.99:
            return False, "Price cannot exceed ₱999,999.99"
        return True, "Valid price"
    except (ValueError, TypeError):
        return False, "Invalid price format"

def validate_stock(stock):
    """Validate product stock"""
    try:
        stock_int = int(stock)
        if stock_int < 0:
            return False, "Stock cannot be negative"
        if stock_int > 999999:
            return False, "Stock cannot exceed 999,999 units"
        return True, "Valid stock"
    except (ValueError, TypeError):
        return False, "Invalid stock format"

def validate_description(description):
    """Validate product description"""
    if not description or len(description.strip()) < 10:
        return False, "Description must be at least 10 characters long"
    if len(description) > 1000:
        return False, "Description must be less than 1000 characters"
    return True, "Valid description"

def validate_image_file(file):
    """Validate uploaded image file"""
    if not file or not file.filename:
        return False, "Image file is required"
    
    allowed_extensions = {'png', 'jpg', 'jpeg'}
    file_extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    
    if file_extension not in allowed_extensions:
        return False, "Invalid file format. Only PNG, JPG, and JPEG are allowed"
    
    # Check file size (max 5MB)
    file.seek(0, 2)  # Move to end of file
    file_size = file.tell()
    file.seek(0)  # Reset to beginning
    
    if file_size > 5 * 1024 * 1024:  # 5MB in bytes
        return False, "Image file size must be less than 5MB"
    
    return True, "Valid image file"

def check_existing_product(seller_id, product_name):
    """Check if product with same name already exists for this seller"""
    conn = get_db_connection()
    if not conn:
        return False, None
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT pi.product_info_id, pi.product_name
            FROM product_info pi
            JOIN product p ON pi.product_info_id = p.product_info_id
            JOIN shop_listing sl ON p.product_id = sl.product_id
            WHERE sl.seller_id = %s AND LOWER(pi.product_name) = LOWER(%s)
            LIMIT 1
        """, (seller_id, product_name))
        
        result = cursor.fetchone()
        return result is not None, result[0] if result else None
        
    except Exception as e:
        print(f"Error checking existing product: {e}")
        return False, None
    finally:
        cursor.close()
        conn.close()


# ADD PRODUCT FUNCTION
@seller_inventory_bp.route('/seller/inventory/add_product', methods=['POST'])
def add_product():

    if 'seller' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Seller':
        flash("Unauthorized access. Sellers only.", "danger")
        return redirect(url_for('login.login'))
    
    # Get Seller ID
    seller_id = session['seller']
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Get Product Details
        product_name = request.form.get('product_name', '').strip()
        category = request.form.get('category', '').strip()
        description = request.form.get('description', '').strip()

        # Get Product Image
        main_image = request.files.get('productMainPicture')
        
        # Enhanced Validation - Return first error only
        # Validate product name first
        is_valid_name, name_msg = validate_product_name(product_name)
        if not is_valid_name:
            flash(name_msg, "danger")
            return redirect(url_for('seller_inventory.inventory'))
        
        # Validate category
        valid_categories = ['Mobile Phones', 'Laptop', 'Desktop', 'Audio Equipment', 'Video Equipment', 
                           'Smart Home Devices', 'Photography', 'Wearable Technology', 'Digital Accessories', 'Others']
        if not category or category not in valid_categories:
            flash("Please select a valid product category", "danger")
            return redirect(url_for('seller_inventory.inventory'))
        
        # Validate description
        is_valid_desc, desc_msg = validate_description(description)
        if not is_valid_desc:
            flash(desc_msg, "danger")
            return redirect(url_for('seller_inventory.inventory'))
        
        # Validate main image
        is_valid_image, image_msg = validate_image_file(main_image)
        if not is_valid_image:
            flash(image_msg, "danger")
            return redirect(url_for('seller_inventory.inventory'))

        # Check if product already exists for this seller
        product_exists, existing_product_info_id = check_existing_product(seller_id, product_name)
        
        if product_exists:
            # Update existing product instead of creating new one
            main_image_filename = None
            if main_image and main_image.filename:
                main_image_filename = save_uploaded_file(main_image, PRODUCT_MAIN_PIC_FOLDER)
            
            if main_image_filename:
                cursor.execute("""
                    UPDATE product_info
                    SET product_category = %s, product_description = %s, product_main_pic = %s
                    WHERE product_info_id = %s
                """, (category, description, main_image_filename, existing_product_info_id))
            else:
                cursor.execute("""
                    UPDATE product_info
                    SET product_category = %s, product_description = %s
                    WHERE product_info_id = %s
                """, (category, description, existing_product_info_id))
            
            product_info_id = existing_product_info_id
            flash(f"Product '{product_name}' already exists. Updated existing product information.", "info")
        else:
            # Create new product
            main_image_filename = save_uploaded_file(main_image, PRODUCT_MAIN_PIC_FOLDER)
            cursor.execute("""
                INSERT INTO product_info (product_category, product_name, product_description, product_main_pic)
                VALUES (%s, %s, %s, %s)
            """, (category, product_name, description, main_image_filename))
            product_info_id = cursor.lastrowid
            
            admin_id = 1
            notification_title = "New Product Added!"
            notification_content = f"Your product **{product_name}** has been successfully added to your inventory."

            cursor.execute("""
                INSERT INTO notifications (recipient_id, sender_id, notification_type, notification_title, content, status)
                VALUES (%s, %s, 'New Product', %s, %s, 'Unread')
            """, (seller_id, admin_id, notification_title, notification_content))

        # Get Variants, Color, Price and Stocks (shipping fee is per product_info)
        variants = [v.strip() for v in request.form.getlist('variant[]') if v.strip()]
        colors = [c.strip() for c in request.form.getlist('color[]') if c.strip()]
        stocks = request.form.getlist('stock[]')
        prices = request.form.getlist('price[]')
        shipping_fee = request.form.get('shipping_fee')
        
        # Enhanced validation for variants, colors, stocks, prices, and shipping fee
        if not variants or not colors or not stocks or not prices or not shipping_fee:
            flash("Please complete the Variants, Colors, Stocks & Shipping Fee section.", "warning")
            return redirect(url_for('seller_inventory.inventory'))
        
        if len(colors) != len(stocks) or len(colors) != len(prices):
            flash("Number of colors, stocks, and prices must match.", "danger")
            return redirect(url_for('seller_inventory.inventory'))

        # Validate shipping fee first
        is_valid_shipping, shipping_msg = validate_price(shipping_fee)  # Use same validation as price
        if not is_valid_shipping:
            flash(f"Shipping fee - {shipping_msg}", "danger")
            return redirect(url_for('seller_inventory.inventory'))

        # Validate each stock and price - return first error only
        for i, (stock, price) in enumerate(zip(stocks, prices)):
            # Validate stock
            is_valid_stock, stock_msg = validate_stock(stock)
            if not is_valid_stock:
                flash(f"Color {i+1}: {stock_msg}", "danger")
                return redirect(url_for('seller_inventory.inventory'))
            
            # Validate price
            is_valid_price, price_msg = validate_price(price)
            if not is_valid_price:
                flash(f"Color {i+1}: {price_msg}", "danger")
                return redirect(url_for('seller_inventory.inventory'))

        # Convert to proper types only after validation
        validated_stocks = [int(stock) for stock in stocks]
        validated_prices = [float(price) for price in prices]
        validated_shipping_fee = float(shipping_fee)

        product_ids = []
        color_index = 0  

        # Iterate through each variant
        for variant in variants:
            for i in range(len(colors) // len(variants)):  
                if color_index >= len(colors):
                    break  

                color = colors[color_index]
                stock = validated_stocks[color_index]
                price = validated_prices[color_index]

                stock_status = 'Active' if stock > 10 else 'Nearly Out of Stock' if stock > 0 else 'Out of Stock'

                # Check if this specific variant/color combination already exists
                cursor.execute("""
                    SELECT product_id FROM product 
                    WHERE product_info_id = %s AND variant = %s AND color = %s
                """, (product_info_id, variant, color))
                
                existing_variant = cursor.fetchone()
                
                if existing_variant:
                    # Update existing variant (including shipping fee to keep it consistent)
                    cursor.execute("""
                        UPDATE product 
                        SET stock = stock + %s, price = %s, shipping_fee = %s, stock_status = %s
                        WHERE product_id = %s
                    """, (stock, price, validated_shipping_fee, stock_status, existing_variant[0]))
                    product_ids.append(existing_variant[0])
                    flash(f"Updated existing variant: {variant} - {color}", "info")
                else:
                    # Insert new variant
                    cursor.execute("""
                        INSERT INTO product (product_info_id, variant, color, stock, stock_status, price, shipping_fee)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (product_info_id, variant, color, stock, stock_status, price, validated_shipping_fee))
                    product_ids.append(cursor.lastrowid)

                color_index += 1  

        # Update shipping fee for all products with the same product_info_id to keep consistency
        cursor.execute("""
            UPDATE product 
            SET shipping_fee = %s 
            WHERE product_info_id = %s
        """, (validated_shipping_fee, product_info_id))

        # Get Seller Shop and ensure shop listing exists
        cursor.execute("SELECT shop_id FROM shop WHERE seller_id = %s", (seller_id,))
        shop = cursor.fetchone()
        if shop:
            shop_id = shop[0]
            for product_id in product_ids:
                # Check if listing already exists
                cursor.execute("""
                    SELECT COUNT(*) FROM shop_listing 
                    WHERE shop_id = %s AND seller_id = %s AND product_id = %s
                """, (shop_id, seller_id, product_id))
                
                if cursor.fetchone()[0] == 0:
                    cursor.execute("""
                        INSERT INTO shop_listing (shop_id, seller_id, product_id)
                        VALUES (%s, %s, %s)
                    """, (shop_id, seller_id, product_id))

        # Handle Product Specifications
        specs_types = [s.strip() for s in request.form.getlist('specs_type[]') if s.strip()]
        specs_contents = [s.strip() for s in request.form.getlist('specs_content[]') if s.strip()]
        
        if specs_types and specs_contents and len(specs_types) == len(specs_contents):
            # Delete existing specs if updating
            cursor.execute("DELETE FROM product_specs WHERE product_info_id = %s", (product_info_id,))
            
            # Insert new specs
            cursor.executemany("""
                INSERT INTO product_specs (product_info_id, specs_type, specs_content)
                VALUES (%s, %s, %s)
            """, [(product_info_id, spec_type, spec_content) for spec_type, spec_content in zip(specs_types, specs_contents)])

        # Handle Product Images
        image_files = request.files.getlist('productImages[]')
        valid_image_filenames = []
        
        for image_file in image_files:
            if image_file.filename:
                is_valid_img, img_msg = validate_image_file(image_file)
                if is_valid_img:
                    filename = save_uploaded_file(image_file, PRODUCT_IMAGES_FOLDER)
                    if filename:
                        valid_image_filenames.append((product_info_id, filename))
                else:
                    flash(f"Image '{image_file.filename}': {img_msg}", "warning")
        
        if valid_image_filenames:
            # Delete existing images if updating
            if product_exists:
                cursor.execute("DELETE FROM product_images WHERE product_info_id = %s", (product_info_id,))
            
            cursor.executemany("""
                INSERT INTO product_images (product_info_id, product_image)
                VALUES (%s, %s)
            """, valid_image_filenames)
            
        connection.commit()
        
        if product_exists:
            flash(f"Product '{product_name}' has been successfully updated!", "success")
        else:
            flash(f"Product '{product_name}' has been successfully added!", "success")

    except Exception as e:
        connection.rollback()
        flash(f"Error processing product: {str(e)}", "danger")
        print(f"Database error: {e}")

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('seller_inventory.inventory'))


# UPDATE PRODUCT FUNCTION
@seller_inventory_bp.route('/seller/inventory/update_product', methods=['POST'])
def update_product():
    if 'seller' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Seller':
        flash("Unauthorized access. Sellers only.", "danger")
        return redirect(url_for('login.login'))

    product_id = request.form.get("product_id")
    product_info_id = request.form.get("product_info_id")
    product_name = request.form.get("product_name")
    category = request.form.get("category")
    description = request.form.get("description")
    variant = request.form.get("variant")
    color = request.form.get("color")
    shipping_fee = request.form.get("shipping_fee")
    stock = request.form.get("stock")
    
    # Get current product data for price (since it's not being updated)
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT price FROM product WHERE product_id = %s", (product_id,))
    current_product = cursor.fetchone()
    
    if not current_product:
        flash("Product not found.", "danger")
        cursor.close()
        connection.close()
        return redirect(url_for('seller_inventory.inventory'))
    
    price = current_product['price']
    shipping_fee_float = float(shipping_fee)
    stock_int = int(stock)
    
    # Conditional Statements
    if shipping_fee_float < 0:
        flash("Shipping fee cannot be negative.", "danger")
        cursor.close()
        connection.close()
        return redirect(url_for('seller_inventory.inventory'))
    if stock_int < 0:
        flash("Stock cannot be negative.", "danger")
        cursor.close()
        connection.close()
        return redirect(url_for('seller_inventory.inventory'))
    if not product_name:
        flash("Product Name is required.", "danger")
        cursor.close()
        connection.close()
        return redirect(url_for('seller_inventory.inventory'))
    if not category:
        flash("Product Category is required.", "danger")
        cursor.close()
        connection.close()
        return redirect(url_for('seller_inventory.inventory'))
    if not description:
        flash("Product Description is required.", "danger")
        cursor.close()
        connection.close()
        return redirect(url_for('seller_inventory.inventory'))
    if not variant:
        flash("Product Variant is required.", "danger")
        cursor.close()
        connection.close()
        return redirect(url_for('seller_inventory.inventory'))
    if not color:
        flash("Product Color is required.", "danger")
        cursor.close()
        connection.close()
        return redirect(url_for('seller_inventory.inventory'))
    if not shipping_fee:
        flash("Shipping Fee is required.", "danger")
        cursor.close()
        connection.close()
        return redirect(url_for('seller_inventory.inventory'))
    if not stock:
        flash("Stock is required.", "danger")
        cursor.close()
        connection.close()
        return redirect(url_for('seller_inventory.inventory'))

    # Determine stock status based on stock quantity
    stock_status = 'Active' if stock_int > 10 else 'Nearly Out of Stock' if stock_int > 0 else 'Out of Stock'
    
    specs_types = request.form.getlist("specs_type[]")
    specs_contents = request.form.getlist("specs_content[]")

    main_image = request.files.get("productMainPicture")
    main_image_filename = None
    if main_image and main_image.filename:
        main_image_filename = save_uploaded_file(main_image, PRODUCT_MAIN_PIC_FOLDER)

    image_files = request.files.getlist("productImages[]")
    new_image_filenames = []
    for img in image_files:
        if img.filename:
            filename = save_uploaded_file(img, PRODUCT_IMAGES_FOLDER)
            if filename:
                new_image_filenames.append((product_info_id, filename))
    
    variant_image_files = request.files.getlist("productVariantImages[]")
    new_variant_image_filenames = []
    for img in variant_image_files:
        if img.filename:
            filename = save_uploaded_file(img, PRODUCT_VARIANT_IMAGES_FOLDER)
            if filename:
                new_variant_image_filenames.append((product_id, filename))

    try:
        if main_image_filename:
            cursor.execute("""
                UPDATE product_info
                SET product_name = %s, product_category = %s, product_description = %s, product_main_pic = %s
                WHERE product_info_id = %s
            """, (product_name, category, description, main_image_filename, product_info_id))
        else:
            cursor.execute("""
                UPDATE product_info
                SET product_name = %s, product_category = %s, product_description = %s
                WHERE product_info_id = %s
            """, (product_name, category, description, product_info_id))

        cursor.execute("""
            UPDATE product
            SET variant = %s, color = %s, shipping_fee = %s, stock = %s, stock_status = %s
            WHERE product_id = %s
        """, (variant, color, shipping_fee_float, stock_int, stock_status, product_id))

        # Update shipping fee for all products with the same product_info_id to keep consistency
        cursor.execute("""
            UPDATE product 
            SET shipping_fee = %s 
            WHERE product_info_id = %s
        """, (shipping_fee_float, product_info_id))

        cursor.execute("DELETE FROM product_specs WHERE product_info_id = %s", (product_info_id,))
        for spec_type, spec_content in zip(specs_types, specs_contents):
            cursor.execute("""
                INSERT INTO product_specs (product_info_id, specs_type, specs_content)
                VALUES (%s, %s, %s)
            """, (product_info_id, spec_type, spec_content))

        if new_image_filenames:
            cursor.execute("DELETE FROM product_images WHERE product_info_id = %s", (product_info_id,))
            cursor.executemany("""
                INSERT INTO product_images (product_info_id, product_image)
                VALUES (%s, %s)
            """, new_image_filenames)
            
        if new_variant_image_filenames:
            cursor.execute("DELETE FROM product_variant_images WHERE product_id = %s", (product_id,))
            cursor.executemany("""
                INSERT INTO product_variant_images (product_id, product_image)
                VALUES (%s, %s)
            """, new_variant_image_filenames)

        connection.commit()
        flash(f"Product {product_name} - ({variant}, {color}) has been updated successfully!", "success")

    except Exception as e:
        connection.rollback()
        flash("Invalid Input! Please try again.", "danger")

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('seller_inventory.inventory'))


# AUTOMATIC STOCK ALERT NOTIFICATION
def check_and_notify_stock():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    seller_id = session.get('seller')
    if not seller_id:
        return
    admin_id = 1

    cursor.execute("""
        SELECT p.product_id, pi.product_name, p.variant, p.color ,p.stock_status, p.stock
        FROM product p
        JOIN product_info pi ON p.product_info_id = pi.product_info_id
        JOIN shop_listing sl ON p.product_id = sl.product_id
        WHERE sl.seller_id = %s AND p.stock_status IN ('Out of Stock', 'Nearly Out of Stock')
    """, (seller_id,))
    
    products = cursor.fetchall()
    
    for product in products:
        if product['stock_status'] == 'Out of Stock':
            notification_title = "Out of Stock Alert!"
            notification_content = f"Your product **{product['product_name']} - {product['variant']} ({product['color']})** is completely out of stock. Restock as soon as possible."
        else:  
            notification_title = "Low Stock Warning!"
            notification_content = f"Your product **{product['product_name']} - {product['variant']} ({product['color']})** has {product['stock']} items left. Restock now!"

        # Check if a similar notification was created in the last 24 hours
        cursor.execute("""
            SELECT COUNT(*) AS count FROM notifications
            WHERE recipient_id = %s 
            AND content = %s 
            AND created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
        """, (seller_id, notification_content))
        
        result = cursor.fetchone()
        
        if result['count'] == 0:
            cursor.execute("""
                INSERT INTO notifications (recipient_id, sender_id, notification_type, notification_title, content, status)
                VALUES (%s, %s, 'Stock Alert', %s, %s, 'Unread')
            """, (seller_id, admin_id, notification_title, notification_content))

    connection.commit()
    cursor.close()
    connection.close()


# Routes to serve product images
@seller_inventory_bp.route('/uploads/product_main_pics/<filename>')
def serve_product_main_pic(filename):
    return send_from_directory(PRODUCT_MAIN_PIC_FOLDER, filename)

@seller_inventory_bp.route('/uploads/product_images/<filename>')
def serve_product_image(filename):
    return send_from_directory(PRODUCT_IMAGES_FOLDER, filename)

@seller_inventory_bp.route('/uploads/product_variant_images/<filename>')
def serve_product_variant_image(filename):
    return send_from_directory(PRODUCT_VARIANT_IMAGES_FOLDER, filename)








