import 'package:flutter/material.dart';
import 'package:fenamaz_ecommerce_app/services/user_session.dart';
import 'package:fenamaz_ecommerce_app/services/notification_service.dart';

class BuyerNotificationsScreen extends StatefulWidget {
  @override
  _BuyerNotificationsScreenState createState() => _BuyerNotificationsScreenState();
}

class _BuyerNotificationsScreenState extends State<BuyerNotificationsScreen> {
  List<dynamic> _notifications = [];
  int _currentPage = 1;
  int _totalPages = 1;
  int _totalNotifications = 0;
  int _loadedNotifications = 0;
  bool _isLoading = true;
  bool _isLoadingMore = false;
  String? _errorMessage;
  String _sortBy = 'recent';
  int? _userId;
  final int _perPage = 10;

  @override
  void initState() {
    super.initState();
    _initializeData();
  }

  Future<void> _initializeData() async {
    await _loadUserData();
    await _loadNotifications();
  }

  Future<void> _loadUserData() async {
    final userData = await UserSession.getUserData();
    setState(() {
      _userId = userData?['user_id'] != null 
          ? int.tryParse(userData!['user_id'].toString()) 
          : null;
    });
  }

  Future<void> _loadNotifications({int page = 1, bool loadMore = false}) async {
    if (_userId == null) return;

    if (loadMore) {
      setState(() {
        _isLoadingMore = true;
      });
    } else {
      setState(() {
        _isLoading = true;
        _errorMessage = null;
      });
    }

    try {
      final response = await NotificationService.getNotifications(
        buyerId: _userId!,
        page: page,
        perPage: _perPage,
        sortBy: _sortBy,
      );

      if (response['success']) {
        final data = response['data'];
        final newNotifications = data['notifications'] ?? [];
        
        setState(() {
          if (loadMore) {
            // Append new notifications to existing list
            _notifications.addAll(newNotifications);
          } else {
            // Replace notifications list
            _notifications = newNotifications;
          }
          
          _currentPage = data['pagination']['current_page'] ?? 1;
          _totalPages = data['pagination']['total_pages'] ?? 1;
          _totalNotifications = data['pagination']['total_notifications'] ?? 0;
          _loadedNotifications = _notifications.length;
          _isLoading = false;
          _isLoadingMore = false;
        });

        // Auto-mark all notifications as read when viewing them
        if (_notifications.isNotEmpty && !loadMore) {
          NotificationService.markNotificationsAsRead(buyerId: _userId!);
        }
      } else {
        setState(() {
          _errorMessage = response['message'];
          _isLoading = false;
          _isLoadingMore = false;
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Failed to load notifications';
        _isLoading = false;
        _isLoadingMore = false;
      });
    }
  }

  Future<void> _loadMoreNotifications() async {
    if (_currentPage < _totalPages && !_isLoadingMore) {
      await _loadNotifications(page: _currentPage + 1, loadMore: true);
    }
  }

  Future<void> _refreshNotifications() async {
    await _loadNotifications(page: 1, loadMore: false);
  }

  void _toggleSort() {
    setState(() {
      _sortBy = _sortBy == 'recent' ? 'oldest' : 'recent';
    });
    _loadNotifications(page: 1, loadMore: false);
  }

  String _getNotificationTypeLabel(String type) {
    switch (type.toLowerCase()) {
      case 'order status': return 'Order Update';
      case 'order received': return 'Order Confirmation';
      case 'order complete': return 'Order Complete';
      case 'payment': return 'Payment Complete';
      case 'delivery': return 'Delivery Update';
      case 'promotion': return 'Promotion';
      case 'commission received': return 'Commission';
      case 'sales added': return 'Sales';
      case 'new review': return 'Review';
      default: return type;
    }
  }

  Color _getNotificationTypeColor(String type) {
    switch (type.toLowerCase()) {
      case 'order status':
      case 'order update': return Color(0xFF64B5F6); // Light Blue
      case 'order received':
      case 'order confirmation': return Color(0xFF81C784); // Light Green
      case 'order complete': return Color(0xFF81C784); // Light Green for completed orders
      case 'payment':
      case 'payment complete': return Color(0xFF81C784); // Light Green for completed payments
      case 'delivery':
      case 'delivery update': return Color(0xFF64B5F6); // Light Blue for delivery
      case 'promotion': return Color(0xFFE57373); // Light Red/Pink
      case 'commission received': return Color(0xFF81C784); // Light Green for money
      case 'sales added': return Color(0xFF7986CB); // Light Indigo
      case 'new review': return Color(0xFFFFB74D); // Light Orange
      default: return Color(0xFFBDBDBD); // Light Gray for unknown
    }
  }

  IconData _getNotificationIcon(String type) {
    switch (type.toLowerCase()) {
      case 'order status': 
      case 'order update': return Icons.shopping_bag;
      case 'order received': 
      case 'order confirmation': return Icons.check_circle;
      case 'order complete': return Icons.check; // Check icon for completed orders
      case 'payment': 
      case 'payment complete': return Icons.payment;
      case 'delivery': 
      case 'delivery update': return Icons.local_shipping;
      case 'promotion': return Icons.local_offer;
      case 'commission received': return Icons.account_balance_wallet;
      case 'sales added': return Icons.trending_up;
      case 'new review': return Icons.rate_review;
      default: return Icons.notifications;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white, // Match buyer_cart background
      appBar: AppBar(
        title: Text('Notifications'), // Match buyer_cart title style
        backgroundColor: Colors.white,
        foregroundColor: Colors.black,
        elevation: 1, // Match buyer_cart elevation
        automaticallyImplyLeading: false, // Remove back button since it's in tab navigation
        actions: [
          IconButton(
            icon: Icon(
              _sortBy == 'recent' ? Icons.access_time : Icons.history,
              color: Color(0xFF2196F3),
            ),
            onPressed: _toggleSort,
          ),
          IconButton(
            icon: Icon(Icons.refresh, color: Color(0xFF2196F3)),
            onPressed: _refreshNotifications,
          ),
        ],
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
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
              onPressed: _refreshNotifications,
              style: ElevatedButton.styleFrom(
                backgroundColor: Color(0xFF2196F3),
                foregroundColor: Colors.white,
              ),
              child: Text('Retry'),
            ),
          ],
        ),
      );
    }

    if (_notifications.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.notifications_off, size: 80, color: Colors.grey[400]),
            SizedBox(height: 20),
            Text(
              'No notifications yet',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.grey[600]),
            ),
            SizedBox(height: 8),
            Text(
              'We\'ll notify you when something important happens!',
              style: TextStyle(fontSize: 16, color: Colors.grey[500]),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      );
    }

    return Container(
      color: Color(0xFFF5F5F5), // Gray background like buyer_cart for better contrast
      child: Column(
        children: [
          Expanded(
            child: RefreshIndicator(
              onRefresh: _refreshNotifications,
              child: ListView.builder(
                padding: EdgeInsets.symmetric(horizontal: 16, vertical: 16),
                itemCount: _notifications.length,
                itemBuilder: (context, index) {
                  final notification = _notifications[index];
                  return _buildNotificationCard(notification);
                },
              ),
            ),
          ),
          if (_loadedNotifications < _totalNotifications) _buildShowMoreSection(),
        ],
      ),
    );
  }

  Widget _buildNotificationCard(dynamic notification) {
    final type = notification['notification_type'] ?? '';
    final isUnread = notification['status'] == 'Unread';
    
    return Container(
      margin: EdgeInsets.only(bottom: 12),
      child: Card(
        elevation: 2,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        child: Container(
          padding: EdgeInsets.all(20),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(12),
            color: Colors.white,
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Circular Icon - with neon colors
              Container(
                width: 60,
                height: 60,
                decoration: BoxDecoration(
                  color: _getNotificationTypeColor(type),
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: _getNotificationTypeColor(type).withOpacity(0.3),
                      blurRadius: 8,
                      offset: Offset(0, 2),
                    ),
                  ],
                ),
                child: Center(
                  child: Icon(
                    _getNotificationIcon(type),
                    color: Colors.white,
                    size: 24,
                  ),
                ),
              ),
              
              SizedBox(width: 16),
              
              // Content Area - fixed alignment
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Title Row
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Expanded(
                          child: Text(
                            notification['notification_title'] ?? 'Notification',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w600,
                              color: Colors.black87,
                            ),
                          ),
                        ),
                      ],
                    ),
                    
                    SizedBox(height: 8),
                    
                    // Content Description
                    Text(
                      notification['content'] ?? '',
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.grey[600],
                        height: 1.4,
                      ),
                    ),
                    
                    SizedBox(height: 16),
                    
                    // Bottom Row - Type Badge and Time aligned
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      crossAxisAlignment: CrossAxisAlignment.center,
                      children: [
                        // Type Badge
                        Container(
                          padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                          decoration: BoxDecoration(
                            color: _getNotificationTypeColor(type),
                            borderRadius: BorderRadius.circular(20),
                            boxShadow: [
                              BoxShadow(
                                color: _getNotificationTypeColor(type).withOpacity(0.3),
                                blurRadius: 4,
                                offset: Offset(0, 2),
                              ),
                            ],
                          ),
                          child: Text(
                            _getNotificationTypeLabel(type),
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 12,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                        
                        // Time - aligned with badge
                        Text(
                          notification['time_ago'] ?? '',
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.grey[500],
                            fontWeight: FontWeight.w400,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildShowMoreSection() {
    if (_loadedNotifications >= _totalNotifications) {
      // No more notifications to load
      return Container(
        padding: EdgeInsets.all(20),
        child: Center(
          child: Text(
            'No more notifications',
            style: TextStyle(
              color: Colors.grey[600],
              fontSize: 14,
            ),
          ),
        ),
      );
    }

    return Container(
      padding: EdgeInsets.all(20),
      child: Column(
        children: [
          // Showing X to Y of Z notifications
          Container(
            margin: EdgeInsets.only(bottom: 16),
            child: Text(
              'Showing ${_loadedNotifications > 0 ? 1 : 0} to $_loadedNotifications of $_totalNotifications notifications',
              style: TextStyle(
                color: Colors.grey[600],
                fontSize: 14,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
          
          // Show More button
          SizedBox(
            width: double.infinity,
            height: 45,
            child: ElevatedButton(
              onPressed: _isLoadingMore ? null : _loadMoreNotifications,
              style: ElevatedButton.styleFrom(
                backgroundColor: Color(0xFF2196F3),
                foregroundColor: Colors.white,
                elevation: 0,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
              child: _isLoadingMore
                  ? Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                          ),
                        ),
                        SizedBox(width: 12),
                        Text(
                          'Loading...',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ],
                    )
                  : Text(
                      'Show More',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
            ),
          ),
        ],
      ),
    );
  }
}
