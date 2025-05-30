# IMPORTS
from flask import Blueprint, render_template, flash, session, redirect, url_for, request
from db_connection import get_db_connection
from datetime import datetime, timedelta
import re


seller_vouchers_bp = Blueprint('seller_vouchers', __name__)

# Validation functions
def validate_voucher_name(name):
    """Validate voucher name"""
    if not name or len(name.strip()) < 3:
        return False, "Voucher name must be at least 3 characters long"
    if len(name) > 255:
        return False, "Voucher name must be less than 255 characters"
    if not re.match(r'^[A-Za-z0-9\s\-_.,()&%/]+$', name):
        return False, "Voucher name contains invalid characters"
    return True, "Valid voucher name"

def validate_voucher_description(description):
    """Validate voucher description"""
    if description and len(description) > 500:
        return False, "Description must be less than 500 characters"
    return True, "Valid description"

def validate_min_spend(min_spend):
    """Validate minimum spend amount"""
    try:
        amount = float(min_spend)
        if amount < 0:
            return False, "Minimum spend cannot be negative"
        if amount > 999999.99:
            return False, "Minimum spend cannot exceed ₱999,999.99"
        return True, "Valid minimum spend"
    except (ValueError, TypeError):
        return False, "Invalid minimum spend format"

def validate_voucher_value(voucher_type, voucher_value):
    """Validate voucher value based on type"""
    try:
        value = float(voucher_value)
        if voucher_type == "Discount":
            if value <= 0 or value > 100:
                return False, "Discount percentage must be between 1-100%"
        elif voucher_type == "Free Shipping":
            if value < 0:
                return False, "Shipping discount cannot be negative"
        else:
            return False, "Invalid voucher type"
        return True, "Valid voucher value"
    except (ValueError, TypeError):
        return False, "Invalid voucher value format"

def validate_dates(start_date_str, end_date_str):
    """Validate voucher dates"""
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        today = datetime.now().date()
        
        if start_date < today:
            return False, "Start date cannot be in the past"
        
        if end_date <= start_date:
            return False, "End date must be after start date"
        
        if (end_date - start_date).days < 1:
            return False, "Voucher must be valid for at least 1 day"
        
        if (end_date - start_date).days > 365:
            return False, "Voucher cannot be valid for more than 1 year"
        
        return True, "Valid dates"
    except ValueError:
        return False, "Invalid date format"

def check_duplicate_voucher(seller_id, voucher_name, voucher_id=None):
    """Check if voucher name already exists for this seller"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if voucher_id:
            # For updates, exclude current voucher
            cursor.execute("""
                SELECT COUNT(*) FROM seller_vouchers 
                WHERE seller_id = %s AND LOWER(voucher_name) = LOWER(%s) AND voucher_id != %s
            """, (seller_id, voucher_name, voucher_id))
        else:
            # For new vouchers
            cursor.execute("""
                SELECT COUNT(*) FROM seller_vouchers 
                WHERE seller_id = %s AND LOWER(voucher_name) = LOWER(%s)
            """, (seller_id, voucher_name))
        
        count = cursor.fetchone()[0]
        return count > 0
    except Exception:
        return False
    finally:
        cursor.close()
        conn.close()

def update_voucher_statuses():
    """Update voucher statuses based on current date"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        today = datetime.now().date()
        
        # Update expired vouchers
        cursor.execute("""
            UPDATE seller_vouchers 
            SET status = 'Expired' 
            WHERE voucher_end_date < %s AND status = 'Active'
        """, (today,))
        
        # Update pending vouchers to active
        cursor.execute("""
            UPDATE seller_vouchers 
            SET status = 'Active' 
            WHERE voucher_start_date <= %s AND voucher_end_date >= %s AND status = 'Pending'
        """, (today, today))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error updating voucher statuses: {e}")
    finally:
        cursor.close()
        conn.close()

