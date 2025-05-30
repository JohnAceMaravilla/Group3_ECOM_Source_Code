#!/usr/bin/env python3
"""
Test script to verify notifications API is working correctly
"""

import requests
import json

def test_notification_api():
    base_url = 'http://192.168.1.3:5000'
    buyer_id = 2  # Adjust this to match your test buyer ID
    
    print("🧪 Testing Notifications API...")
    print(f"Base URL: {base_url}")
    print(f"Buyer ID: {buyer_id}")
    print("-" * 50)
    
    # Test 1: Get unread count
    print("1️⃣ Testing unread count...")
    try:
        response = requests.get(f'{base_url}/api/buyer/notifications/unread-count?buyer_id={buyer_id}')
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                count = data['data']['unread_count']
                print(f"✅ Unread count: {count}")
            else:
                print(f"❌ API Error: {data['message']}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Request Error: {e}")
    
    print()
    
    # Test 2: Get notifications list
    print("2️⃣ Testing notifications list...")
    try:
        response = requests.get(f'{base_url}/api/buyer/notifications?buyer_id={buyer_id}&page=1&per_page=3&sort_by=recent')
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                notifications = data['data']['notifications']
                pagination = data['data']['pagination']
                print(f"✅ Found {len(notifications)} notifications")
                print(f"✅ Total notifications: {pagination['total_notifications']}")
                print("Recent notifications:")
                for i, notif in enumerate(notifications[:3], 1):
                    print(f"   {i}. [{notif['notification_type']}] {notif['notification_title']} - {notif['time_ago']}")
            else:
                print(f"❌ API Error: {data['message']}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Request Error: {e}")
    
    print()
    
    # Test 3: Mark as read
    print("3️⃣ Testing mark as read...")
    try:
        payload = {
            'buyer_id': buyer_id,
            'notification_ids': []  # Empty array marks all as read
        }
        response = requests.post(
            f'{base_url}/api/buyer/notifications/mark-read',
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload)
        )
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"✅ {data['message']}")
            else:
                print(f"❌ API Error: {data['message']}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Request Error: {e}")
    
    print()
    
    # Test 4: Check unread count after marking as read
    print("4️⃣ Testing unread count after marking as read...")
    try:
        response = requests.get(f'{base_url}/api/buyer/notifications/unread-count?buyer_id={buyer_id}')
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                count = data['data']['unread_count']
                print(f"✅ Unread count after marking as read: {count}")
            else:
                print(f"❌ API Error: {data['message']}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Request Error: {e}")
    
    print()
    print("🎯 API Testing Complete!")

if __name__ == "__main__":
    test_notification_api() 