import 'dart:convert';
import 'package:http/http.dart' as http;

class NotificationService {
  static const String baseUrl = 'http://192.168.1.3:5000';

  static Future<Map<String, dynamic>> getNotifications({
    required int buyerId,
    int page = 1,
    int perPage = 10,
    String sortBy = 'recent',
  }) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/buyer/notifications?buyer_id=$buyerId&page=$page&per_page=$perPage&sort_by=$sortBy'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        return {
          'success': false,
          'message': 'Failed to fetch notifications',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Network error: $e',
      };
    }
  }

  static Future<Map<String, dynamic>> markNotificationsAsRead({
    required int buyerId,
    List<int>? notificationIds, // If null, marks all as read
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/buyer/notifications/mark-read'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'buyer_id': buyerId,
          'notification_ids': notificationIds ?? [],
        }),
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        return {
          'success': false,
          'message': 'Failed to mark notifications as read',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Network error: $e',
      };
    }
  }

  static Future<Map<String, dynamic>> getUnreadCount({
    required int buyerId,
  }) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/buyer/notifications/unread-count?buyer_id=$buyerId'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        return {
          'success': false,
          'message': 'Failed to fetch unread count',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Network error: $e',
      };
    }
  }
} 