# VOUCHERS
@seller_vouchers_bp.route('/seller/vouchers')
def vouchers():
    if 'seller' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Seller':
        flash("Unauthorized access. Sellers only.", "danger")
        return redirect(url_for('login.login'))

    seller_id = session['seller']
    
    # Update voucher statuses before displaying
    update_voucher_statuses()

    # Get filter & search parameters from URL
    sort_by = request.args.get('sort_by', 'date_added')
    order = request.args.get('order', 'desc')
    status_filter = request.args.get('status', 'Active')
    search_query = request.args.get('search', '')

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Base query with voucher value
        query = """
            SELECT voucher_id, voucher_type, voucher_name, voucher_description, 
                   voucher_min_spend, voucher_value, voucher_start_date, voucher_end_date, 
                   status, date_added
            FROM seller_vouchers
            WHERE seller_id = %s
        """
        params = [seller_id]

        # Add status filter
        if status_filter and status_filter != 'All':
            query += " AND status = %s"
            params.append(status_filter)

        # Add search functionality
        if search_query:
            query += """
            AND (voucher_name LIKE %s 
                OR voucher_type LIKE %s
                OR voucher_description LIKE %s
                OR status LIKE %s)
            """
            search_param = f"%{search_query}%"
            params.extend([search_param] * 4)

        # Add sorting
        valid_sort_fields = {
            "date_added": "date_added",
            "voucher_name": "voucher_name",
            "voucher_type": "voucher_type",
            "min_spend": "voucher_min_spend",
            "start_date": "voucher_start_date",
            "end_date": "voucher_end_date"
        }
        sort_column = valid_sort_fields.get(sort_by, "date_added")
        order_direction = "DESC" if order == "desc" else "ASC"
        query += f" ORDER BY {sort_column} {order_direction}"

        cursor.execute(query, params)
        vouchers = cursor.fetchall()

        # Get voucher statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_vouchers,
                SUM(CASE WHEN status = 'Active' THEN 1 ELSE 0 END) as active_vouchers,
                SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) as pending_vouchers,
                SUM(CASE WHEN status = 'Expired' THEN 1 ELSE 0 END) as expired_vouchers,
                SUM(CASE WHEN status = 'Archived' THEN 1 ELSE 0 END) as archived_vouchers
            FROM seller_vouchers 
            WHERE seller_id = %s
        """, (seller_id,))
        stats = cursor.fetchone()

    except Exception as e:
        flash(f"Error fetching vouchers: {str(e)}", "danger")
        vouchers = []
        stats = {'total_vouchers': 0, 'active_vouchers': 0, 'expired_vouchers': 0, 'archived_vouchers': 0}

    finally:
        cursor.close()
        connection.close()

    return render_template(
        'seller_vouchers.html', 
        vouchers=vouchers, 
        stats=stats,
        sort_by=sort_by, 
        order=order, 
        status_filter=status_filter, 
        search_query=search_query
    )


# ADD VOUCHER
@seller_vouchers_bp.route('/seller/vouchers/add_voucher', methods=['POST'])
def add_voucher():
    if 'seller' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Seller':
        flash("Unauthorized access. Sellers only.", "danger")
        return redirect(url_for('login.login'))

    seller_id = session['seller']
    
    # Get form data
    voucher_name = request.form.get('voucher_name', '').strip()
    voucher_type = request.form.get('voucher_type', '').strip()
    voucher_description = request.form.get('voucher_description', '').strip()
    voucher_min_spend = request.form.get('voucher_min_spend', '0')
    voucher_value = request.form.get('voucher_value', '0')
    voucher_start_date = request.form.get('voucher_start_date', '')
    voucher_end_date = request.form.get('voucher_end_date', '')

    # Comprehensive validation
    is_valid_name, name_msg = validate_voucher_name(voucher_name)
    if not is_valid_name:
        flash(name_msg, "danger")
        return redirect(url_for('seller_vouchers.vouchers'))

    is_valid_desc, desc_msg = validate_voucher_description(voucher_description)
    if not is_valid_desc:
        flash(desc_msg, "danger")
        return redirect(url_for('seller_vouchers.vouchers'))

    is_valid_min_spend, min_spend_msg = validate_min_spend(voucher_min_spend)
    if not is_valid_min_spend:
        flash(min_spend_msg, "danger")
        return redirect(url_for('seller_vouchers.vouchers'))

    is_valid_value, value_msg = validate_voucher_value(voucher_type, voucher_value)
    if not is_valid_value:
        flash(value_msg, "danger")
        return redirect(url_for('seller_vouchers.vouchers'))

    is_valid_dates, dates_msg = validate_dates(voucher_start_date, voucher_end_date)
    if not is_valid_dates:
        flash(dates_msg, "danger")
        return redirect(url_for('seller_vouchers.vouchers'))

    # Check for duplicate voucher names
    if check_duplicate_voucher(seller_id, voucher_name):
        flash("A voucher with this name already exists. Please choose a different name.", "danger")
        return redirect(url_for('seller_vouchers.vouchers'))

    # Validate voucher type
    valid_types = ['Free Shipping', 'Discount']
    if voucher_type not in valid_types:
        flash("Please select a valid voucher type.", "danger")
        return redirect(url_for('seller_vouchers.vouchers'))

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Determine initial status based on start date
        start_date = datetime.strptime(voucher_start_date, "%Y-%m-%d").date()
        today = datetime.now().date()
        initial_status = 'Active' if start_date <= today else 'Pending'

        # Insert voucher with voucher_value
        cursor.execute("""
            INSERT INTO seller_vouchers 
            (seller_id, voucher_type, voucher_name, voucher_description, voucher_min_spend, 
             voucher_value, voucher_start_date, voucher_end_date, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (seller_id, voucher_type, voucher_name, voucher_description, 
              float(voucher_min_spend), float(voucher_value), voucher_start_date, 
              voucher_end_date, initial_status))
        
        # Add notification
        admin_id = 1
        formatted_start_date = datetime.strptime(voucher_start_date, "%Y-%m-%d").strftime("%b %d, %Y")
        formatted_end_date = datetime.strptime(voucher_end_date, "%Y-%m-%d").strftime("%b %d, %Y")

        if voucher_type == "Discount":
            value_text = f"{voucher_value}% discount"
        else:
            value_text = f"₱{voucher_value} shipping discount"

        notification_title = "New Voucher Created!"
        notification_content = f"Your new voucher **{voucher_name}** ({value_text}) has been successfully created and will be {initial_status.lower()} from {formatted_start_date} to {formatted_end_date}."

        cursor.execute("""
            INSERT INTO notifications (recipient_id, sender_id, notification_type, notification_title, content, status)
            VALUES (%s, %s, 'New Voucher', %s, %s, 'Unread')
        """, (seller_id, admin_id, notification_title, notification_content))

        connection.commit()
        flash(f"Voucher '{voucher_name}' created successfully! Status: {initial_status}", "success")

    except Exception as e:
        connection.rollback()
        flash(f"Error creating voucher: {str(e)}", "danger")
        print(f"Database error in add_voucher: {e}")

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('seller_vouchers.vouchers'))


