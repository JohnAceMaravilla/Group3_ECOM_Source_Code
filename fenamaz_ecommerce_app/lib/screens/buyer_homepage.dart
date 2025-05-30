import 'package:flutter/material.dart';
import 'package:fenamaz_ecommerce_app/services/user_session.dart';
import 'package:fenamaz_ecommerce_app/services/buyer_service.dart';
import 'package:fenamaz_ecommerce_app/services/notification_service.dart';
// import 'package:fenamaz_ecommerce_app/screens/login_screen.dart';
// import 'package:fenamaz_ecommerce_app/screens/buyer_categories.dart';
import 'package:fenamaz_ecommerce_app/screens/buyer_category_products.dart';
import 'package:fenamaz_ecommerce_app/screens/buyer_orders.dart';
import 'package:fenamaz_ecommerce_app/screens/buyer_profile.dart';
import 'package:fenamaz_ecommerce_app/screens/buyer_product.dart';
import 'package:fenamaz_ecommerce_app/screens/buyer_likes.dart';
import 'package:fenamaz_ecommerce_app/screens/buyer_cart.dart';
import 'package:fenamaz_ecommerce_app/screens/buyer_notifications.dart';
import 'package:fenamaz_ecommerce_app/screens/buyer_search.dart';
import 'dart:convert';
import 'dart:async';

class BuyerHomepage extends StatefulWidget {
  @override
  _BuyerHomepageState createState() => _BuyerHomepageState();
}

class _BuyerHomepageState extends State<BuyerHomepage> {
  int _currentIndex = 0;
  String? userName;
  int? userId;
  bool _isLoading = true;
  int _unreadNotificationCount = 0;
  final TextEditingController _searchController = TextEditingController();
  
  // Homepage data
  List<dynamic> _bestSellers = [];
  List<dynamic> _highestRated = [];
  List<dynamic> _mostReviewed = [];
  String? _errorMessage;

  // Pagination controllers
  PageController _bestSellersController = PageController();
  PageController _highestRatedController = PageController();
  PageController _mostReviewedController = PageController();
  PageController _bannerController = PageController();
  
  int _bestSellersPage = 0;
  int _highestRatedPage = 0;
  int _mostReviewedPage = 0;
  int _bannerPage = 0;

  @override
  void initState() {
    super.initState();
    _initializeApp();
  }

  @override
  void didUpdateWidget(BuyerHomepage oldWidget) {
    super.didUpdateWidget(oldWidget);
    // Refresh notification count when widget updates
    if (userId != null) {
      _loadUnreadNotificationCount();
    }
  }

  Future<void> _initializeApp() async {
    await _loadUserData();
    await _loadHomepageData();
    // Load notification count after user data is available
    if (userId != null) {
      await _loadUnreadNotificationCount();
      _startNotificationCountTimer();
    }
  }

  void _startNotificationCountTimer() {
    // Refresh notification count every 15 seconds for better responsiveness
    Timer.periodic(Duration(seconds: 15), (timer) {
      if (mounted && userId != null) {
        _loadUnreadNotificationCount();
      } else {
        timer.cancel();
      }
    });
  }

  @override
  void dispose() {
    _bestSellersController.dispose();
    _highestRatedController.dispose();
    _mostReviewedController.dispose();
    _bannerController.dispose();
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _loadUserData() async {
    final userData = await UserSession.getUserData();
    setState(() {
      userName = userData?['name'] ?? "Buyer";
      userId = userData?['user_id'] != null 
          ? int.tryParse(userData!['user_id'].toString()) 
          : null;
    });
    print('User loaded: $userName, ID: $userId'); // Debug print
    
    // Load notification count immediately after user data is loaded
    if (userId != null) {
      _loadUnreadNotificationCount();
    }
  }

  Future<void> _loadHomepageData() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final response = await BuyerService.getHomepageData(userId: userId);
      
      if (response['success']) {
        final data = response['data'];
        setState(() {
          _bestSellers = data['best_sellers'] ?? [];
          _highestRated = data['highest_rated'] ?? [];
          _mostReviewed = data['most_reviewed'] ?? [];
          _isLoading = false;
        });
        
        // Refresh notification count after loading homepage data
        if (userId != null) {
          _loadUnreadNotificationCount();
        }
      } else {
        setState(() {
          _errorMessage = response['message'];
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Failed to load data';
        _isLoading = false;
      });
    }
  }

