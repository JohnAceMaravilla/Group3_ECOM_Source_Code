from flask import Blueprint, render_template, flash, session, redirect, url_for, request, jsonify
from db_connection import get_db_connection  

buyer_notifications_bp = Blueprint('buyer_notifications', __name__)

# BUYER NOTIFICATIONS LIST
@buyer_notifications_bp.route('/buyer/notifications')
def notifications():
    if 'buyer' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Buyer':
        flash("Unauthorized access. Buyers only.", "danger")
        return redirect(url_for('login.login'))
    
    buyer_id = session.get('buyer') 
    
    if not buyer_id:
        flash("Invalid session. Please log in again.", "danger")
        return redirect(url_for('login.login'))

    sort_by = request.args.get('sort_by', 'recent')  
    page = request.args.get('page', 1, type=int)
    per_page = 10  # 10 notifications per page
    
    order_by = "DESC" if sort_by == "recent" else "ASC"
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  

    # First, mark all unread notifications as read
    cursor.execute("""
        UPDATE notifications 
        SET status = 'Read' 
        WHERE recipient_id = %s AND status = 'Unread'
    """, (buyer_id,))
    conn.commit()

    # Get total count of notifications
    cursor.execute("""
        SELECT COUNT(*) as total
        FROM notifications 
        WHERE recipient_id = %s
    """, (buyer_id,))
    
    total_notifications = cursor.fetchone()['total']
    total_pages = (total_notifications + per_page - 1) // per_page  # Calculate total pages

    # Then fetch notifications with pagination
    cursor.execute(f"""
        SELECT notification_id, notification_type, notification_title, content, status, created_at 
        FROM notifications 
        WHERE recipient_id = %s 
        ORDER BY created_at {order_by}
        LIMIT %s OFFSET %s
    """, (buyer_id, per_page, offset))
    
    notifications = cursor.fetchall()

    session['notif_unread_count'] = 0  # Reset unread count since all are now read
    session.modified = True  

    conn.close()

    return render_template('buyer_notifications.html', 
                         notifications=notifications, 
                         sort_by=sort_by,
                         current_page=page,
                         total_pages=total_pages,
                         total_notifications=total_notifications)
    
    
# GET UNREAD NOTIFICATIONS COUNT
def get_unread_notifications_count(buyer_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) FROM notifications 
        WHERE recipient_id = %s AND status = 'Unread'
    """, (buyer_id,))
    
    unread_count = cursor.fetchone()[0]  
    conn.close()
    
    return unread_count  


# MARK SINGLE NOTIFICATION AS READ
@buyer_notifications_bp.route('/buyer/notifications/read/<int:notification_id>', methods=['POST'])
def mark_notification_as_read(notification_id):
    if 'buyer' not in session:
        flash("You must log in first.", "danger")
        return redirect(url_for('login.login'))
    
    buyer_id = session.get('buyer')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE notifications 
        SET status = 'Read' 
        WHERE notification_id = %s AND recipient_id = %s
    """, (notification_id, buyer_id))
    
    conn.commit()
    conn.close()

    return redirect(url_for('buyer_notifications.notifications'))


# MARK ALL NOTIFICATIONS AS READ
@buyer_notifications_bp.route('/buyer/notifications/read_all', methods=['POST'])
def mark_all_notifications_as_read():
    if 'buyer' not in session:
        flash("You must log in first.", "danger")
        return redirect(url_for('login.login'))
    
    buyer_id = session.get('buyer')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE notifications 
        SET status = 'Read' 
        WHERE recipient_id = %s AND status = 'Unread'
    """, (buyer_id,))
    
    conn.commit()
    conn.close()

    return redirect(url_for('buyer_notifications.notifications'))


# GET NOTIFICATION COUNT
@buyer_notifications_bp.route('/buyer/notifications/count')
def get_notification_count():
    if 'buyer' not in session:
        return jsonify({'count': 0})
    
    buyer_id = session.get('buyer')
    count = get_unread_notifications_count(buyer_id)
    return jsonify({'count': count})