# UPDATE VOUCHERS
@seller_vouchers_bp.route('/seller/vouchers/update', methods=['POST'])
def update_voucher():
    if 'seller' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Seller':
        flash("Unauthorized access. Sellers only.", "danger")
        return redirect(url_for('login.login'))

    seller_id = session['seller']
    
    # Get form data
    voucher_id = request.form.get('voucher_id')
    voucher_name = request.form.get('voucher_name', '').strip()
    voucher_type = request.form.get('voucher_type', '').strip()
    voucher_description = request.form.get('voucher_description', '').strip()
    voucher_min_spend = request.form.get('voucher_min_spend', '0')
    voucher_value = request.form.get('voucher_value', '0')
    voucher_start_date = request.form.get('voucher_start_date', '')
    voucher_end_date = request.form.get('voucher_end_date', '')

    # Validate voucher ID
    if not voucher_id:
        flash("Invalid voucher ID.", "danger")
        return redirect(url_for('seller_vouchers.vouchers'))

    # Comprehensive validation
    is_valid_name, name_msg = validate_voucher_name(voucher_name)
    if not is_valid_name:
        flash(name_msg, "danger")
        return redirect(url_for('seller_vouchers.vouchers'))

    is_valid_desc, desc_msg = validate_voucher_description(voucher_description)
    if not is_valid_desc:
        flash(desc_msg, "danger")
        return redirect(url_for('seller_vouchers.vouchers'))

    is_valid_min_spend, min_spend_msg = validate_min_spend(voucher_min_spend)
    if not is_valid_min_spend:
        flash(min_spend_msg, "danger")
        return redirect(url_for('seller_vouchers.vouchers'))

    is_valid_value, value_msg = validate_voucher_value(voucher_type, voucher_value)
    if not is_valid_value:
        flash(value_msg, "danger")
        return redirect(url_for('seller_vouchers.vouchers'))

    # For updates, allow past dates if voucher is already active
    try:
        start_date = datetime.strptime(voucher_start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(voucher_end_date, "%Y-%m-%d").date()
        today = datetime.now().date()
        
        if end_date <= start_date:
            flash("End date must be after start date.", "danger")
            return redirect(url_for('seller_vouchers.vouchers'))
        
        if (end_date - start_date).days < 1:
            flash("Voucher must be valid for at least 1 day.", "danger")
            return redirect(url_for('seller_vouchers.vouchers'))
            
        if (end_date - start_date).days > 365:
            flash("Voucher cannot be valid for more than 1 year.", "danger")
            return redirect(url_for('seller_vouchers.vouchers'))
            
    except ValueError:
        flash("Invalid date format.", "danger")
        return redirect(url_for('seller_vouchers.vouchers'))

    # Check for duplicate voucher names (excluding current voucher)
    if check_duplicate_voucher(seller_id, voucher_name, voucher_id):
        flash("A voucher with this name already exists. Please choose a different name.", "danger")
        return redirect(url_for('seller_vouchers.vouchers'))

    # Validate voucher type
    valid_types = ['Free Shipping', 'Discount']
    if voucher_type not in valid_types:
        flash("Please select a valid voucher type.", "danger")
        return redirect(url_for('seller_vouchers.vouchers'))

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Check if voucher belongs to this seller
        cursor.execute("""
            SELECT status FROM seller_vouchers 
            WHERE voucher_id = %s AND seller_id = %s
        """, (voucher_id, seller_id))
        
        voucher_data = cursor.fetchone()
        if not voucher_data:
            flash("Voucher not found or you don't have permission to edit it.", "danger")
            return redirect(url_for('seller_vouchers.vouchers'))

        # Determine new status based on dates
        current_status = voucher_data[0]
        if current_status == 'Archived':
            new_status = 'Archived'  # Keep archived status
        elif end_date < today:
            new_status = 'Expired'
        elif start_date <= today <= end_date:
            new_status = 'Active'
        else:
            new_status = 'Pending'

        # Update voucher
        cursor.execute("""
            UPDATE seller_vouchers 
            SET voucher_name = %s, voucher_type = %s, voucher_description = %s, 
                voucher_min_spend = %s, voucher_value = %s, voucher_start_date = %s, 
                voucher_end_date = %s, status = %s
            WHERE voucher_id = %s AND seller_id = %s
        """, (voucher_name, voucher_type, voucher_description, float(voucher_min_spend), 
              float(voucher_value), voucher_start_date, voucher_end_date, new_status, 
              voucher_id, seller_id))

        if cursor.rowcount == 0:
            flash("No changes were made to the voucher.", "warning")
        else:
            connection.commit()
            flash(f"Voucher '{voucher_name}' updated successfully! Status: {new_status}", "success")

    except Exception as e:
        connection.rollback()
        flash(f"Error updating voucher: {str(e)}", "danger")
        print(f"Database error in update_voucher: {e}")

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('seller_vouchers.vouchers'))


