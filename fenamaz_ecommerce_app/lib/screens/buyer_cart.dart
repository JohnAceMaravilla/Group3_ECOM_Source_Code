import 'package:flutter/material.dart';
import 'package:fenamaz_ecommerce_app/services/buyer_service.dart';
import 'package:fenamaz_ecommerce_app/services/user_session.dart';
import 'package:fenamaz_ecommerce_app/screens/buyer_product.dart';
import 'dart:convert';

class BuyerCartScreen extends StatefulWidget {
  final VoidCallback? onNavigateToHome;
  
  const BuyerCartScreen({Key? key, this.onNavigateToHome}) : super(key: key);

  @override
  _BuyerCartScreenState createState() => _BuyerCartScreenState();
}

class _BuyerCartScreenState extends State<BuyerCartScreen> with AutomaticKeepAliveClientMixin {
  @override
  bool get wantKeepAlive => true;
  
  List<dynamic> _shops = [];
  Map<String, dynamic>? _summary;
  Map<String, dynamic>? _buyerAddress;
  bool _isLoading = true;
  String? _errorMessage;
  int? _userId;

  @override
  void initState() {
    super.initState();
    _loadUserData();
  }

  @override
  void didUpdateWidget(BuyerCartScreen oldWidget) {
    super.didUpdateWidget(oldWidget);
    // Refresh cart when the widget updates (like when switching tabs)
    if (_userId != null) {
      _loadCartData();
    }
  }

  Future<void> _loadUserData() async {
    final userData = await UserSession.getUserData();
    setState(() {
      _userId = userData?['user_id'] != null 
          ? int.tryParse(userData!['user_id'].toString()) 
          : null;
    });
    if (_userId != null) {
      _loadCartData();
    } else {
      setState(() {
        _errorMessage = 'Please login to view your cart';
        _isLoading = false;
      });
    }
  }

  Future<void> _loadCartData() async {
    if (_userId == null) return;

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      // Load cart items and buyer address concurrently
      final futures = await Future.wait([
        BuyerService.getCartItems(userId: _userId!),
        BuyerService.getBuyerAddress(userId: _userId!),
      ]);

      final cartResponse = futures[0];
      final addressResponse = futures[1];

      if (cartResponse['success']) {
        setState(() {
          _shops = cartResponse['data']['shops'] ?? [];
          _summary = cartResponse['data']['summary'];
          _isLoading = false;
        });
      } else {
        setState(() {
          _errorMessage = cartResponse['message'];
          _isLoading = false;
        });
      }

      if (addressResponse['success']) {
        setState(() {
          _buyerAddress = addressResponse['data'];
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Failed to load cart data';
        _isLoading = false;
      });
    }
  }

