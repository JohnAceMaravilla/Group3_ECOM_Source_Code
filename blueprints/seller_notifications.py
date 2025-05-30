from flask import Blueprint, render_template, flash, session, redirect, url_for, request, jsonify
from db_connection import get_db_connection  

seller_notifications_bp = Blueprint('seller_notifications', __name__)

# SELLER NOTIFICATIONS LIST
@seller_notifications_bp.route('/seller/notifications')
def notifications():
    if 'seller' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Seller':
        flash("Unauthorized access. Sellers only.", "danger")
        return redirect(url_for('login.login'))
    
    seller_id = session.get('seller') 
    
    if not seller_id:
        flash("Invalid session. Please log in again.", "danger")
        return redirect(url_for('login.login'))

    sort_by = request.args.get('sort_by', 'recent')  
    order_by = "DESC" if sort_by == "recent" else "ASC"

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  

    # Fetch all notifications
    cursor.execute(f"""
        SELECT notification_id, notification_type, notification_title, content, status, created_at 
        FROM notifications 
        WHERE recipient_id = %s 
        ORDER BY created_at {order_by}
    """, (seller_id,))
    
    notifications = cursor.fetchall()
    conn.close()

    return render_template('seller_notifications.html', notifications=notifications, sort_by=sort_by)
    
    
# GET UNREAD NOTIFICATIONS COUNT
def get_unread_notifications_count(seller_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) FROM notifications 
        WHERE recipient_id = %s AND status = 'Unread'
    """, (seller_id,))
    
    unread_count = cursor.fetchone()[0]  
    conn.close()
    
    return unread_count  


# GET NOTIFICATION COUNT
@seller_notifications_bp.route('/seller/notifications/count')
def get_notification_count():
    if 'seller' not in session:
        return jsonify({'count': 0})
    
    seller_id = session.get('seller')
    count = get_unread_notifications_count(seller_id)
    return jsonify({'count': count})


# MARK SINGLE NOTIFICATION AS READ
@seller_notifications_bp.route('/seller/notifications/read/<int:notification_id>', methods=['POST'])
def mark_notification_as_read(notification_id):
    if 'seller' not in session:
        flash("You must log in first.", "danger")
        return redirect(url_for('login.login'))
    
    seller_id = session.get('seller')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE notifications 
        SET status = 'Read' 
        WHERE notification_id = %s AND recipient_id = %s
    """, (notification_id, seller_id))
    
    conn.commit()
    conn.close()

    return redirect(url_for('seller_notifications.notifications'))


# MARK ALL NOTIFICATIONS AS READ
@seller_notifications_bp.route('/seller/notifications/read_all', methods=['POST'])
def mark_all_notifications_as_read():
    if 'seller' not in session:
        flash("You must log in first.", "danger")
        return redirect(url_for('login.login'))
    
    seller_id = session.get('seller')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE notifications 
        SET status = 'Read' 
        WHERE recipient_id = %s AND status = 'Unread'
    """, (seller_id,))
    
    conn.commit()
    conn.close()

    return redirect(url_for('seller_notifications.notifications'))