# ARCHIVE VOUCHERS
@seller_vouchers_bp.route('/seller/vouchers/archive_multiple', methods=['POST'])
def archive_multiple_vouchers():
    if 'seller' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Seller':
        flash("Unauthorized access. Sellers only.", "danger")
        return redirect(url_for('login.login'))

    seller_id = session['seller']
    voucher_ids = request.form.get('voucher_ids')
    
    if not voucher_ids:
        flash("No vouchers selected for archiving.", "warning")
        return redirect(url_for('seller_vouchers.vouchers'))

    try:
        voucher_ids = [int(vid.strip()) for vid in voucher_ids.split(',') if vid.strip().isdigit()]
        if not voucher_ids:
            flash("Invalid voucher selection.", "danger")
            return redirect(url_for('seller_vouchers.vouchers'))
    except (ValueError, AttributeError):
        flash("Invalid voucher selection.", "danger")
        return redirect(url_for('seller_vouchers.vouchers'))

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Verify all vouchers belong to this seller and get their current status
        format_ids = ','.join(['%s'] * len(voucher_ids))
        cursor.execute(f"""
            SELECT voucher_id, voucher_name, status FROM seller_vouchers 
            WHERE voucher_id IN ({format_ids}) AND seller_id = %s
        """, tuple(voucher_ids) + (seller_id,))
        
        valid_vouchers = cursor.fetchall()
        
        if len(valid_vouchers) != len(voucher_ids):
            flash("Some vouchers were not found or you don't have permission to archive them.", "danger")
            return redirect(url_for('seller_vouchers.vouchers'))

        # Check if any vouchers are already archived
        already_archived = [v for v in valid_vouchers if v[2] == 'Archived']
        if already_archived:
            archived_names = [v[1] for v in already_archived]
            flash(f"Some vouchers are already archived: {', '.join(archived_names)}", "warning")

        # Archive only non-archived vouchers
        archivable_ids = [v[0] for v in valid_vouchers if v[2] != 'Archived']
        
        if not archivable_ids:
            flash("No vouchers available for archiving.", "warning")
            return redirect(url_for('seller_vouchers.vouchers'))

        # Archive vouchers
        format_archivable = ','.join(['%s'] * len(archivable_ids))
        cursor.execute(f"""
            UPDATE seller_vouchers 
            SET status = 'Archived' 
            WHERE voucher_id IN ({format_archivable}) AND seller_id = %s
        """, tuple(archivable_ids) + (seller_id,))

        archived_count = cursor.rowcount
        connection.commit()
        
        if archived_count > 0:
            flash(f"Successfully archived {archived_count} voucher(s).", "success")
        else:
            flash("No vouchers were archived.", "warning")

    except Exception as e:
        connection.rollback()
        flash(f"Error archiving vouchers: {str(e)}", "danger")
        print(f"Database error in archive_multiple_vouchers: {e}")

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('seller_vouchers.vouchers'))


