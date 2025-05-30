import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import 'dart:math';

class AuthService {
  static const String baseUrl = 'http://192.168.1.3:5000/api/mobile';
  static String? _forgotPasswordToken; // Store token for forgot password flow

  static Future<Map<String, dynamic>> login(String username, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/login'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'username': username,
          'password': password,
        }),
      ).timeout(const Duration(seconds: 10));

      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200 && data['status'] == 'success') {
        // Convert response format for mobile app compatibility
        return {
          'success': true,
          'message': data['message'],
          'user': {
            'user_id': data['data']['user_id'],
            'user_role': data['data']['user_type'] == 'buyer' ? 'Buyer' : 'Courier',
            'status': data['data']['status'],
            'profile': data['data']['profile'],
          }
        };
      } else {
        return {
          'success': false,
          'message': data['message'] ?? 'Login failed',
        };
      }
    } catch (e) {
      print('Login error: $e');
      return {
        'success': false,
        'message': 'Connection error. Please check your network and try again.',
      };
    }
  }

  static Future<Map<String, dynamic>> sendRegistrationOTP(
    String userType, 
    Map<String, dynamic> userData,
    File? idPicture
  ) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/send-otp/$userType'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode(userData),
      ).timeout(const Duration(seconds: 10));

      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200 && data['status'] == 'success') {
        return {
          'status': 'success',
          'message': data['message'],
          'otp': data['otp'], // For development - remove in production
        };
      } else {
        return {
          'status': 'error',
          'message': data['message'] ?? 'Failed to send OTP',
        };
      }
    } catch (e) {
      print('Send OTP error: $e');
      return {
        'status': 'error',
        'message': 'Connection error. Please check your network and try again.',
      };
    }
  }

  static Future<Map<String, dynamic>> register(
    String userType, 
    Map<String, dynamic> userData,
    File? idPicture
  ) async {
    try {
      var request = http.MultipartRequest(
        'POST',
        Uri.parse('$baseUrl/auth/register/$userType'),
      );

      // Add text fields
      userData.forEach((key, value) {
        if (key != 'otp') { // Don't include OTP in the final registration
          request.fields[key] = value.toString();
        }
      });

      // Add file if provided
      if (idPicture != null) {
        var stream = http.ByteStream(idPicture.openRead());
        var length = await idPicture.length();
        var multipartFile = http.MultipartFile(
          'id_pic',
          stream,
          length,
          filename: 'id_picture.jpg',
          contentType: MediaType('image', 'jpeg'),
        );
        request.files.add(multipartFile);
      }

      final streamedResponse = await request.send().timeout(const Duration(seconds: 30));
      final response = await http.Response.fromStream(streamedResponse);
      final data = jsonDecode(response.body);

      if (response.statusCode == 201 && data['status'] == 'success') {
        return {
          'status': 'success',
          'message': data['message'],
          'data': data['data'],
        };
      } else {
        return {
          'status': 'error',
          'message': data['message'] ?? 'Registration failed',
        };
      }
    } catch (e) {
      print('Registration error: $e');
      return {
        'status': 'error',
        'message': 'Connection error. Please check your network and try again.',
      };
    }
  }

  static Future<Map<String, dynamic>> validateRegistrationData(Map<String, dynamic> userData) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/register/validate'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(userData),
      );

      return json.decode(response.body);
    } catch (e) {
      print('Validation error: $e');
      return {
        'status': 'error',
        'message': 'Connection error. Please check your internet connection.',
      };
    }
  }

  static Future<Map<String, dynamic>> forgotPassword(String email) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/forgot-password'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'email': email,
        }),
      ).timeout(const Duration(seconds: 10));

      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200 && data['status'] == 'success') {
        // Store the token for subsequent requests
        _forgotPasswordToken = data['token'];
        
        return {
          'status': 'success',
          'message': data['message'],
          'otp': data['otp'], // For development - remove in production
        };
      } else {
        return {
          'status': 'error',
          'message': data['message'] ?? 'Failed to send reset OTP',
        };
      }
    } catch (e) {
      print('Forgot password error: $e');
      return {
        'status': 'error',
        'message': 'Connection error. Please check your network and try again.',
      };
    }
  }

  static Future<Map<String, dynamic>> verifyForgotOTP(String otp) async {
    try {
      if (_forgotPasswordToken == null) {
        return {
          'status': 'error',
          'message': 'Session expired. Please request OTP again.',
        };
      }

      final response = await http.post(
        Uri.parse('$baseUrl/auth/verify-forgot-otp'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'otp': otp,
          'token': _forgotPasswordToken,
        }),
      ).timeout(const Duration(seconds: 10));

      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200 && data['status'] == 'success') {
        // Update token if a new one is returned
        if (data['token'] != null) {
          _forgotPasswordToken = data['token'];
        }
        
        return {
          'status': 'success',
          'message': data['message'],
        };
      } else {
        return {
          'status': 'error',
          'message': data['message'] ?? 'Invalid OTP',
        };
      }
    } catch (e) {
      print('Verify forgot OTP error: $e');
      return {
        'status': 'error',
        'message': 'Connection error. Please check your network and try again.',
      };
    }
  }

  static Future<Map<String, dynamic>> resetPassword(String newPassword, String confirmPassword) async {
    try {
      if (_forgotPasswordToken == null) {
        return {
          'status': 'error',
          'message': 'Session expired. Please request OTP again.',
        };
      }

      final response = await http.post(
        Uri.parse('$baseUrl/auth/reset-password'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'new_password': newPassword,
          'confirm_password': confirmPassword,
          'token': _forgotPasswordToken,
        }),
      ).timeout(const Duration(seconds: 10));

      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200 && data['status'] == 'success') {
        // Clear token after successful password reset
        _forgotPasswordToken = null;
        
        return {
          'status': 'success',
          'message': data['message'],
        };
      } else {
        return {
          'status': 'error',
          'message': data['message'] ?? 'Failed to reset password',
        };
      }
    } catch (e) {
      print('Reset password error: $e');
      return {
        'status': 'error',
        'message': 'Connection error. Please check your network and try again.',
      };
    }
  }

  static Future<Map<String, dynamic>> resendForgotOTP() async {
    try {
      if (_forgotPasswordToken == null) {
        return {
          'status': 'error',
          'message': 'Session expired. Please request OTP again.',
        };
      }

      final response = await http.post(
        Uri.parse('$baseUrl/auth/resend-forgot-otp'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'token': _forgotPasswordToken,
        }),
      ).timeout(const Duration(seconds: 10));

      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200 && data['status'] == 'success') {
        return {
          'status': 'success',
          'message': data['message'],
          'otp': data['otp'], // For development - remove in production
        };
      } else {
        return {
          'status': 'error',
          'message': data['message'] ?? 'Failed to resend OTP',
        };
      }
    } catch (e) {
      print('Resend forgot OTP error: $e');
      return {
        'status': 'error',
        'message': 'Connection error. Please check your network and try again.',
      };
    }
  }

  // Method to clear forgot password token if needed
  static void clearForgotPasswordToken() {
    _forgotPasswordToken = null;
  }

  // Get the working base URL
  static Future<String> _getWorkingBaseUrl() async {
    const List<String> baseUrls = [
      'http://192.168.1.3:5000/api/mobile',   // Your laptop's IP (update this to your actual IP)
      'http://127.0.0.1:5000/api/mobile',     // Localhost
      'http://localhost:5000/api/mobile',     // Alternative localhost
      'http://10.0.2.2:5000/api/mobile',     // Android Emulator
    ];

    for (String baseUrl in baseUrls) {
      try {
        print('Trying to connect to: $baseUrl');
        final response = await http.get(
          Uri.parse('$baseUrl/health'),
          headers: {'Content-Type': 'application/json'},
        ).timeout(const Duration(seconds: 5));

        print('Response from $baseUrl: ${response.statusCode}');
        if (response.statusCode == 200) {
          print('Successfully connected to: $baseUrl');
          return baseUrl;
        }
      } catch (e) {
        print('Failed to connect to $baseUrl: $e');
        continue;
      }
    }
    throw Exception('No working server found. Make sure your Flask server is running.');
  }
} 