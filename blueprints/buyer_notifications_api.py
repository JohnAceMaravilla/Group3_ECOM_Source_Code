from flask import Blueprint, request, jsonify
from db_connection import get_db_connection
import datetime

buyer_notifications_api_bp = Blueprint('buyer_notifications_api', __name__)

# GET BUYER NOTIFICATIONS (Mobile API)
@buyer_notifications_api_bp.route('/api/buyer/notifications', methods=['GET'])
def get_notifications():
    try:
        buyer_id = request.args.get('buyer_id', type=int)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        sort_by = request.args.get('sort_by', 'recent')  # 'recent' or 'oldest'
        
        if not buyer_id:
            return jsonify({
                'success': False,
                'message': 'Buyer ID is required'
            }), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Calculate offset for pagination
        offset = (page - 1) * per_page
        order_by = "DESC" if sort_by == "recent" else "ASC"

        # Get total count of notifications
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM notifications 
            WHERE recipient_id = %s
        """, (buyer_id,))
        
        total_notifications = cursor.fetchone()['total']
        total_pages = (total_notifications + per_page - 1) // per_page

        # Get notifications with pagination
        cursor.execute(f"""
            SELECT notification_id, notification_type, notification_title, 
                   content, status, created_at 
            FROM notifications 
            WHERE recipient_id = %s 
            ORDER BY created_at {order_by}
            LIMIT %s OFFSET %s
        """, (buyer_id, per_page, offset))
        
        notifications = cursor.fetchall()
        
        # Format the notifications for mobile response
        formatted_notifications = []
        for notification in notifications:
            # Calculate time ago
            time_diff = datetime.datetime.now() - notification['created_at']
            if time_diff.days > 0:
                time_ago = f"{time_diff.days}d ago"
            elif time_diff.seconds >= 3600:
                hours = time_diff.seconds // 3600
                time_ago = f"{hours}h ago"
            elif time_diff.seconds >= 60:
                minutes = time_diff.seconds // 60
                time_ago = f"{minutes}m ago"
            else:
                time_ago = "Just now"
            
            formatted_notifications.append({
                'notification_id': notification['notification_id'],
                'notification_type': notification['notification_type'],
                'notification_title': notification['notification_title'],
                'content': notification['content'],
                'status': notification['status'],
                'created_at': notification['created_at'].isoformat(),
                'time_ago': time_ago
            })

        conn.close()

        return jsonify({
            'success': True,
            'data': {
                'notifications': formatted_notifications,
                'pagination': {
                    'current_page': page,
                    'total_pages': total_pages,
                    'total_notifications': total_notifications,
                    'per_page': per_page
                }
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching notifications: {str(e)}'
        }), 500


# MARK NOTIFICATIONS AS READ (Mobile API)
@buyer_notifications_api_bp.route('/api/buyer/notifications/mark-read', methods=['POST'])
def mark_notifications_read():
    try:
        data = request.get_json()
        buyer_id = data.get('buyer_id')
        notification_ids = data.get('notification_ids', [])  # List of IDs to mark as read, empty means all
        
        if not buyer_id:
            return jsonify({
                'success': False,
                'message': 'Buyer ID is required'
            }), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        
        if notification_ids:
            # Mark specific notifications as read
            placeholders = ','.join(['%s'] * len(notification_ids))
            cursor.execute(f"""
                UPDATE notifications 
                SET status = 'Read' 
                WHERE notification_id IN ({placeholders}) AND recipient_id = %s
            """, notification_ids + [buyer_id])
        else:
            # Mark all notifications as read
            cursor.execute("""
                UPDATE notifications 
                SET status = 'Read' 
                WHERE recipient_id = %s AND status = 'Unread'
            """, (buyer_id,))
        
        affected_rows = cursor.rowcount
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': f'Marked {affected_rows} notifications as read'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error marking notifications as read: {str(e)}'
        }), 500


# GET UNREAD NOTIFICATIONS COUNT (Mobile API)
@buyer_notifications_api_bp.route('/api/buyer/notifications/unread-count', methods=['GET'])
def get_unread_count():
    try:
        buyer_id = request.args.get('buyer_id', type=int)
        
        if not buyer_id:
            return jsonify({
                'success': False,
                'message': 'Buyer ID is required'
            }), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*) as count
            FROM notifications 
            WHERE recipient_id = %s AND status = 'Unread'
        """, (buyer_id,))
        
        result = cursor.fetchone()
        unread_count = result[0] if result else 0
        
        conn.close()

        return jsonify({
            'success': True,
            'data': {
                'unread_count': unread_count
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching unread count: {str(e)}'
        }), 500