# UNARCHIVE VOUCHERS
@seller_vouchers_bp.route('/seller/vouchers/unarchive_multiple', methods=['POST'])
def unarchive_multiple_vouchers():
    if 'seller' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Seller':
        flash("Unauthorized access. Sellers only.", "danger")
        return redirect(url_for('login.login'))

    seller_id = session['seller']
    voucher_ids = request.form.get('voucher_ids')
    
    if not voucher_ids:
        flash("No vouchers selected for restoration.", "warning")
        return redirect(url_for('seller_vouchers.vouchers', status='Archived'))

    try:
        voucher_ids = [int(vid.strip()) for vid in voucher_ids.split(',') if vid.strip().isdigit()]
        if not voucher_ids:
            flash("Invalid voucher selection.", "danger")
            return redirect(url_for('seller_vouchers.vouchers', status='Archived'))
    except (ValueError, AttributeError):
        flash("Invalid voucher selection.", "danger")
        return redirect(url_for('seller_vouchers.vouchers', status='Archived'))

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Verify all vouchers belong to this seller and are archived
        format_ids = ','.join(['%s'] * len(voucher_ids))
        cursor.execute(f"""
            SELECT voucher_id, voucher_name, voucher_start_date, voucher_end_date, status 
            FROM seller_vouchers 
            WHERE voucher_id IN ({format_ids}) AND seller_id = %s AND status = 'Archived'
        """, tuple(voucher_ids) + (seller_id,))
        
        valid_vouchers = cursor.fetchall()
        
        if len(valid_vouchers) != len(voucher_ids):
            flash("Some vouchers were not found, don't belong to you, or are not archived.", "danger")
            return redirect(url_for('seller_vouchers.vouchers', status='Archived'))

        # Determine new status for each voucher based on dates
        today = datetime.now().date()
        updates = []
        
        for voucher in valid_vouchers:
            voucher_id, name, start_date, end_date, status = voucher
            
            if end_date < today:
                new_status = 'Expired'
            elif start_date <= today <= end_date:
                new_status = 'Active'
            else:
                new_status = 'Pending'
            
            updates.append((new_status, voucher_id))

        # Update voucher statuses
        cursor.executemany("""
            UPDATE seller_vouchers 
            SET status = %s 
            WHERE voucher_id = %s AND seller_id = %s
        """, [(status, vid, seller_id) for status, vid in updates])

        restored_count = cursor.rowcount
        connection.commit()
        
        if restored_count > 0:
            flash(f"Successfully restored {restored_count} voucher(s).", "success")
        else:
            flash("No vouchers were restored.", "warning")

    except Exception as e:
        connection.rollback()
        flash(f"Error restoring vouchers: {str(e)}", "danger")
        print(f"Database error in unarchive_multiple_vouchers: {e}")

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('seller_vouchers.vouchers', status='Archived'))


