import 'dart:convert';
import 'package:http/http.dart' as http;

class BuyerService {
  static const String baseUrl = 'http://192.168.1.3:5000/api/mobile/buyer';

  static Future<Map<String, dynamic>> getHomepageData({int? userId}) async {
    try {
      String url = '$baseUrl/homepage';
      if (userId != null) {
        url += '?user_id=$userId';
      }

      final response = await http.get(
        Uri.parse(url),
        headers: {
          'Content-Type': 'application/json',
        },
      ).timeout(const Duration(seconds: 15));

      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200 && data['status'] == 'success') {
        return {
          'success': true,
          'data': data['data'],
        };
      } else {
        return {
          'success': false,
          'message': data['message'] ?? 'Failed to load homepage data',
        };
      }
    } catch (e) {
      print('Homepage data error: $e');
      return {
        'success': false,
        'message': 'Connection error. Please check your internet connection.',
      };
    }
  }

  static Future<Map<String, dynamic>> getMostReviewed({int? userId, int limit = 8}) async {
    try {
      String url = '$baseUrl/products/most-reviewed?limit=$limit';
      if (userId != null) {
        url += '&user_id=$userId';
      }

      final response = await http.get(
        Uri.parse(url),
        headers: {
          'Content-Type': 'application/json',
        },
      ).timeout(const Duration(seconds: 10));

      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200 && data['status'] == 'success') {
        return {
          'success': true,
          'data': data['data'],
        };
      } else {
        return {
          'success': false,
          'message': data['message'] ?? 'Failed to load most reviewed products',
        };
      }
    } catch (e) {
      print('Most reviewed products error: $e');
      return {
        'success': false,
        'message': 'Connection error. Please check your internet connection.',
      };
    }
  }

  static Future<Map<String, dynamic>> getBestSellers({int? userId, int limit = 8}) async {
    try {
      String url = '$baseUrl/products/best-sellers?limit=$limit';
      if (userId != null) {
        url += '&user_id=$userId';
      }

      final response = await http.get(
        Uri.parse(url),
        headers: {
          'Content-Type': 'application/json',
        },
      ).timeout(const Duration(seconds: 10));

      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200 && data['status'] == 'success') {
        return {
          'success': true,
          'data': data['data'],
        };
      } else {
        return {
          'success': false,
          'message': data['message'] ?? 'Failed to load best sellers',
        };
      }
    } catch (e) {
      print('Best sellers error: $e');
      return {
        'success': false,
        'message': 'Connection error. Please check your internet connection.',
      };
    }
  }

  static Future<Map<String, dynamic>> getHighestRated({int? userId, int limit = 8}) async {
    try {
      String url = '$baseUrl/products/highest-rated?limit=$limit';
      if (userId != null) {
        url += '&user_id=$userId';
      }

      final response = await http.get(
        Uri.parse(url),
        headers: {
          'Content-Type': 'application/json',
        },
      ).timeout(const Duration(seconds: 10));

      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200 && data['status'] == 'success') {
        return {
          'success': true,
          'data': data['data'],
        };
      } else {
        return {
          'success': false,
          'message': data['message'] ?? 'Failed to load highest rated products',
        };
      }
    } catch (e) {
      print('Highest rated error: $e');
      return {
        'success': false,
        'message': 'Connection error. Please check your internet connection.',
      };
    }
  }

  static Future<Map<String, dynamic>> getCategories() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/categories'),
        headers: {
          'Content-Type': 'application/json',
        },
      ).timeout(const Duration(seconds: 10));

      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200 && data['status'] == 'success') {
        return {
          'success': true,
          'data': data['data'],
        };
      } else {
        return {
          'success': false,
          'message': data['message'] ?? 'Failed to load categories',
        };
      }
    } catch (e) {
      print('Categories error: $e');
      return {
        'success': false,
        'message': 'Connection error. Please check your internet connection.',
      };
    }
  }

  static Future<Map<String, dynamic>> searchProducts({
    String? query,
    String? category,
    int? userId,
    int limit = 20,
  }) async {
    try {
      String url = '$baseUrl/products/search?limit=$limit';
      
      if (query != null && query.isNotEmpty) {
        url += '&q=${Uri.encodeComponent(query)}';
      }
      
      if (category != null && category.isNotEmpty) {
        url += '&category=${Uri.encodeComponent(category)}';
      }
      
      if (userId != null) {
        url += '&user_id=$userId';
      }

      final response = await http.get(
        Uri.parse(url),
        headers: {
          'Content-Type': 'application/json',
        },
      ).timeout(const Duration(seconds: 10));

      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200 && data['status'] == 'success') {
        return {
          'success': true,
          'data': data['data'],
          'count': data['count'],
        };
      } else {
        return {
          'success': false,
          'message': data['message'] ?? 'Search failed',
        };
      }
    } catch (e) {
      print('Search error: $e');
      return {
        'success': false,
        'message': 'Connection error. Please check your internet connection.',
      };
    }
  }

  static Future<Map<String, dynamic>> searchProductsAdvanced({
    String? query,
    String? category,
    int? userId,
    int limit = 20,
    int offset = 0,
    double minPrice = 0,
    double maxPrice = 0,
    String sort = 'recent',
  }) async {
    try {
      String url = '$baseUrl/search?limit=$limit&offset=$offset&sort=$sort';
      
      if (query != null && query.isNotEmpty) {
        url += '&q=${Uri.encodeComponent(query)}';
      }
      
      if (category != null && category.isNotEmpty) {
        url += '&category=${Uri.encodeComponent(category)}';
      }
      
      if (minPrice > 0) {
        url += '&min_price=$minPrice';
      }
      
      if (maxPrice > 0) {
        url += '&max_price=$maxPrice';
      }
      
      if (userId != null) {
        url += '&user_id=$userId';
      }

      final response = await http.get(
        Uri.parse(url),
        headers: {
          'Content-Type': 'application/json',
        },
      ).timeout(const Duration(seconds: 15));

      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200 && data['status'] == 'success') {
        return {
          'success': true,
          'data': data['data'],
          'count': data['count'],
          'query': data['query'],
          'category': data['category'],
        };
      } else {
        return {
          'success': false,
          'message': data['message'] ?? 'Search failed',
        };
      }
    } catch (e) {
      print('Advanced search error: $e');
      return {
        'success': false,
        'message': 'Connection error. Please check your internet connection.',
      };
    }
  }

  static Future<Map<String, dynamic>> getSearchCategories() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/search/categories'),
        headers: {
          'Content-Type': 'application/json',
        },
      ).timeout(const Duration(seconds: 10));

      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200 && data['status'] == 'success') {
        return {
          'success': true,
          'data': data['data'],
        };
      } else {
        return {
          'success': false,
          'message': data['message'] ?? 'Failed to load search categories',
        };
      }
    } catch (e) {
      print('Search categories error: $e');
      return {
        'success': false,
        'message': 'Connection error. Please check your internet connection.',
      };
    }
  }

  static Future<Map<String, dynamic>> toggleProductLike(int productId, int userId) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/products/$productId/like'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'user_id': userId,
        }),
      ).timeout(const Duration(seconds: 10));

      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200 && data['status'] == 'success') {
        return {
          'success': true,
          'data': data['data'],
        };
      } else {
        return {
          'success': false,
          'message': data['message'] ?? 'Failed to toggle like',
        };
      }
    } catch (e) {
      print('Toggle like error: $e');
      return {
        'success': false,
        'message': 'Connection error. Please check your internet connection.',
      };
    }
  }

  static Future<Map<String, dynamic>> getProductsByCategory({
    required String category,
    int? userId,
    int limit = 20,
    int offset = 0,
    double minPrice = 0,
    double maxPrice = 0,
    String sort = 'recent',
  }) async {
    try {
      String url = '$baseUrl/products/category/${Uri.encodeComponent(category)}?limit=$limit&offset=$offset&sort=$sort';
      
      if (minPrice > 0) {
        url += '&min_price=$minPrice';
      }
      
      if (maxPrice > 0) {
        url += '&max_price=$maxPrice';
      }
      
      if (userId != null) {
        url += '&user_id=$userId';
      }

      final response = await http.get(
        Uri.parse(url),
        headers: {
          'Content-Type': 'application/json',
        },
      ).timeout(const Duration(seconds: 15));

      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200 && data['status'] == 'success') {
        return {
          'success': true,
          'data': data['data'],
          'count': data['count'],
          'category': data['category'],
        };
      } else {
        return {
          'success': false,
          'message': data['message'] ?? 'Failed to load category products',
        };
      }
    } catch (e) {
      print('Category products error: $e');
      return {
        'success': false,
        'message': 'Connection error. Please check your internet connection.',
      };
    }
  }

  static Future<Map<String, dynamic>> getProductDetails({
    required int productInfoId,
    int? userId,
  }) async {
    try {
      String url = 'http://192.168.1.3:5000/api/mobile/buyer/product/$productInfoId';
      
      if (userId != null) {
        url += '?user_id=$userId';
      }

      final response = await http.get(
        Uri.parse(url),
        headers: {
          'Content-Type': 'application/json',
        },
      ).timeout(const Duration(seconds: 15));

      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200 && data['status'] == 'success') {
        return {
          'status': 'success',
          'data': data['data'],
        };
      } else {
        return {
          'status': 'error',
          'message': data['message'] ?? 'Failed to load product details',
        };
      }
    } catch (e) {
      print('Product details error: $e');
      return {
        'status': 'error',
        'message': 'Connection error. Please check your internet connection.',
      };
    }
  }

  static Future<Map<String, dynamic>> addToCart({
    required int userId,
    required int productInfoId,
    required String variant,
    required String color,
    required int quantity,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('http://192.168.1.3:5000/api/mobile/buyer/product/add-to-cart'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'user_id': userId,
          'product_info_id': productInfoId,
          'variant': variant,
          'color': color,
          'quantity': quantity,
        }),
      ).timeout(const Duration(seconds: 10));

      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200 && data['status'] == 'success') {
        return {
          'status': 'success',
          'message': data['message'],
        };
      } else {
        return {
          'status': 'error',
          'message': data['message'] ?? 'Failed to add to cart',
        };
      }
    } catch (e) {
      print('Add to cart error: $e');
      return {
        'status': 'error',
        'message': 'Connection error. Please check your internet connection.',
      };
    }
  }

  static Future<Map<String, dynamic>> toggleProductInfoLike(int productInfoId, int userId) async {
    try {
      final response = await http.post(
        Uri.parse('http://192.168.1.3:5000/api/mobile/buyer/product/$productInfoId/like'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'user_id': userId,
        }),
      ).timeout(const Duration(seconds: 10));

      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200 && data['status'] == 'success') {
        return {
          'success': true,
          'data': data['data'],
          'message': data['message'],
        };
      } else {
        return {
          'success': false,
          'message': data['message'] ?? 'Failed to toggle like',
        };
      }
    } catch (e) {
      print('Toggle like error: $e');
      return {
        'success': false,
        'message': 'Connection error. Please check your internet connection.',
      };
    }
  }

  static Future<Map<String, dynamic>> getLikedProducts({
    required int userId,
    String sort = 'recent',
  }) async {
    try {
      final response = await http.get(
        Uri.parse('http://192.168.1.3:5000/api/mobile/buyer/likes?user_id=$userId&sort=$sort'),
        headers: {
          'Content-Type': 'application/json',
        },
      ).timeout(const Duration(seconds: 15));

      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200 && data['status'] == 'success') {
        return {
          'success': true,
          'data': data['data'],
          'count': data['count'],
        };
      } else {
        return {
          'success': false,
          'message': data['message'] ?? 'Failed to load liked products',
        };
      }
    } catch (e) {
      print('Get liked products error: $e');
      return {
        'success': false,
        'message': 'Connection error. Please check your internet connection.',
      };
    }
  }

  static Future<Map<String, dynamic>> removeLikedProduct({
    required int productInfoId,
    required int userId,
  }) async {
    try {
      final response = await http.delete(
        Uri.parse('http://192.168.1.3:5000/api/mobile/buyer/likes/$productInfoId?user_id=$userId'),
        headers: {
          'Content-Type': 'application/json',
        },
      ).timeout(const Duration(seconds: 10));

      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200 && data['status'] == 'success') {
        return {
          'success': true,
          'message': data['message'],
        };
      } else {
        return {
          'success': false,
          'message': data['message'] ?? 'Failed to remove product from likes',
        };
      }
    } catch (e) {
      print('Remove liked product error: $e');
      return {
        'success': false,
        'message': 'Connection error. Please check your internet connection.',
      };
    }
  }

  // CART METHODS
  static Future<Map<String, dynamic>> getCartItems({
    required int userId,
  }) async {
    try {
      final response = await http.get(
        Uri.parse('http://192.168.1.3:5000/api/mobile/buyer/cart?user_id=$userId'),
        headers: {
          'Content-Type': 'application/json',
        },
      ).timeout(const Duration(seconds: 15));

      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200 && data['status'] == 'success') {
        return {
          'success': true,
          'data': data['data'],
        };
      } else {
        return {
          'success': false,
          'message': data['message'] ?? 'Failed to load cart items',
        };
      }
    } catch (e) {
      print('Get cart items error: $e');
      return {
        'success': false,
        'message': 'Connection error. Please check your internet connection.',
      };
    }
  }

  static Future<Map<String, dynamic>> updateCartQuantity({
    required int userId,
    required int cartId,
    required int quantity,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('http://192.168.1.3:5000/api/mobile/buyer/cart/update-quantity'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'user_id': userId,
          'cart_id': cartId,
          'quantity': quantity,
        }),
      ).timeout(const Duration(seconds: 10));

      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200 && data['status'] == 'success') {
        return {
          'success': true,
          'message': data['message'],
        };
      } else {
        return {
          'success': false,
          'message': data['message'] ?? 'Failed to update cart quantity',
        };
      }
    } catch (e) {
      print('Update cart quantity error: $e');
      return {
        'success': false,
        'message': 'Connection error. Please check your internet connection.',
      };
    }
  }

  static Future<Map<String, dynamic>> removeCartItem({
    required int userId,
    required int cartId,
  }) async {
    try {
      final response = await http.delete(
        Uri.parse('http://192.168.1.3:5000/api/mobile/buyer/cart/remove-item'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'user_id': userId,
          'cart_id': cartId,
        }),
      ).timeout(const Duration(seconds: 10));

      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200 && data['status'] == 'success') {
        return {
          'success': true,
          'message': data['message'],
        };
      } else {
        return {
          'success': false,
          'message': data['message'] ?? 'Failed to remove item from cart',
        };
      }
    } catch (e) {
      print('Remove cart item error: $e');
      return {
        'success': false,
        'message': 'Connection error. Please check your internet connection.',
      };
    }
  }

  static Future<Map<String, dynamic>> clearCart({
    required int userId,
  }) async {
    try {
      final response = await http.delete(
        Uri.parse('http://192.168.1.3:5000/api/mobile/buyer/cart/clear'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'user_id': userId,
        }),
      ).timeout(const Duration(seconds: 10));

      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200 && data['status'] == 'success') {
        return {
          'success': true,
          'message': data['message'],
        };
      } else {
        return {
          'success': false,
          'message': data['message'] ?? 'Failed to clear cart',
        };
      }
    } catch (e) {
      print('Clear cart error: $e');
      return {
        'success': false,
        'message': 'Connection error. Please check your internet connection.',
      };
    }
  }

  static Future<Map<String, dynamic>> checkout({
    required int userId,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('http://192.168.1.3:5000/api/mobile/buyer/cart/checkout'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'user_id': userId,
        }),
      ).timeout(const Duration(seconds: 20)); // Longer timeout for checkout

      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200 && data['status'] == 'success') {
        return {
          'success': true,
          'message': data['message'],
          'order_count': data['order_count'],
        };
      } else {
        return {
          'success': false,
          'message': data['message'] ?? 'Checkout failed',
          'errors': data['errors'],
        };
      }
    } catch (e) {
      print('Checkout error: $e');
      return {
        'success': false,
        'message': 'Connection error. Please check your internet connection.',
      };
    }
  }

  static Future<Map<String, dynamic>> getBuyerAddress({
    required int userId,
  }) async {
    try {
      final response = await http.get(
        Uri.parse('http://192.168.1.3:5000/api/mobile/buyer/cart/buyer-address?user_id=$userId'),
        headers: {
          'Content-Type': 'application/json',
        },
      ).timeout(const Duration(seconds: 10));

      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200 && data['status'] == 'success') {
        return {
          'success': true,
          'data': data['data'],
        };
      } else {
        return {
          'success': false,
          'message': data['message'] ?? 'Failed to load buyer address',
        };
      }
    } catch (e) {
      print('Get buyer address error: $e');
      return {
        'success': false,
        'message': 'Connection error. Please check your internet connection.',
      };
    }
  }

  // ORDERS METHODS
  static Future<Map<String, dynamic>> getOrders({
    required int userId,
    String status = 'All',
    String sortBy = 'date_ordered',
    String order = 'desc',
  }) async {
    try {
      String url = 'http://192.168.1.3:5000/api/mobile/buyer/orders?user_id=$userId&status=$status&sort_by=$sortBy&order=$order';

      final response = await http.get(
        Uri.parse(url),
        headers: {
          'Content-Type': 'application/json',
        },
      ).timeout(const Duration(seconds: 15));

      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200 && data['status'] == 'success') {
        return {
          'success': true,
          'data': data['data'],
          'count': data['count'],
        };
      } else {
        return {
          'success': false,
          'message': data['message'] ?? 'Failed to load orders',
        };
      }
    } catch (e) {
      print('Get orders error: $e');
      return {
        'success': false,
        'message': 'Connection error. Please check your internet connection.',
      };
    }
  }

  static Future<Map<String, dynamic>> getOrderStatistics({
    required int userId,
  }) async {
    try {
      final response = await http.get(
        Uri.parse('http://192.168.1.3:5000/api/mobile/buyer/orders/statistics?user_id=$userId'),
        headers: {
          'Content-Type': 'application/json',
        },
      ).timeout(const Duration(seconds: 10));

      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200 && data['status'] == 'success') {
        return {
          'success': true,
          'data': data['data'],
        };
      } else {
        return {
          'success': false,
          'message': data['message'] ?? 'Failed to load order statistics',
        };
      }
    } catch (e) {
      print('Get order statistics error: $e');
      return {
        'success': false,
        'message': 'Connection error. Please check your internet connection.',
      };
    }
  }

  static Future<Map<String, dynamic>> submitReview({
    required int userId,
    required int orderId,
    required int rating,
    String reviewText = '',
  }) async {
    try {
      final response = await http.post(
        Uri.parse('http://192.168.1.3:5000/api/mobile/buyer/orders/submit-review'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'user_id': userId,
          'order_id': orderId,
          'rating': rating,
          'review_text': reviewText,
        }),
      ).timeout(const Duration(seconds: 10));

      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200 && data['status'] == 'success') {
        return {
          'success': true,
          'message': data['message'],
        };
      } else {
        return {
          'success': false,
          'message': data['message'] ?? 'Failed to submit review',
        };
      }
    } catch (e) {
      print('Submit review error: $e');
      return {
        'success': false,
        'message': 'Connection error. Please check your internet connection.',
      };
    }
  }

  static Future<Map<String, dynamic>> markOrderReceived({
    required int userId,
    required int orderId,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('http://192.168.1.3:5000/api/mobile/buyer/orders/mark-received'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'user_id': userId,
          'order_id': orderId,
        }),
      ).timeout(const Duration(seconds: 10));

      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200 && data['status'] == 'success') {
        return {
          'success': true,
          'message': data['message'],
        };
      } else {
        return {
          'success': false,
          'message': data['message'] ?? 'Failed to mark order as received',
        };
      }
    } catch (e) {
      print('Mark order received error: $e');
      return {
        'success': false,
        'message': 'Connection error. Please check your internet connection.',
      };
    }
  }
} 