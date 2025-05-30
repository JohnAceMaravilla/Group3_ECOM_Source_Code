import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  // Multiple URLs to try for different environments
  // Phone IP: 192.168.1.2, Laptop IP: 192.168.1.3
  static const List<String> baseUrls = [
    'http://192.168.1.3:5000/api/mobile',   // Your laptop's IP (PRIORITY for phone connection)
    'http://10.0.2.2:5000/api/mobile',      // Android Emulator
    'http://localhost:5000/api/mobile',      // iOS Simulator / Desktop
    'http://127.0.0.1:5000/api/mobile',     // Alternative localhost
  ];

  // Health check to test connection with multiple URLs
  static Future<Map<String, dynamic>> healthCheck() async {
    String? lastError;
    
    for (String baseUrl in baseUrls) {
      try {
        print('🔄 Trying to connect to: $baseUrl/health');
        
        final response = await http.get(
          Uri.parse('$baseUrl/health'),
          headers: {'Content-Type': 'application/json'},
        ).timeout(
          const Duration(seconds: 8), // Increased timeout
          onTimeout: () {
            throw Exception('Connection timeout after 8 seconds');
          },
        );

        if (response.statusCode == 200) {
          print('✅ SUCCESS! Connected to: $baseUrl');
          print('📱 Response: ${response.body}');
          return json.decode(response.body);
        } else {
          lastError = 'HTTP ${response.statusCode}: ${response.body}';
          print('❌ Failed with status ${response.statusCode}: $baseUrl');
        }
      } catch (e) {
        lastError = 'Network error: $e';
        print('❌ Failed to connect to $baseUrl: $e');
        continue;
      }
    }
    
    throw Exception('❌ Failed to connect to any server. Last error: $lastError');
  }

  // Get the working base URL
  static Future<String> _getWorkingBaseUrl() async {
    for (String baseUrl in baseUrls) {
      try {
        final response = await http.get(
          Uri.parse('$baseUrl/health'),
          headers: {'Content-Type': 'application/json'},
        ).timeout(const Duration(seconds: 3));

        if (response.statusCode == 200) {
          return baseUrl;
        }
      } catch (e) {
        continue;
      }
    }
    throw Exception('No working server found');
  }

  // Login endpoint
  static Future<Map<String, dynamic>> login(String email, String password) async {
    try {
      final baseUrl = await _getWorkingBaseUrl();
      final response = await http.post(
        Uri.parse('$baseUrl/auth/login'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'email': email,
          'password': password,
        }),
      );

      return json.decode(response.body);
    } catch (e) {
      throw Exception('Login error: $e');
    }
  }

  // Get user profile
  static Future<Map<String, dynamic>> getUserProfile() async {
    try {
      final baseUrl = await _getWorkingBaseUrl();
      final response = await http.get(
        Uri.parse('$baseUrl/user/profile'),
        headers: {'Content-Type': 'application/json'},
      );

      return json.decode(response.body);
    } catch (e) {
      throw Exception('Profile error: $e');
    }
  }

  // Get products
  static Future<Map<String, dynamic>> getProducts() async {
    try {
      final baseUrl = await _getWorkingBaseUrl();
      final response = await http.get(
        Uri.parse('$baseUrl/products'),
        headers: {'Content-Type': 'application/json'},
      );

      return json.decode(response.body);
    } catch (e) {
      throw Exception('Products error: $e');
    }
  }
} 