  Future<void> _loadUnreadNotificationCount() async {
    if (userId == null) return;
    
    try {
      final response = await NotificationService.getUnreadCount(buyerId: userId!);
      if (response['success'] && mounted) {
        setState(() {
          _unreadNotificationCount = response['data']['unread_count'] ?? 0;
        });
        print('Notification count loaded: $_unreadNotificationCount'); // Debug print
      }
    } catch (e) {
      // Silently fail for notification count
      print('Error loading notification count: $e');
    }
  }

  Future<void> _toggleProductLike(int productId, int index, String section) async {
    if (userId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Please login to like products'),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }

    try {
      final response = await BuyerService.toggleProductLike(productId, userId!);
      
      if (response['success']) {
        setState(() {
          switch (section) {
            case 'best_sellers':
              _bestSellers[index]['is_liked'] = response['data']['is_liked'];
              break;
            case 'highest_rated':
              _highestRated[index]['is_liked'] = response['data']['is_liked'];
              break;
            case 'most_reviewed':
              _mostReviewed[index]['is_liked'] = response['data']['is_liked'];
              break;
          }
        });
        
        // Success message
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              response['data']['is_liked'] 
                  ? 'Added to favorites' 
                  : 'Removed from favorites'
            ),
            backgroundColor: Colors.green,
            duration: Duration(seconds: 2),
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(response['message'] ?? 'Failed to update like status'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to update like status'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  String _formatPrice(double price) {
    return price.toInt().toString().replaceAllMapped(
      RegExp(r'(\d)(?=(\d{3})+(?!\d))'),
      (Match match) => '${match[1]},',
    );
  }

  double _parsePrice(dynamic price) {
    if (price == null) return 0.0;
    if (price is double) return price;
    if (price is int) return price.toDouble();
    if (price is String) {
      return double.tryParse(price) ?? 0.0;
    }
    return 0.0;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // NO APP BAR - just like the website
      body: SafeArea(
        child: IndexedStack(
          index: _currentIndex,
          children: [
            _buildHomeTab(),
            BuyerNotificationsScreen(),
            BuyerCartScreen(
              onNavigateToHome: () {
                setState(() {
                  _currentIndex = 0; // Navigate to home tab
                });
                // Refresh notification count when returning to home
                if (userId != null) {
                  _loadUnreadNotificationCount();
                }
              },
            ),
            BuyerOrdersScreen(),
            BuyerProfileScreen(),
          ],
        ),
      ),
      bottomNavigationBar: BottomNavigationBar(
        type: BottomNavigationBarType.fixed,
        currentIndex: _currentIndex,
        onTap: (index) {
          setState(() {
            _currentIndex = index;
          });
          
          // Handle notification tab click - mark as read
          if (index == 1) {
            // When clicking notifications tab, mark all as read after a short delay
            Future.delayed(Duration(milliseconds: 800), () {
              if (userId != null) {
                NotificationService.markNotificationsAsRead(buyerId: userId!);
                // Reset count to 0 immediately
                setState(() {
                  _unreadNotificationCount = 0;
                });
                // Refresh the count after marking as read
                Future.delayed(Duration(milliseconds: 1000), () {
                  _loadUnreadNotificationCount();
                });
              }
            });
          }
          
          // Always refresh notification count when switching tabs
          if (userId != null) {
            _loadUnreadNotificationCount();
          }
        },
        selectedItemColor: Color(0xFF2196F3),
        unselectedItemColor: Colors.grey,
        items: [
          BottomNavigationBarItem(
            icon: Icon(Icons.home),
            label: 'Home',
          ),
          BottomNavigationBarItem(
            icon: Stack(
              children: [
                Icon(Icons.notifications),
                if (_unreadNotificationCount > 0)
                  Positioned(
                    right: 0,
                    top: 0,
                    child: Container(
                      padding: EdgeInsets.all(2),
                      decoration: BoxDecoration(
                        color: Colors.red,
                        borderRadius: BorderRadius.circular(10),
                      ),
                      constraints: BoxConstraints(
                        minWidth: 16,
                        minHeight: 16,
                      ),
                      child: Text(
                        '$_unreadNotificationCount',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ),
                  ),
              ],
            ),
            label: 'Notification',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.shopping_cart),
            label: 'Cart',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.assignment),
            label: 'Orders',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person),
            label: 'Account',
          ),
        ],
      ),
    );
  }