def check_and_notify_voucher():
    """Check voucher statuses and send notifications for expiring/expired vouchers"""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    seller_id = session.get('seller')
    if not seller_id:
        return
    admin_id = 1

    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)

    # Get vouchers that are expiring tomorrow or have expired today for current seller
    cursor.execute("""
        SELECT voucher_id, voucher_name, voucher_end_date, status
        FROM seller_vouchers
        WHERE seller_id = %s AND status IN ('Active', 'Pending') 
        AND (voucher_end_date = %s OR voucher_end_date = %s)
    """, (seller_id, tomorrow, today))

    vouchers = cursor.fetchall()

    for voucher in vouchers:
        voucher_name = voucher['voucher_name']
        voucher_end_date = voucher['voucher_end_date']
        voucher_id = voucher['voucher_id']

        # Determine notification type and content
        if voucher_end_date == today:
            # Voucher expires today
            notification_title = "Voucher Expired!"
            notification_content = f"Your voucher **{voucher_name}** has expired today ({voucher_end_date.strftime('%b %d, %Y')}). Consider creating a new voucher to continue attracting customers."
            
            # Update voucher status to expired
            cursor.execute("""
                UPDATE seller_vouchers 
                SET status = 'Expired' 
                WHERE voucher_id = %s
            """, (voucher_id,))
            
        elif voucher_end_date == tomorrow:
            # Expiring in 24 hours (1 day before expiring)
            notification_title = "Voucher Expiring Tomorrow!"
            notification_content = f"Your voucher **{voucher_name}** expires tomorrow ({voucher_end_date.strftime('%b %d, %Y')}). Consider extending it or creating a new one."

        # Check if notification already exists to avoid duplicates
        cursor.execute("""
            SELECT COUNT(*) AS count FROM notifications
            WHERE recipient_id = %s AND content = %s AND status = 'Unread'
        """, (seller_id, notification_content))
        
        result = cursor.fetchone()
        
        if result['count'] == 0:
            cursor.execute("""
                INSERT INTO notifications (recipient_id, sender_id, notification_type, notification_title, content, status)
                VALUES (%s, %s, 'Voucher Alert', %s, %s, 'Unread')
            """, (seller_id, admin_id, notification_title, notification_content))

    connection.commit()
    cursor.close()
    connection.close()
