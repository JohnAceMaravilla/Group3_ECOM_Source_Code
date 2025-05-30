from flask import Blueprint, render_template, flash, session, redirect, url_for, request, jsonify
from db_connection import get_db_connection  

admin_notifications_bp = Blueprint('admin_notifications', __name__)

# ADMIN NOTIFICATIONS
@admin_notifications_bp.route('/admin/notifications')
def notifications():
    if 'admin' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Admin':
        flash("Unauthorized access. Admins only.", "danger")
        return redirect(url_for('login.login'))
    
    admin_id = session.get('admin') 
    
    if not admin_id:
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
    """, (admin_id,))
    
    notifications = cursor.fetchall()
    conn.close()

    return render_template('admin_notifications.html', notifications=notifications, sort_by=sort_by)


# COUNT UNREAD NOTIFICATIONS
def get_unread_notifications_count(admin_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) FROM notifications 
        WHERE recipient_id = %s AND status = 'Unread'
    """, (admin_id,))
    
    unread_count = cursor.fetchone()[0]
    conn.close()
    
    return unread_count


# GET NOTIFICATION COUNT
@admin_notifications_bp.route('/admin/notifications/count')
def get_notification_count():
    if 'admin' not in session:
        return jsonify({'count': 0})
    
    admin_id = session.get('admin')
    count = get_unread_notifications_count(admin_id)
    return jsonify({'count': count})


# MARK NOTIFICATION AS READ
@admin_notifications_bp.route('/admin/notifications/read/<int:notification_id>', methods=['POST'])
def mark_notification_as_read(notification_id):
    if 'admin' not in session:
        flash("You must log in first.", "danger")
        return redirect(url_for('login.login'))
    
    admin_id = session.get('admin')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE notifications 
        SET status = 'Read' 
        WHERE notification_id = %s AND recipient_id = %s
    """, (notification_id, admin_id))
    
    conn.commit()
    conn.close()

    return redirect(url_for('admin_notifications.notifications'))


# MARK ALL NOTIFICATIONS AS READ
@admin_notifications_bp.route('/admin/notifications/read_all', methods=['POST'])
def mark_all_notifications_as_read():
    if 'admin' not in session:
        flash("You must log in first.", "danger")
        return redirect(url_for('login.login'))
    
    admin_id = session.get('admin')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE notifications 
        SET status = 'Read' 
        WHERE recipient_id = %s AND status = 'Unread'
    """, (admin_id,))
    
    conn.commit()
    conn.close()

    return redirect(url_for('admin_notifications.notifications'))