  Widget _buildHomeTab() {
    if (_isLoading) {
      return Center(
        child: CircularProgressIndicator(
          valueColor: AlwaysStoppedAnimation<Color>(Color(0xFF2196F3)),
        ),
      );
    }

    if (_errorMessage != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.error_outline, size: 64, color: Colors.grey),
            SizedBox(height: 16),
            Text(
              _errorMessage!,
              style: TextStyle(fontSize: 16, color: Colors.grey[600]),
              textAlign: TextAlign.center,
            ),
            SizedBox(height: 16),
            ElevatedButton(
              onPressed: _loadHomepageData,
              child: Text('Retry'),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadHomepageData,
      child: SingleChildScrollView(
        physics: AlwaysScrollableScrollPhysics(),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Search Bar exactly like website
            Container(
              margin: EdgeInsets.all(16),
              child: Row(
                children: [
                  Expanded(
                    child: Container(
                      height: 48,
                      child: TextField(
                        controller: _searchController,
                        onTap: () {
                          // Navigate to search screen when tapping the search field
                          _navigateToSearch();
                        },
                        onSubmitted: (value) {
                          // Navigate with search query when submitting
                          _performSearch();
                        },
                        decoration: InputDecoration(
                          hintText: 'Search keywords...',
                          prefixIcon: Icon(Icons.search, color: Colors.grey),
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8),
                            borderSide: BorderSide(color: Colors.grey[300]!),
                          ),
                          filled: true,
                          fillColor: Colors.white,
                          contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 0),
                        ),
                      ),
                    ),
                  ),
                  SizedBox(width: 12),
                  GestureDetector(
                    onTap: _performSearch,
                    child: Container(
                      height: 48,
                      padding: EdgeInsets.symmetric(horizontal: 20),
                      decoration: BoxDecoration(
                        color: Color(0xFF2196F3),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Center(
                        child: Text(
                          'Search',
                          style: TextStyle(color: Colors.white, fontWeight: FontWeight.w500),
                        ),
                      ),
                    ),
                  ),
                  SizedBox(width: 8),
                  GestureDetector(
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => BuyerLikesScreen(),
                        ),
                      );
                    },
                    child: Icon(Icons.favorite_border, color: Colors.grey, size: 28),
                  ),
                ],
              ),
            ),
            
            // Banner/Carousel Section - like website
            Container(
              height: 200,
              margin: EdgeInsets.symmetric(horizontal: 16),
              child: Stack(
                children: [
                  PageView(
                    controller: _bannerController,
                    onPageChanged: (page) {
                      setState(() {
                        _bannerPage = page;
                      });
                    },
                    children: [
                      // First banner - UNLEASH YOUR POWER
                      Container(
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Stack(
                          children: [
                            Positioned.fill(
                              child: ClipRRect(
                                borderRadius: BorderRadius.circular(12),
                                child: Image.network(
                                  'http://192.168.1.3:5000/static/img/cover/fenamaz_cover1.jpg',
                                  fit: BoxFit.cover,
                                  errorBuilder: (context, error, stackTrace) {
                                    return Container(
                                      decoration: BoxDecoration(
                                        borderRadius: BorderRadius.circular(12),
                                        gradient: LinearGradient(
                                          begin: Alignment.topLeft,
                                          end: Alignment.bottomRight,
                                          colors: [Color(0xFF8B0000), Color(0xFFFF1493), Color(0xFF8A2BE2)],
                                        ),
                                      ),
                                      child: Center(
                                        child: Column(
                                          mainAxisAlignment: MainAxisAlignment.center,
                                          children: [
                                            Text(
                                              'UNLEASH YOUR POWER',
                                              style: TextStyle(
                                                color: Colors.white,
                                                fontSize: 24,
                                                fontWeight: FontWeight.bold,
                                                shadows: [Shadow(blurRadius: 4, color: Colors.black45)],
                                              ),
                                            ),
                                            SizedBox(height: 8),
                                            Text(
                                              'ORDER YOURS NOW AND DOMINATE YOUR GAMES!',
                                              style: TextStyle(
                                                color: Colors.white,
                                                fontSize: 12,
                                                fontWeight: FontWeight.w500,
                                              ),
                                              textAlign: TextAlign.center,
                                            ),
                                          ],
                                        ),
                                      ),
                                    );
                                  },
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                      
                      // Second banner - PC Building
                      Container(
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Stack(
                          children: [
                            Positioned.fill(
                              child: ClipRRect(
                                borderRadius: BorderRadius.circular(12),
                                child: Image.network(
                                  'http://192.168.1.3:5000/static/img/cover/fenamaz_cover2.png',
                                  fit: BoxFit.cover,
                                  errorBuilder: (context, error, stackTrace) {
                                    return Container(
                                      decoration: BoxDecoration(
                                        borderRadius: BorderRadius.circular(12),
                                        gradient: LinearGradient(
                                          begin: Alignment.topLeft,
                                          end: Alignment.bottomRight,
                                          colors: [Color(0xFF1E3A8A), Color(0xFF3B82F6), Color(0xFF8B5CF6)],
                                        ),
                                      ),
                                      child: Positioned(
                                        left: 16,
                                        top: 0,
                                        bottom: 0,
                                        child: Column(
                                          mainAxisAlignment: MainAxisAlignment.center,
                                          crossAxisAlignment: CrossAxisAlignment.start,
                                          children: [
                                            Text(
                                              'START BUILDING YOUR\nDREAM PC TODAY!',
                                              style: TextStyle(
                                                color: Colors.white,
                                                fontSize: 16,
                                                fontWeight: FontWeight.bold,
                                                shadows: [Shadow(blurRadius: 4, color: Colors.black45)],
                                              ),
                                            ),
                                            SizedBox(height: 8),
                                            Text(
                                              'DON\'T SETTLE FOR "ALMOST"\nWHEN YOU CAN HAVE THE PERFECT PC!',
                                              style: TextStyle(
                                                color: Colors.white,
                                                fontSize: 10,
                                                fontWeight: FontWeight.w500,
                                              ),
                                            ),
                                          ],
                                        ),
                                      ),
                                    );
                                  },
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                      
                      // Third banner - Upgrade Setup
                      Container(
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Stack(
                          children: [
                            Positioned.fill(
                              child: ClipRRect(
                                borderRadius: BorderRadius.circular(12),
                                child: Image.network(
                                  'http://192.168.1.3:5000/static/img/cover/fenamaz_cover3.png',
                                  fit: BoxFit.cover,
                                  errorBuilder: (context, error, stackTrace) {
                                    return Container(
                                      decoration: BoxDecoration(
                                        borderRadius: BorderRadius.circular(12),
                                        gradient: LinearGradient(
                                          begin: Alignment.topLeft,
                                          end: Alignment.bottomRight,
                                          colors: [Color(0xFF4C1D95), Color(0xFF7C3AED), Color(0xFFEC4899)],
                                        ),
                                      ),
                                      child: Center(
                                        child: Column(
                                          mainAxisAlignment: MainAxisAlignment.center,
                                          children: [
                                            Text(
                                              'UPGRADE YOUR SETUP WITH US',
                                              style: TextStyle(
                                                color: Colors.white,
                                                fontSize: 18,
                                                fontWeight: FontWeight.bold,
                                                shadows: [Shadow(blurRadius: 4, color: Colors.black45)],
                                              ),
                                              textAlign: TextAlign.center,
                                            ),
                                            SizedBox(height: 8),
                                            Text(
                                              'Premium Gaming Experience Awaits',
                                              style: TextStyle(
                                                color: Colors.white,
                                                fontSize: 12,
                                                fontWeight: FontWeight.w500,
                                              ),
                                              textAlign: TextAlign.center,
                                            ),
                                            SizedBox(height: 12),
                                            Text(
                                              'www.fenamaz.com',
                                              style: TextStyle(
                                                color: Colors.white70,
                                                fontSize: 10,
                                                fontWeight: FontWeight.w400,
                                              ),
                                            ),
                                          ],
                                        ),
                                      ),
                                    );
                                  },
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  
                  // Page indicators
                  Positioned(
                    bottom: 12,
                    left: 0,
                    right: 0,
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        for (int i = 0; i < 3; i++)
                          Container(
                            margin: EdgeInsets.symmetric(horizontal: 3),
                            width: 8,
                            height: 8,
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              color: _bannerPage == i 
                                  ? Colors.white 
                                  : Colors.white.withOpacity(0.5),
                            ),
                          ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            
            SizedBox(height: 20),
            
            // Category Icons Row - ALL categories like website
            Container(
              margin: EdgeInsets.symmetric(horizontal: 16),
              child: Wrap(
                spacing: 8,
                runSpacing: 16,
                alignment: WrapAlignment.spaceEvenly,
                children: [
                  _buildCategoryIcon(Icons.smartphone, 'Mobile\nPhone', 'Mobile Phones'),
                  _buildCategoryIcon(Icons.laptop, 'Laptop', 'Laptop'),
                  _buildCategoryIcon(Icons.desktop_windows, 'Desktop', 'Desktop'),
                  _buildCategoryIcon(Icons.headphones, 'Audio\nEquipment', 'Audio Equipment'),
                  _buildCategoryIcon(Icons.videocam, 'Video\nEquipment', 'Video Equipment'),
                  _buildCategoryIcon(Icons.home_outlined, 'Smart Home\nDevices', 'Smart Home Devices'),
                  _buildCategoryIcon(Icons.camera_alt, 'Photography', 'Photography'),
                  _buildCategoryIcon(Icons.watch, 'Wearable\nTech', 'Wearable Tech'),
                  _buildCategoryIcon(Icons.cable, 'Digital\nAccessories', 'Digital Accessories'),
                  _buildCategoryIcon(Icons.more_horiz, 'Others', 'Others'),
                ],
              ),
            ),
            
            SizedBox(height: 30),
            
            // Best Sellers
            if (_bestSellers.isNotEmpty) ...[
              _buildProductSection(
                title: 'Best Sellers',
                products: _bestSellers,
                sectionType: 'best_sellers',
                controller: _bestSellersController,
                currentPage: _bestSellersPage,
                onPageChanged: (page) => setState(() => _bestSellersPage = page),
              ),
            ],
            
            // Highest Rated
            if (_highestRated.isNotEmpty) ...[
              _buildProductSection(
                title: 'Highest Rated',
                products: _highestRated,
                sectionType: 'highest_rated',
                controller: _highestRatedController,
                currentPage: _highestRatedPage,
                onPageChanged: (page) => setState(() => _highestRatedPage = page),
              ),
            ],
            
            SizedBox(height: 20),
          ],
        ),
      ),
    );
  }

  Widget _buildCategoryIcon(IconData icon, String label, String categoryName) {
    return GestureDetector(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => BuyerCategoryProductsScreen(category: categoryName),
          ),
        );
      },
      child: Container(
        width: (MediaQuery.of(context).size.width - 64) / 5, // Adjusted for better spacing
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 60,
              height: 60,
              decoration: BoxDecoration(
                color: Color(0xFF2196F3).withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Center(
                child: Icon(icon, color: Color(0xFF2196F3), size: 28),
              ),
            ),
            SizedBox(height: 8),
            Text(
              label.replaceAll('\n', ' '), // Remove line breaks and use single line
              style: TextStyle(
                fontSize: 9, 
                fontWeight: FontWeight.w500,
                color: Colors.black87,
              ),
              textAlign: TextAlign.center,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildProductSection({
    required String title,
    required List<dynamic> products,
    required String sectionType,
    required PageController controller,
    required int currentPage,
    required Function(int) onPageChanged,
  }) {
    int totalPages = (products.length / 2).ceil();
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: EdgeInsets.symmetric(horizontal: 16),
          child: Text(
            title,
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        SizedBox(height: 8),
        
        // Product Cards with Pagination
        Container(
          height: 350, // Increased height to accommodate new card layout
          child: PageView.builder(
            controller: controller,
            onPageChanged: onPageChanged,
            itemCount: totalPages,
            itemBuilder: (context, pageIndex) {
              int startIndex = pageIndex * 2;
              int endIndex = (startIndex + 2).clamp(0, products.length);
              List<dynamic> pageProducts = products.sublist(startIndex, endIndex);
              
              return Padding(
                padding: EdgeInsets.symmetric(horizontal: 16),
                child: Row(
                  children: [
                    for (int i = 0; i < pageProducts.length; i++) ...[
                      Expanded(
                        child: _buildProductCard(
                          pageProducts[i], 
                          startIndex + i, 
                          sectionType
                        ),
                      ),
                      if (i < pageProducts.length - 1) SizedBox(width: 12),
                    ],
                    // Fill remaining space if only 1 product
                    if (pageProducts.length == 1) Expanded(child: SizedBox()),
                  ],
                ),
              );
            },
          ),
        ),
        
        // Pagination Controls (only show if more than 1 page)
        if (totalPages > 1) ...[
          SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              IconButton(
                onPressed: currentPage > 0 
                    ? () {
                        controller.previousPage(
                          duration: Duration(milliseconds: 300),
                          curve: Curves.easeInOut,
                        );
                      }
                    : null,
                icon: Icon(Icons.chevron_left),
                color: currentPage > 0 ? Color(0xFF2196F3) : Colors.grey,
              ),
              Text(
                '${currentPage + 1} / $totalPages',
                style: TextStyle(
                  fontWeight: FontWeight.w500,
                  color: Colors.grey[600],
                ),
              ),
              IconButton(
                onPressed: currentPage < totalPages - 1 
                    ? () {
                        controller.nextPage(
                          duration: Duration(milliseconds: 300),
                          curve: Curves.easeInOut,
                        );
                      }
                    : null,
                icon: Icon(Icons.chevron_right),
                color: currentPage < totalPages - 1 ? Color(0xFF2196F3) : Colors.grey,
              ),
            ],
          ),
        ],
        
        SizedBox(height: 20),
      ],
    );
  }

  Widget _buildProductCard(dynamic product, int index, String section) {
    double minPrice = _parsePrice(product['min_price']);
    double maxPrice = _parsePrice(product['max_price']);
    double averageRating = _parsePrice(product['average_rating']);

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8),
      ),
      child: Container(
        padding: EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            // Product Image with Heart Icon
            Stack(
              children: [
                Container(
                  height: 120,
                  width: double.infinity,
                  decoration: BoxDecoration(
                    color: Colors.grey[100],
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(8),
                    child: product['image_base64'] != null
                        ? Image.memory(
                            base64Decode(product['image_base64'].split(',')[1]),
                            fit: BoxFit.cover,
                            errorBuilder: (context, error, stackTrace) {
                              return Center(
                                child: Icon(Icons.image, size: 40, color: Colors.grey[400]),
                              );
                            },
                          )
                        : Center(
                            child: Icon(Icons.image, size: 40, color: Colors.grey[400]),
                          ),
                  ),
                ),
                // Heart icon in upper right
                Positioned(
                  top: 8,
                  right: 8,
                  child: GestureDetector(
                    onTap: () {
                      _toggleProductLike(
                        product['product_info_id'],
                        index,
                        section,
                      );
                    },
                    child: Container(
                      padding: EdgeInsets.all(6),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(20),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.1),
                            blurRadius: 4,
                            offset: Offset(0, 2),
                          ),
                        ],
                      ),
                      child: Icon(
                        product['is_liked'] == true
                            ? Icons.favorite
                            : Icons.favorite_border,
                        color: product['is_liked'] == true
                            ? Colors.red
                            : Colors.grey[600],
                        size: 18,
                      ),
                    ),
                  ),
                ),
              ],
            ),
            
            SizedBox(height: 12),
            
            // Product Name
            Text(
              product['product_name'] ?? 'Unknown Product',
              style: TextStyle(
                fontWeight: FontWeight.w600,
                fontSize: 14,
                color: Color(0xFF2196F3),
              ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            
            SizedBox(height: 8),
            
            // Price Range
            Text(
              minPrice == maxPrice 
                  ? '₱${_formatPrice(minPrice)}'
                  : '₱${_formatPrice(minPrice)}-₱${_formatPrice(maxPrice)}',
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.bold,
                color: Colors.black87,
              ),
            ),
            
            SizedBox(height: 8),
            
            // Variants and Colors
            Text(
              '${product['variant_count'] ?? 0} Variants | ${product['color_count'] ?? 0} Colors',
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey[600],
              ),
            ),
            
            SizedBox(height: 8),
            
            // Rating and Sales Info Row
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                // Single star with rating
                Row(
                  children: [
                    Icon(Icons.star, color: Colors.amber, size: 16),
                    SizedBox(width: 4),
                    Text(
                      averageRating.toStringAsFixed(1),
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey[600],
                      ),
                    ),
                  ],
                ),
                // Sales info
                Text(
                  section == 'best_sellers' 
                      ? '${product['total_orders'] ?? 0} Sold'
                      : section == 'most_reviewed'
                          ? '${product['total_feedback'] ?? product['total_ratings'] ?? 0} Reviews'
                          : '${product['total_ratings'] ?? 0} Ratings',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[600],
                  ),
                ),
              ],
            ),
            
            SizedBox(height: 6), // Small space between rating and button
            
            // Add to Cart Button
            SizedBox(
              width: double.infinity,
              height: 36,
              child: ElevatedButton.icon(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => BuyerProductScreen(
                        productInfoId: product['product_info_id'],
                      ),
                    ),
                  );
                },
                icon: Icon(Icons.shopping_cart, size: 16, color: Colors.white),
                label: Text(
                  'Add to Cart',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 12,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Color(0xFF2196F3),
                  elevation: 0,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(6),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildNotificationTab() {
    return Center(
      child: Text(
        'Notifications',
        style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
      ),
    );
  }

  void _navigateToSearch([String? query]) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => BuyerSearchScreen(
          initialQuery: query,
        ),
      ),
    );
  }

  void _performSearch() {
    final query = _searchController.text.trim();
    if (query.isNotEmpty) {
      _navigateToSearch(query);
    } else {
      _navigateToSearch();
    }
  }
} 