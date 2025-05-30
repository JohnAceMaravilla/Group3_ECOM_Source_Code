from flask import Blueprint, render_template, flash, session, redirect, url_for, request, jsonify
from db_connection import get_db_connection  

courier_notifications_bp = Blueprint('courier_notifications', __name__)

# COURIER NOTIFICATIONS LIST
@courier_notifications_bp.route('/courier/notifications')
def notifications():
    if 'courier' not in session:
        flash("You must log in first.", "danger")
        return redirect(url_for('login.login'))
    
    courier_id = session.get('courier') 
    
    if not courier_id:
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
    """, (courier_id,))
    
    notifications = cursor.fetchall()
    conn.close()

    return render_template('courier_notifications.html', notifications=notifications, sort_by=sort_by)


# GET UNREAD NOTIFICATIONS COUNT
def get_unread_notifications_count(courier_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) FROM notifications 
        WHERE recipient_id = %s AND status = 'Unread'
    """, (courier_id,))
    
    unread_count = cursor.fetchone()[0]  
    conn.close()
    
    return unread_count  


# GET NOTIFICATION COUNT
@courier_notifications_bp.route('/courier/notifications/count')
def get_notification_count():
    if 'courier' not in session:
        return jsonify({'count': 0})
    
    courier_id = session.get('courier')
    count = get_unread_notifications_count(courier_id)
    return jsonify({'count': count})


# MARK SINGLE NOTIFICATION AS READ
@courier_notifications_bp.route('/courier/notifications/read/<int:notification_id>', methods=['POST'])
def mark_notification_as_read(notification_id):
    if 'courier' not in session:
        flash("You must log in first.", "danger")
        return redirect(url_for('login.login'))
    
    courier_id = session.get('courier')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE notifications 
        SET status = 'Read' 
        WHERE notification_id = %s AND recipient_id = %s
    """, (notification_id, courier_id))
    
    conn.commit()
    conn.close()

    return redirect(url_for('courier_notifications.notifications'))


# MARK ALL NOTIFICATIONS AS READ
@courier_notifications_bp.route('/courier/notifications/read_all', methods=['POST'])
def mark_all_notifications_as_read():
    if 'courier' not in session:
        flash("You must log in first.", "danger")
        return redirect(url_for('login.login'))
    
    courier_id = session.get('courier')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE notifications 
        SET status = 'Read' 
        WHERE recipient_id = %s AND status = 'Unread'
    """, (courier_id,))
    
    conn.commit()
    conn.close()

    return redirect(url_for('courier_notifications.notifications'))