  Future<void> _updateQuantity(int cartId, int newQuantity) async {
    if (_userId == null) return;

    // Find and update the item locally first for immediate UI update
    bool itemFound = false;
    for (var shop in _shops) {
      for (var item in shop['items']) {
        if (item['cart_id'] == cartId) {
          setState(() {
            // Update quantity and item total locally
            item['quantity'] = newQuantity;
            item['item_total'] = item['price'] * newQuantity;
            
            // Update shop subtotal
            shop['subtotal'] = 0.0;
            for (var shopItem in shop['items']) {
              shop['subtotal'] += shopItem['item_total'];
            }
            
            // Update overall summary
            _summary?['total_items'] = _shops.fold(0, (sum, shop) => sum + (shop['items'] as List).length);
            _summary?['subtotal'] = _shops.fold(0.0, (sum, shop) => sum + shop['subtotal']);
            _summary?['grand_total'] = (_summary?['subtotal'] ?? 0.0) + (_summary?['total_shipping'] ?? 0.0);
          });
          itemFound = true;
          break;
        }
      }
      if (itemFound) break;
    }

    try {
      final response = await BuyerService.updateCartQuantity(
        userId: _userId!,
        cartId: cartId,
        quantity: newQuantity,
      );

      if (response['success']) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(response['message']),
            backgroundColor: Colors.green,
            duration: Duration(seconds: 1),
          ),
        );
      } else {
        // If server update failed, reload to get correct state
        _loadCartData();
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(response['message']),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (e) {
      // If network error, reload to get correct state
      _loadCartData();
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to update quantity'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  Future<void> _removeItem(int cartId, String productName) async {
    if (_userId == null) return;

    // Show confirmation dialog
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Remove Item'),
        content: Text('Are you sure you want to remove "$productName" from your cart?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: Text('Remove', style: TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );

    if (confirm != true) return;

    try {
      final response = await BuyerService.removeCartItem(
        userId: _userId!,
        cartId: cartId,
      );

      if (response['success']) {
        _loadCartData(); // Reload after removal
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(response['message']),
            backgroundColor: Colors.green,
            duration: Duration(seconds: 2),
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
          content: Text('Failed to remove item'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  Future<void> _clearCart() async {
    if (_userId == null) return;

    // Show confirmation dialog
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Clear Cart'),
        content: Text('Are you sure you want to clear your entire cart? This action cannot be undone.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: Text('Clear Cart', style: TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );

    if (confirm != true) return;

    try {
      final response = await BuyerService.clearCart(userId: _userId!);

      if (response['success']) {
        _loadCartData(); // Reload cart data
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(response['message']),
            backgroundColor: Colors.green,
            duration: Duration(seconds: 2),
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
          content: Text('Failed to clear cart'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  Future<void> _checkout() async {
    if (_userId == null) return;

    // Show confirmation dialog
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Confirm Checkout'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('You are about to checkout all items in your cart:'),
            SizedBox(height: 12),
            Container(
              padding: EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.grey[100],
                borderRadius: BorderRadius.circular(8),
              ),
              child: Column(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('Total Items:'),
                      Text('${_summary?['total_items'] ?? 0}', style: TextStyle(fontWeight: FontWeight.bold)),
                    ],
                  ),
                  SizedBox(height: 4),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('Subtotal:'),
                      Text('₱${_formatPrice(_summary?['subtotal']?.toDouble() ?? 0)}'),
                    ],
                  ),
                  SizedBox(height: 4),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('Shipping Fee:'),
                      Text('₱${_formatPrice(_summary?['total_shipping']?.toDouble() ?? 0)}'),
                    ],
                  ),
                  Divider(),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('Total Amount:', style: TextStyle(fontWeight: FontWeight.bold)),
                      Text('₱${_formatPrice(_summary?['grand_total']?.toDouble() ?? 0)}', style: TextStyle(fontWeight: FontWeight.bold)),
                    ],
                  ),
                ],
              ),
            ),
            SizedBox(height: 12),
            Text('Payment Method: Cash on Delivery', style: TextStyle(color: Colors.grey[600], fontSize: 12)),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            child: Text('Checkout'),
            style: ElevatedButton.styleFrom(backgroundColor: Color(0xFF2196F3)),
          ),
        ],
      ),
    );

    if (confirm != true) return;

    try {
      final response = await BuyerService.checkout(userId: _userId!);

      if (response['success']) {
        _loadCartData(); // Reload cart data
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(response['message']),
            backgroundColor: Colors.green,
            duration: Duration(seconds: 3),
          ),
        );
      } else {
        String errorMessage = response['message'];
        if (response['errors'] != null) {
          errorMessage += '\n\nItems with issues:';
          for (String error in response['errors']) {
            errorMessage += '\n• $error';
          }
        }
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(errorMessage),
            backgroundColor: Colors.red,
            duration: Duration(seconds: 5),
          ),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Checkout failed. Please try again.'),
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

  @override
  Widget build(BuildContext context) {
    super.build(context); // Required for AutomaticKeepAliveClientMixin
    
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: Text('Shopping Cart'),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black,
        elevation: 1,
        automaticallyImplyLeading: false, // Remove back button since it's in tab navigation
        actions: [
          if (_shops.isNotEmpty)
            IconButton(
              onPressed: _clearCart,
              icon: Icon(Icons.delete_sweep, color: Colors.red),
            ),
          // Add refresh button
          IconButton(
            onPressed: _loadCartData,
            icon: Icon(Icons.refresh, color: Color(0xFF2196F3)),
          ),
        ],
      ),
      body: _buildBody(),
      bottomNavigationBar: _shops.isNotEmpty
          ? Container(
              padding: EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.1),
                    blurRadius: 4,
                    offset: Offset(0, -2),
                  ),
                ],
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        'Total (${_summary?['total_items'] ?? 0} items)',
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.grey[600],
                        ),
                      ),
                      Text(
                        '₱${_formatPrice(_summary?['grand_total']?.toDouble() ?? 0)}',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF2196F3),
                        ),
                      ),
                    ],
                  ),
                  
                  // Checkout button
                  SizedBox(
                    width: 160,
                    height: 48,
                    child: ElevatedButton.icon(
                      onPressed: _checkout,
                      icon: Icon(Icons.shopping_bag, color: Colors.white),
                      label: Text(
                        'Checkout',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Color(0xFF2196F3),
                        elevation: 0,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            )
          : null,
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
              onPressed: _loadCartData,
              child: Text('Retry'),
            ),
          ],
        ),
      );
    }

    if (_shops.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.shopping_cart_outlined,
              size: 80,
              color: Colors.grey[400],
            ),
            SizedBox(height: 20),
            Text(
              'Your cart is empty',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: Colors.grey[600],
              ),
            ),
            SizedBox(height: 8),
            Text(
              'Add some products to your cart to get started!',
              style: TextStyle(
                fontSize: 16,
                color: Colors.grey[500],
              ),
              textAlign: TextAlign.center,
            ),
            SizedBox(height: 24),
            ElevatedButton(
              onPressed: () {
                // Navigate to home tab instead of popping
                if (widget.onNavigateToHome != null) {
                  widget.onNavigateToHome!();
                } else {
                  // Fallback: try to pop if possible
                  if (Navigator.canPop(context)) {
                    Navigator.pop(context);
                  }
                }
              },
              child: Text('Continue Shopping'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Color(0xFF2196F3),
                foregroundColor: Colors.white,
                padding: EdgeInsets.symmetric(horizontal: 32, vertical: 12),
              ),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadCartData,
      child: ListView.builder(
        padding: EdgeInsets.only(bottom: 20),
        itemCount: _shops.length + (_buyerAddress != null ? 1 : 0),
        itemBuilder: (context, index) {
          if (index < _shops.length) {
            return _buildShopSection(_shops[index]);
          } else {
            return _buildAddressSection();
          }
        },
      ),
    );
  }

  Widget _buildShopSection(Map<String, dynamic> shop) {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
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
          // Shop Header
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
              children: [
                Icon(Icons.store, color: Color(0xFF2196F3), size: 20),
                SizedBox(width: 8),
                Text(
                  shop['shop_name'] ?? 'Unknown Shop',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF2196F3),
                  ),
                ),
              ],
            ),
          ),

          // Shop Items
          ...((shop['items'] as List<dynamic>? ?? []).map((item) => _buildCartItem(item)).toList()),

          // Shop Subtotal
          Container(
            padding: EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.grey[50],
              borderRadius: BorderRadius.only(
                bottomLeft: Radius.circular(12),
                bottomRight: Radius.circular(12),
              ),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Subtotal + Shipping',
                  style: TextStyle(fontWeight: FontWeight.w500),
                ),
                Text(
                  '₱${_formatPrice((shop['subtotal']?.toDouble() ?? 0) + (shop['shipping_fee']?.toDouble() ?? 0))}',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF2196F3),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCartItem(Map<String, dynamic> item) {
    return Container(
      padding: EdgeInsets.all(16),
      decoration: BoxDecoration(
        border: Border(bottom: BorderSide(color: Colors.grey[200]!)),
      ),
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
                    productInfoId: item['product_info_id'],
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
                child: item['image_base64'] != null
                    ? Image.memory(
                        base64Decode(item['image_base64'].split(',')[1]),
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

          // Product Details
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
                          productInfoId: item['product_info_id'],
                        ),
                      ),
                    );
                  },
                  child: Text(
                    item['product_name'] ?? 'Unknown Product',
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
                  '${item['variant']}, ${item['color']}',
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey[600],
                  ),
                ),
                SizedBox(height: 8),
                
                // Stock Status
                Container(
                  padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: _getStockStatusColor(item['stock_status']),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    _getStockStatusText(item['stock_status'], item['stock']),
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.white,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
                SizedBox(height: 12),

                // Price and Quantity Controls
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      '₱${_formatPrice(item['item_total']?.toDouble() ?? 0)}',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Colors.black87,
                      ),
                    ),
                    
                    // Quantity Controls
                    Row(
                      children: [
                        // Decrease button
                        GestureDetector(
                          onTap: item['quantity'] > 1 && item['stock_status'] != 'Out of Stock'
                              ? () => _updateQuantity(item['cart_id'], item['quantity'] - 1)
                              : null,
                          child: Container(
                            width: 32,
                            height: 32,
                            decoration: BoxDecoration(
                              color: item['quantity'] > 1 && item['stock_status'] != 'Out of Stock'
                                  ? Color(0xFF2196F3)
                                  : Colors.grey[300],
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: Icon(
                              Icons.remove,
                              color: Colors.white,
                              size: 16,
                            ),
                          ),
                        ),
                        
                        // Quantity display
                        Container(
                          width: 40,
                          height: 32,
                          decoration: BoxDecoration(
                            border: Border.symmetric(
                              horizontal: BorderSide(color: Colors.grey[300]!),
                            ),
                          ),
                          child: Center(
                            child: Text(
                              '${item['quantity']}',
                              style: TextStyle(
                                fontSize: 14,
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                          ),
                        ),
                        
                        // Increase button
                        GestureDetector(
                          onTap: item['quantity'] < item['stock'] && item['stock_status'] != 'Out of Stock'
                              ? () => _updateQuantity(item['cart_id'], item['quantity'] + 1)
                              : null,
                          child: Container(
                            width: 32,
                            height: 32,
                            decoration: BoxDecoration(
                              color: item['quantity'] < item['stock'] && item['stock_status'] != 'Out of Stock'
                                  ? Color(0xFF2196F3)
                                  : Colors.grey[300],
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: Icon(
                              Icons.add,
                              color: Colors.white,
                              size: 16,
                            ),
                          ),
                        ),
                        
                        SizedBox(width: 12),
                        
                        // Remove button
                        GestureDetector(
                          onTap: () => _removeItem(item['cart_id'], item['product_name']),
                          child: Container(
                            width: 32,
                            height: 32,
                            decoration: BoxDecoration(
                              color: Colors.red,
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: Icon(
                              Icons.delete,
                              color: Colors.white,
                              size: 16,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAddressSection() {
    if (_buyerAddress == null) return SizedBox.shrink();
    
    return Container(
      margin: EdgeInsets.all(16),
      padding: EdgeInsets.all(16),
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
          Row(
            children: [
              Icon(Icons.location_on, color: Color(0xFF2196F3)),
              SizedBox(width: 8),
              Text(
                'Delivery Location',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          SizedBox(height: 12),
          Text(
            '${_buyerAddress!['firstname']} ${_buyerAddress!['lastname']}',
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w500,
            ),
          ),
          SizedBox(height: 4),
          Text(
            '${_buyerAddress!['house_no']} ${_buyerAddress!['street']} Brgy. ${_buyerAddress!['barangay']}, ${_buyerAddress!['city']}, ${_buyerAddress!['province']}',
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey[600],
            ),
          ),
          if (_buyerAddress!['phone'] != null) ...[
            SizedBox(height: 4),
            Text(
              _buyerAddress!['phone'],
              style: TextStyle(
                fontSize: 14,
                color: Colors.grey[600],
              ),
            ),
          ],
        ],
      ),
    );
  }

  Color _getStockStatusColor(String? status) {
    switch (status) {
      case 'Out of Stock':
        return Colors.red;
      case 'Nearly Out of Stock':
        return Colors.orange;
      default:
        return Colors.green;
    }
  }

  String _getStockStatusText(String? status, int? stock) {
    switch (status) {
      case 'Out of Stock':
        return 'Out of Stock';
      case 'Nearly Out of Stock':
        return 'Low Stock ($stock left)';
      default:
        return 'In Stock';
    }
  }
} 