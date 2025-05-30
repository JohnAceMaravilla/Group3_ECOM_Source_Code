import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

class UserSession {
  static const String _keyIsLoggedIn = 'is_logged_in';
  static const String _keyUserData = 'user_data';
  static const String _keyUserType = 'user_type';
  static const String _keyUserId = 'user_id';
  static const String _keyUserRole = 'user_role';
  static const String _keyUserStatus = 'user_status';
  static const String _keyToken = 'auth_token';

  // Save user login session
  static Future<void> saveUserSession({
    required String userId,
    required String userType,
    required Map<String, dynamic> profileData,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    
    await prefs.setBool(_keyIsLoggedIn, true);
    await prefs.setString(_keyUserType, userType);
    
    final userData = {
      'user_id': userId,
      'user_type': userType,
      'profile': profileData,
      'login_time': DateTime.now().toIso8601String(),
    };
    
    await prefs.setString(_keyUserData, json.encode(userData));
  }

  // Get current user data
  static Future<Map<String, dynamic>?> getUserData() async {
    final prefs = await SharedPreferences.getInstance();
    final userDataString = prefs.getString(_keyUserData);
    
    if (userDataString != null) {
      return json.decode(userDataString);
    }
    
    return null;
  }

  // Check if user is logged in
  static Future<bool> isLoggedIn() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getBool(_keyIsLoggedIn) ?? false;
  }

  // Get user type (buyer or courier)
  static Future<String?> getUserType() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_keyUserType);
  }

  // Get user ID
  static Future<String?> getUserId() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_keyUserId);
  }

  // Get user role
  static Future<String?> getUserRole() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_keyUserRole);
  }

  // Get user status
  static Future<String?> getUserStatus() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_keyUserStatus);
  }

  // Get auth token
  static Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_keyToken);
  }

  // Clear user session (logout)
  static Future<void> clearSession() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_keyIsLoggedIn);
    await prefs.remove(_keyUserData);
    await prefs.remove(_keyUserType);
    await prefs.remove(_keyUserId);
    await prefs.remove(_keyUserRole);
    await prefs.remove(_keyUserStatus);
    await prefs.remove(_keyToken);
  }

  // Update user profile data
  static Future<void> updateUserProfile(Map<String, dynamic> newProfileData) async {
    final currentData = await getUserData();
    if (currentData != null) {
      currentData['profile'] = newProfileData;
      
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_keyUserData, json.encode(currentData));
    }
  }
} 