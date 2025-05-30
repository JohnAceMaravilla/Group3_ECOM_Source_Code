# IMPORTS
from flask import Blueprint, render_template, flash, session, redirect, url_for, request, send_from_directory
from db_connection import get_db_connection
from werkzeug.utils import secure_filename
import os
import secrets

seller_shop_profile_bp = Blueprint('seller_shop_profile', __name__)

# Constants for file uploads
SHOP_PROFILE_UPLOAD_FOLDER = "static/uploads/seller/shop_profile"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Ensure folder exists
if not os.path.exists(SHOP_PROFILE_UPLOAD_FOLDER):
    os.makedirs(SHOP_PROFILE_UPLOAD_FOLDER)

def validate_file_extension(filename):
    """Validate file extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_file_size(file):
    """Validate file size (max 5MB)"""
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB in bytes
    return file.content_length <= MAX_FILE_SIZE if hasattr(file, 'content_length') else True

@seller_shop_profile_bp.route('/seller/shop_profile')
def shop_profile():
    if 'seller' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Seller':
        flash("Unauthorized access. Sellers only.", "danger")
        return redirect(url_for('login.login'))
    
    seller_id = session['seller']
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get shop information
        cursor.execute("""
            SELECT 
                s.shop_id, s.date_created as shop_date_created,
                si.shop_info_id, si.shop_name, si.shop_description, si.shop_pic
            FROM shop s
            JOIN shop_info si ON s.shop_info_id = si.shop_info_id
            WHERE s.seller_id = %s
        """, (seller_id,))
        shop_data = cursor.fetchone()
        
        if not shop_data:
            flash("Shop not found.", "danger")
            return redirect(url_for('seller_dashboard.dashboard'))
        
        # Get shop products with pagination
        page = request.args.get('page', 1, type=int)
        per_page = 12
        offset = (page - 1) * per_page
        
        # Get products count for pagination (count unique product_info_id)
        cursor.execute("""
            SELECT COUNT(DISTINCT pi.product_info_id) as total
            FROM shop_listing sl
            JOIN product p ON sl.product_id = p.product_id
            JOIN product_info pi ON p.product_info_id = pi.product_info_id
            WHERE sl.shop_id = %s AND p.status = 'Active'
        """, (shop_data['shop_id'],))
        total_products = cursor.fetchone()['total']
        
        # Get products grouped by product_info_id
        cursor.execute("""
            SELECT 
                pi.product_info_id, pi.product_name, pi.product_description, 
                pi.product_main_pic, pi.product_category,
                GROUP_CONCAT(DISTINCT CONCAT(p.variant, ' (', p.color, ')') SEPARATOR ', ') as variants_colors,
                MIN(p.price) as min_price,
                MAX(p.price) as max_price,
                SUM(p.stock) as total_stock,
                MAX(p.date_added) as latest_date_added
            FROM shop_listing sl
            JOIN product p ON sl.product_id = p.product_id
            JOIN product_info pi ON p.product_info_id = pi.product_info_id
            WHERE sl.shop_id = %s AND p.status = 'Active'
            GROUP BY pi.product_info_id, pi.product_name, pi.product_description, 
                     pi.product_main_pic, pi.product_category
            ORDER BY latest_date_added DESC
            LIMIT %s OFFSET %s
        """, (shop_data['shop_id'], per_page, offset))
        products = cursor.fetchall()
        
        # Get shop ratings and feedback statistics
        cursor.execute("""
            SELECT 
                COUNT(pr.rating_id) as total_ratings,
                AVG(pr.rate) as average_rating
            FROM product_rating pr
            WHERE pr.shop_id = %s
        """, (shop_data['shop_id'],))
        rating_stats = cursor.fetchone()
        
        # Get feedback count
        cursor.execute("""
            SELECT COUNT(pf.feedback_id) as total_feedback
            FROM product_feedback pf
            WHERE pf.shop_id = %s
        """, (shop_data['shop_id'],))
        feedback_stats = cursor.fetchone()
        
        # Get rating distribution
        cursor.execute("""
            SELECT 
                rate,
                COUNT(*) as count
            FROM product_rating
            WHERE shop_id = %s
            GROUP BY rate
            ORDER BY rate DESC
        """, (shop_data['shop_id'],))
        rating_distribution = cursor.fetchall()
        
        # Calculate pagination info
        total_pages = (total_products + per_page - 1) // per_page
        has_prev = page > 1
        has_next = page < total_pages
        
        return render_template('seller_shop_profile.html',
                             shop_data=shop_data,
                             products=products,
                             rating_stats=rating_stats,
                             feedback_stats=feedback_stats,
                             rating_distribution=rating_distribution,
                             total_products=total_products,
                             page=page,
                             total_pages=total_pages,
                             has_prev=has_prev,
                             has_next=has_next)
                             
    except Exception as e:
        flash(f"Error loading shop profile: {str(e)}", "danger")
        return redirect(url_for('seller_dashboard.dashboard'))
    finally:
        cursor.close()
        conn.close()

@seller_shop_profile_bp.route('/seller/shop_profile/update', methods=['POST'])
def update_shop_profile():
    if 'seller' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Seller':
        flash("Unauthorized access. Sellers only.", "danger")
        return redirect(url_for('login.login'))
    
    seller_id = session['seller']
    shop_name = request.form.get('shop_name')
    shop_description = request.form.get('shop_description')
    shop_pic = request.files.get('shop_pic')
    
    # Validate inputs
    if not shop_name or not shop_description:
        flash("Shop name and description are required.", "danger")
        return redirect(url_for('seller_shop_profile.shop_profile'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get current shop info
        cursor.execute("""
            SELECT si.shop_info_id, si.shop_pic
            FROM shop s
            JOIN shop_info si ON s.shop_info_id = si.shop_info_id
            WHERE s.seller_id = %s
        """, (seller_id,))
        shop_info = cursor.fetchone()
        
        if not shop_info:
            flash("Shop not found.", "danger")
            return redirect(url_for('seller_shop_profile.shop_profile'))
        
        # Handle file upload if new image is provided
        filename = shop_info['shop_pic']  # Keep existing filename by default
        
        if shop_pic and shop_pic.filename:
            if not validate_file_extension(shop_pic.filename):
                flash('Invalid file type. Please upload png, jpg, or jpeg files only.', 'danger')
                return redirect(url_for('seller_shop_profile.shop_profile'))
            
            if not validate_file_size(shop_pic):
                flash('File size too large. Maximum size is 5MB.', 'danger')
                return redirect(url_for('seller_shop_profile.shop_profile'))
            
            # Delete old image if it exists
            if shop_info['shop_pic']:
                old_file_path = os.path.join(SHOP_PROFILE_UPLOAD_FOLDER, shop_info['shop_pic'])
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
            
            # Save new image
            temp_token = secrets.token_urlsafe(16)
            filename = f"{temp_token}_{secure_filename(shop_pic.filename)}"
            file_path = os.path.join(SHOP_PROFILE_UPLOAD_FOLDER, filename)
            shop_pic.save(file_path)
        
        # Update shop information
        cursor.execute("""
            UPDATE shop_info 
            SET shop_name = %s, shop_description = %s, shop_pic = %s
            WHERE shop_info_id = %s
        """, (shop_name, shop_description, filename, shop_info['shop_info_id']))
        
        conn.commit()
        flash("Shop profile updated successfully!", "success")
        
    except Exception as e:
        conn.rollback()
        flash(f"Error updating shop profile: {str(e)}", "danger")
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('seller_shop_profile.shop_profile'))

@seller_shop_profile_bp.route('/seller/uploads/shop_profile/<filename>')
def serve_shop_pic(filename):
    return send_from_directory(SHOP_PROFILE_UPLOAD_FOLDER, filename) 