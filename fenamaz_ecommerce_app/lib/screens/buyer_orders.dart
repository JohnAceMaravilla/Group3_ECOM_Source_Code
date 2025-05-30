import 'package:flutter/material.dart';
import 'package:fenamaz_ecommerce_app/services/buyer_service.dart';
import 'package:fenamaz_ecommerce_app/services/user_session.dart';
import 'package:fenamaz_ecommerce_app/screens/buyer_product.dart';
import 'dart:convert';

class BuyerOrdersScreen extends StatefulWidget {
  @override
  _BuyerOrdersScreenState createState() => _BuyerOrdersScreenState();
}

class _BuyerOrdersScreenState extends State<BuyerOrdersScreen> with TickerProviderStateMixin {
  late TabController _tabController;
  List<dynamic> _orders = [];
  Map<String, dynamic>? _statistics;
  bool _isLoading = true;
  String? _errorMessage;
  int? _userId;
  
  String _currentStatus = 'Pending';
  String _sortBy = 'date_ordered';
  String _order = 'desc';

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 5, vsync: this);
    _tabController.addListener(_onTabChanged);
    _loadUserData();
  }

  @override
  void dispose() {
    _tabController.removeListener(_onTabChanged);
    _tabController.dispose();
    super.dispose();
  }

  void _onTabChanged() {
    if (_tabController.indexIsChanging) return;
    
    final statusMap = ['Pending', 'To Pack', 'To Ship', 'To Deliver', 'Completed'];
    setState(() {
      _currentStatus = statusMap[_tabController.index];
    });
    _loadOrders();
  }

  Future<void> _loadUserData() async {
    final userData = await UserSession.getUserData();
    setState(() {
      _userId = userData?['user_id'] != null 
          ? int.tryParse(userData!['user_id'].toString()) 
          : null;
    });
    if (_userId != null) {
      _loadOrdersAndStatistics();
    } else {
      setState(() {
        _errorMessage = 'Please login to view your orders';
        _isLoading = false;
      });
    }
  }

  Future<void> _loadOrdersAndStatistics() async {
    if (_userId == null) return;

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      // Load orders and statistics concurrently
      final futures = await Future.wait([
        BuyerService.getOrders(
          userId: _userId!,
          status: _currentStatus,
          sortBy: _sortBy,
          order: _order,
        ),
        BuyerService.getOrderStatistics(userId: _userId!),
      ]);

      final ordersResponse = futures[0];
      final statsResponse = futures[1];

      if (ordersResponse['success']) {
        setState(() {
          _orders = ordersResponse['data'] ?? [];
          _isLoading = false;
        });
      } else {
        setState(() {
          _errorMessage = ordersResponse['message'];
          _isLoading = false;
        });
      }

      if (statsResponse['success']) {
        setState(() {
          _statistics = statsResponse['data'];
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Failed to load orders';
        _isLoading = false;
      });
    }
  }

  Future<void> _loadOrders() async {
    if (_userId == null) return;

    try {
      final response = await BuyerService.getOrders(
        userId: _userId!,
        status: _currentStatus,
        sortBy: _sortBy,
        order: _order,
      );

      if (response['success']) {
        setState(() {
          _orders = response['data'] ?? [];
        });
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(response['message']),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to load orders'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  Future<void> _submitReview(int orderId, int rating, String reviewText) async {
    if (_userId == null) return;

    try {
      final response = await BuyerService.submitReview(
        userId: _userId!,
        orderId: orderId,
        rating: rating,
        reviewText: reviewText,
      );

      if (response['success']) {
        // Reload orders immediately to show the updated review status
        await _loadOrders();
        
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(response['message']),
            backgroundColor: Colors.green,
            duration: Duration(seconds: 3),
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(response['message']),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to submit review'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  Future<void> _markOrderReceived(int orderId, String productName) async {
    if (_userId == null) return;

    // Show confirmation dialog
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Confirm Receipt'),
        content: Text('Mark this order as received?\n\n"$productName"\n\nBy confirming receipt, you acknowledge that you have received the order in good condition. Payment will be released to the seller.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            child: Text('Confirm Receipt'),
            style: ElevatedButton.styleFrom(backgroundColor: Color(0xFF2196F3)),
          ),
        ],
      ),
    );

    if (confirm != true) return;

    try {
      final response = await BuyerService.markOrderReceived(
        userId: _userId!,
        orderId: orderId,
      );

      if (response['success']) {
        // Reload orders immediately to show the Write Review button
        await _loadOrders();
        
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(response['message']),
            backgroundColor: Colors.green,
            duration: Duration(seconds: 3),
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(response['message']),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to mark order as received'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  void _showReviewDialog(Map<String, dynamic> order) {
    int rating = 0;
    final reviewController = TextEditingController();

    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: Text('Write a Review'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Order #${order['order_id']}', style: TextStyle(fontWeight: FontWeight.bold)),
                SizedBox(height: 8),
                Text('Product: ${order['product_name']}'),
                SizedBox(height: 8),
                Text('Shop: ${order['shop_name']}'),
                SizedBox(height: 16),
                
                // Star Rating
                Text('Rating *', style: TextStyle(fontWeight: FontWeight.w500)),
                SizedBox(height: 8),
                Row(
                  children: List.generate(5, (index) {
                    return GestureDetector(
                      onTap: () {
                        setDialogState(() {
                          rating = index + 1;
                        });
                      },
                      child: Icon(
                        Icons.star,
                        size: 32,
                        color: index < rating ? Colors.amber : Colors.grey[300],
                      ),
                    );
                  }),
                ),
                SizedBox(height: 16),
                
                // Review Text
                Text('Review (Optional)'),
                SizedBox(height: 8),
                TextField(
                  controller: reviewController,
                  maxLines: 3,
                  decoration: InputDecoration(
                    hintText: 'Share your experience with this product...',
                    border: OutlineInputBorder(),
                  ),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: rating > 0
                  ? () {
                      Navigator.pop(context);
                      _submitReview(order['order_id'], rating, reviewController.text.trim());
                    }
                  : null,
              child: Text('Submit Review'),
              style: ElevatedButton.styleFrom(backgroundColor: Color(0xFF2196F3)),
            ),
          ],
        ),
      ),
    );
  }

  String _formatPrice(double price) {
    return price.toInt().toString().replaceAllMapped(
      RegExp(r'(\d)(?=(\d{3})+(?!\d))'),
      (Match match) => '${match[1]},',
    );
  }

  String _formatDate(String? dateString) {
    if (dateString == null) return 'Unknown';
    try {
      final date = DateTime.parse(dateString);
      return '${date.day}/${date.month}/${date.year}';
    } catch (e) {
      return 'Unknown';
    }
  }

  Color _getStatusColor(String status) {
    switch (status) {
      case 'Pending':
        return Colors.orange;
      case 'To Pack':
      case 'Packed':
        return Colors.blue;
      case 'Shipping':
      case 'Shipped':
        return Colors.purple;
      case 'For Delivery':
      case 'Out for Delivery':
      case 'Delivered':
        return Colors.green;
      case 'Received':
        return Colors.grey[700]!;
      default:
        return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: Text('My Orders'),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black,
        elevation: 1,
        automaticallyImplyLeading: false,
        actions: [
          IconButton(
            onPressed: _loadOrdersAndStatistics,
            icon: Icon(Icons.refresh, color: Color(0xFF2196F3)),
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          isScrollable: true,
          labelColor: Color(0xFF2196F3),
          unselectedLabelColor: Colors.grey,
          indicatorColor: Color(0xFF2196F3),
          tabs: [
            Tab(
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text('Pending'),
                  if (_statistics?['pending_orders'] != null && _statistics!['pending_orders'] > 0) ...[
                    SizedBox(width: 8),
                    Container(
                      padding: EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(
                        color: Colors.orange,
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Text(
                        '${_statistics!['pending_orders']}',
                        style: TextStyle(color: Colors.white, fontSize: 12),
                      ),
                    ),
                  ],
                ],
              ),
            ),
            Tab(
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text('To Pack'),
                  if (_statistics?['to_pack_orders'] != null && _statistics!['to_pack_orders'] > 0) ...[
                    SizedBox(width: 8),
                    Container(
                      padding: EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(
                        color: Colors.blue,
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Text(
                        '${_statistics!['to_pack_orders']}',
                        style: TextStyle(color: Colors.white, fontSize: 12),
                      ),
                    ),
                  ],
                ],
              ),
            ),
            Tab(
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text('To Ship'),
                  if (_statistics?['to_ship_orders'] != null && _statistics!['to_ship_orders'] > 0) ...[
                    SizedBox(width: 8),
                    Container(
                      padding: EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(
                        color: Colors.purple,
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Text(
                        '${_statistics!['to_ship_orders']}',
                        style: TextStyle(color: Colors.white, fontSize: 12),
                      ),
                    ),
                  ],
                ],
              ),
            ),
            Tab(
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text('To Deliver'),
                  if (_statistics?['to_deliver_orders'] != null && _statistics!['to_deliver_orders'] > 0) ...[
                    SizedBox(width: 8),
                    Container(
                      padding: EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(
                        color: Colors.green,
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Text(
                        '${_statistics!['to_deliver_orders']}',
                        style: TextStyle(color: Colors.white, fontSize: 12),
                      ),
                    ),
                  ],
                ],
              ),
            ),
            Tab(
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text('Completed'),
                  if (_statistics?['completed_orders'] != null && _statistics!['completed_orders'] > 0) ...[
                    SizedBox(width: 8),
                    Container(
                      padding: EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(
                        color: Colors.grey[700],
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Text(
                        '${_statistics!['completed_orders']}',
                        style: TextStyle(color: Colors.white, fontSize: 12),
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ],
        ),
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
              onPressed: _loadOrdersAndStatistics,
              child: Text('Retry'),
            ),
          ],
        ),
      );
    }

    return Column(
      children: [
        // Orders List
        Expanded(
          child: _orders.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        Icons.shopping_bag_outlined,
                        size: 80,
                        color: Colors.grey[400],
                      ),
                      SizedBox(height: 20),
                      Text(
                        'No ${_currentStatus.toLowerCase()} orders',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: Colors.grey[600],
                        ),
                      ),
                      SizedBox(height: 8),
                      Text(
                        'Your ${_currentStatus.toLowerCase()} orders will appear here',
                        style: TextStyle(
                          fontSize: 16,
                          color: Colors.grey[500],
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _loadOrdersAndStatistics,
                  child: ListView.builder(
                    padding: EdgeInsets.symmetric(horizontal: 16),
                    itemCount: _orders.length,
                    itemBuilder: (context, index) {
                      return _buildOrderCard(_orders[index]);
                    },
                  ),
                ),
        ),
      ],
    );
  }

  Widget _buildOrderCard(Map<String, dynamic> order) {
    return Container(
      margin: EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Order Header
          Container(
            padding: EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Color(0xFF2196F3).withOpacity(0.1),
              borderRadius: BorderRadius.only(
                topLeft: Radius.circular(12),
                topRight: Radius.circular(12),
              ),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    Icon(Icons.store, color: Color(0xFF2196F3), size: 20),
                    SizedBox(width: 8),
                    Text(
                      order['shop_name'] ?? 'Unknown Shop',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF2196F3),
                      ),
                    ),
                  ],
                ),
                Container(
                  padding: EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                  decoration: BoxDecoration(
                    color: _getStatusColor(order['status']),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    order['status'],
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 12,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
              ],
            ),
          ),

          // Order Content
          Padding(
            padding: EdgeInsets.all(16),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Product Image
                GestureDetector(
                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => BuyerProductScreen(
                          productInfoId: order['product_info_id'],
                        ),
                      ),
                    );
                  },
                  child: Container(
                    width: 80,
                    height: 80,
                    decoration: BoxDecoration(
                      color: Colors.grey[100],
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(8),
                      child: order['image_base64'] != null
                          ? Image.memory(
                              base64Decode(order['image_base64'].split(',')[1]),
                              fit: BoxFit.cover,
                              errorBuilder: (context, error, stackTrace) {
                                return Icon(Icons.image, size: 30, color: Colors.grey[400]);
                              },
                            )
                          : Icon(Icons.image, size: 30, color: Colors.grey[400]),
                    ),
                  ),
                ),

                SizedBox(width: 12),

                // Order Details
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      GestureDetector(
                        onTap: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) => BuyerProductScreen(
                                productInfoId: order['product_info_id'],
                              ),
                            ),
                          );
                        },
                        child: Text(
                          order['product_name'] ?? 'Unknown Product',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w600,
                            color: Color(0xFF2196F3),
                          ),
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      SizedBox(height: 4),
                      Text(
                        '${order['variant']}, ${order['color']}',
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.grey[600],
                        ),
                      ),
                      SizedBox(height: 4),
                      Text(
                        'Qty: ${order['quantity']} | Order #${order['order_id']}',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey[500],
                        ),
                      ),
                      SizedBox(height: 8),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            '₱${_formatPrice(order['total_amount']?.toDouble() ?? 0)}',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                              color: Colors.black87,
                            ),
                          ),
                          Text(
                            _formatDate(order['date_ordered']),
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.grey[500],
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

          // Action Buttons
          if (order['status'] == 'Delivered' || 
              (order['status'] == 'Received' && !order['has_review']) ||
              (order['status'] == 'Received' && order['has_review']))
            Container(
              padding: EdgeInsets.fromLTRB(16, 0, 16, 16),
              child: Row(
                children: [
                  if (order['status'] == 'Delivered') ...[
                    Expanded(
                      child: ElevatedButton(
                        onPressed: () => _markOrderReceived(
                          order['order_id'],
                          order['product_name'],
                        ),
                        child: Text('Mark as Received'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Color(0xFF2196F3),
                          foregroundColor: Colors.white,
                        ),
                      ),
                    ),
                  ] else if (order['status'] == 'Received' && !order['has_review']) ...[
                    Expanded(
                      child: ElevatedButton.icon(
                        onPressed: () => _showReviewDialog(order),
                        icon: Icon(Icons.star, size: 18),
                        label: Text('Write Review'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.amber,
                          foregroundColor: Colors.white,
                        ),
                      ),
                    ),
                  ] else if (order['status'] == 'Received' && order['has_review']) ...[
                    Container(
                      padding: EdgeInsets.symmetric(vertical: 8),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(Icons.check_circle, color: Colors.green, size: 20),
                              SizedBox(width: 8),
                              Text(
                                'Reviewed',
                                style: TextStyle(
                                  color: Colors.green,
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                            ],
                          ),
                          if (order['user_rating'] != null) ...[
                            SizedBox(height: 8),
                            Row(
                              children: [
                                Text('Your Rating: '),
                                Row(
                                  children: List.generate(5, (index) {
                                    return Icon(
                                      Icons.star,
                                      size: 16,
                                      color: index < order['user_rating'] 
                                          ? Colors.amber 
                                          : Colors.grey[300],
                                    );
                                  }),
                                ),
                                SizedBox(width: 8),
                                Text(
                                  '${order['user_rating']}/5',
                                  style: TextStyle(
                                    fontWeight: FontWeight.w500,
                                    color: Colors.grey[600],
                                  ),
                                ),
                              ],
                            ),
                          ],
                          if (order['user_feedback'] != null && order['user_feedback'].toString().isNotEmpty) ...[
                            SizedBox(height: 8),
                            Container(
                              padding: EdgeInsets.all(8),
                              decoration: BoxDecoration(
                                color: Colors.grey[100],
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    'Your Review:',
                                    style: TextStyle(
                                      fontWeight: FontWeight.w500,
                                      fontSize: 12,
                                      color: Colors.grey[600],
                                    ),
                                  ),
                                  SizedBox(height: 4),
                                  Text(
                                    order['user_feedback'],
                                    style: TextStyle(
                                      fontSize: 12,
                                      color: Colors.black87,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ],
                      ),
                    ),
                  ],
                ],
              ),
            ),
        ],
      ),
    );
  }
} 