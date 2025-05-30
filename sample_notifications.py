#!/usr/bin/env python3
"""
Sample script to add test notifications to the database
Run this script to create sample notifications for testing the mobile app
"""

from db_connection import get_db_connection
from datetime import datetime, timedelta

def add_sample_notifications():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get a sample buyer ID (you may need to adjust this based on your database)
    cursor.execute("SELECT user_id FROM user_account WHERE user_role = 'Buyer' LIMIT 1")
    result = cursor.fetchone()
    
    if not result:
        print("No buyer found in database. Please register a buyer first.")
        conn.close()
        return
    
    buyer_id = result[0]
    print(f"Adding sample notifications for buyer ID: {buyer_id}")
    
    # Sample notifications data
    notifications = [
        {
            'notification_type': 'Order Update',
            'notification_title': 'Order Approved',
            'content': 'Your order for Vivo Y100 has been approved and is now being prepared for packing.',
            'created_at': datetime.now() - timedelta(minutes=6)
        },
        {
            'notification_type': 'Order Confirmation',
            'notification_title': 'Order Placed Successfully',
            'content': 'Your order has been placed successfully. Orders will be processed soon.',
            'created_at': datetime.now() - timedelta(minutes=7)
        },
        {
            'notification_type': 'Payment Complete',
            'notification_title': 'Order Delivered & Payment Confirmed',
            'content': 'Your order #17 for Tecno Spark 20 Pro has been successfully delivered and payment has been confirmed. Thank you for your purchase!',
            'created_at': datetime.now() - timedelta(minutes=13)
        },
        {
            'notification_type': 'Delivery Update',
            'notification_title': 'Order Out for Delivery',
            'content': 'Great news! Your order #17 for Tecno Spark 20 Pro is now out for delivery with courier.',
            'created_at': datetime.now() - timedelta(minutes=13)
        },
        {
            'notification_type': 'Delivery Update',
            'notification_title': 'Courier Assigned',
            'content': 'A courier has been assigned to your order. You will receive updates on the delivery progress.',
            'created_at': datetime.now() - timedelta(minutes=15)
        },
        {
            'notification_type': 'Promotion',
            'notification_title': 'Special Discount Available',
            'content': 'Don\'t miss out! Get 20% off on all laptop accessories. Limited time offer!',
            'created_at': datetime.now() - timedelta(hours=2)
        },
        {
            'notification_type': 'Order Update',
            'notification_title': 'Order Shipped',
            'content': 'Your order has been shipped and is on its way to you. Track your package for real-time updates.',
            'created_at': datetime.now() - timedelta(hours=4)
        },
        {
            'notification_type': 'New Review',
            'notification_title': 'Please Rate Your Purchase',
            'content': 'How was your experience with the Tecno Spark 20 Pro? Please leave a review to help other customers.',
            'created_at': datetime.now() - timedelta(days=1)
        }
    ]
    
    # Insert notifications
    for notification in notifications:
        cursor.execute("""
            INSERT INTO notifications 
            (recipient_id, notification_type, notification_title, content, status, created_at)
            VALUES (%s, %s, %s, %s, 'Unread', %s)
        """, (
            buyer_id,
            notification['notification_type'],
            notification['notification_title'],
            notification['content'],
            notification['created_at']
        ))
    
    conn.commit()
    print(f"Successfully added {len(notifications)} sample notifications!")
    
    # Show the added notifications
    cursor.execute("""
        SELECT notification_type, notification_title, created_at 
        FROM notifications 
        WHERE recipient_id = %s 
        ORDER BY created_at DESC
    """, (buyer_id,))
    
    results = cursor.fetchall()
    print("\nAdded notifications:")
    for i, (ntype, title, created) in enumerate(results, 1):
        print(f"{i}. [{ntype}] {title} - {created}")
    
    conn.close()

if __name__ == "__main__":
    add_sample_notifications() 