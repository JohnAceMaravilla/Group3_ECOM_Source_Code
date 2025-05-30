import 'package:flutter/material.dart';
import 'package:fenamaz_ecommerce_app/services/buyer_service.dart';
import 'package:fenamaz_ecommerce_app/services/user_session.dart';
import 'package:fenamaz_ecommerce_app/screens/buyer_product.dart';
import 'dart:convert';

class BuyerLikesScreen extends StatefulWidget {
  @override
  _BuyerLikesScreenState createState() => _BuyerLikesScreenState();
}

class _BuyerLikesScreenState extends State<BuyerLikesScreen> {
  List<dynamic> _likedProducts = [];
  bool _isLoading = true;
  String? _errorMessage;
  int? _userId;
  String _currentSort = 'recent';

  final List<Map<String, String>> _sortOptions = [
    {'value': 'recent', 'label': 'Most Recent'},
    {'value': 'oldest', 'label': 'Oldest'},
    {'value': 'name_asc', 'label': 'Name A-Z'},
    {'value': 'name_desc', 'label': 'Name Z-A'},
    {'value': 'price_low', 'label': 'Price Low to High'},
    {'value': 'price_high', 'label': 'Price High to Low'},
  ];

  @override
  void initState() {
    super.initState();
    _loadUserData();
  }

  Future<void> _loadUserData() async {
    final userData = await UserSession.getUserData();
    setState(() {
      _userId = userData?['user_id'] != null 
          ? int.tryParse(userData!['user_id'].toString()) 
          : null;
    });
    if (_userId != null) {
      _loadLikedProducts();
    } else {
      setState(() {
        _errorMessage = 'Please login to view your liked products';
        _isLoading = false;
      });
    }
  }

  Future<void> _loadLikedProducts() async {
    if (_userId == null) return;

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final response = await BuyerService.getLikedProducts(
        userId: _userId!,
        sort: _currentSort,
      );

      if (response['success']) {
        setState(() {
          _likedProducts = response['data'] ?? [];
          _isLoading = false;
        });
      } else {
        setState(() {
          _errorMessage = response['message'];
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Failed to load liked products';
        _isLoading = false;
      });
    }
  }

  Future<void> _removeLikedProduct(int productInfoId, int index) async {
    if (_userId == null) return;

    try {
      final response = await BuyerService.removeLikedProduct(
        productInfoId: productInfoId,
        userId: _userId!,
      );

      if (response['success']) {
        setState(() {
          _likedProducts.removeAt(index);
        });
        
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
          content: Text('Failed to remove product'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  void _showSortOptions() {
    showModalBottomSheet(
      context: context,
      builder: (BuildContext context) {
        return Container(
          padding: EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Sort By',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              SizedBox(height: 16),
              ...(_sortOptions.map((option) {
                final isSelected = _currentSort == option['value'];
                return ListTile(
                  title: Text(option['label']!),
                  trailing: isSelected 
                      ? Icon(Icons.check, color: Color(0xFF2196F3))
                      : null,
                  onTap: () {
                    Navigator.pop(context);
                    if (_currentSort != option['value']) {
                      setState(() {
                        _currentSort = option['value']!;
                      });
                      _loadLikedProducts();
                    }
                  },
                );
              }).toList()),
            ],
          ),
        );
      },
    );
  }

  String _formatPrice(double price) {
    return price.toInt().toString().replaceAllMapped(
      RegExp(r'(\d)(?=(\d{3})+(?!\d))'),
      (Match match) => '${match[1]},',
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: Text('Your Likes'),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black,
        elevation: 1,
        actions: [
          IconButton(
            onPressed: _showSortOptions,
            icon: Icon(Icons.sort),
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
              onPressed: _loadLikedProducts,
              child: Text('Retry'),
            ),
          ],
        ),
      );
    }

    if (_likedProducts.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.favorite_border,
              size: 80,
              color: Colors.grey[400],
            ),
            SizedBox(height: 20),
            Text(
              'No Liked Products Yet',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: Colors.grey[600],
              ),
            ),
            SizedBox(height: 8),
            Text(
              'Start exploring and like products to see them here!',
              style: TextStyle(
                fontSize: 16,
                color: Colors.grey[500],
              ),
              textAlign: TextAlign.center,
            ),
            SizedBox(height: 24),
            ElevatedButton(
              onPressed: () {
                Navigator.pop(context);
              },
              child: Text('Start Shopping'),
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
      onRefresh: _loadLikedProducts,
      child: Column(
        children: [
          // Header with count and sort info
          Container(
            padding: EdgeInsets.all(16),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'You have ${_likedProducts.length} liked product(s)',
                  style: TextStyle(
                    fontSize: 16,
                    color: Colors.grey[600],
                  ),
                ),
                Text(
                  _sortOptions.firstWhere(
                    (option) => option['value'] == _currentSort,
                    orElse: () => {'label': 'Recent'},
                  )['label']!,
                  style: TextStyle(
                    fontSize: 14,
                    color: Color(0xFF2196F3),
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),
          
          // Products Grid
          Expanded(
            child: Padding(
              padding: EdgeInsets.symmetric(horizontal: 16),
              child: GridView.builder(
                gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 2,
                  childAspectRatio: 0.62,
                  crossAxisSpacing: 12,
                  mainAxisSpacing: 12,
                ),
                itemCount: _likedProducts.length,
                itemBuilder: (context, index) {
                  final product = _likedProducts[index];
                  return _buildProductCard(product, index);
                },
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildProductCard(dynamic product, int index) {
    double minPrice = product['min_price']?.toDouble() ?? 0.0;
    double maxPrice = product['max_price']?.toDouble() ?? 0.0;
    double averageRating = product['average_rating']?.toDouble() ?? 0.0;

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
                GestureDetector(
                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => BuyerProductScreen(
                          productInfoId: product['product_info_id'],
                        ),
                      ),
                    );
                  },
                  child: Container(
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
                ),
                // Heart icon in upper right
                Positioned(
                  top: 8,
                  right: 8,
                  child: GestureDetector(
                    onTap: () => _removeLikedProduct(product['product_info_id'], index),
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
                        Icons.favorite,
                        color: Colors.red,
                        size: 18,
                      ),
                    ),
                  ),
                ),
              ],
            ),
            
            SizedBox(height: 12),
            
            // Product Name
            GestureDetector(
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => BuyerProductScreen(
                      productInfoId: product['product_info_id'],
                    ),
                  ),
                );
              },
              child: Text(
                product['product_name'] ?? 'Unknown Product',
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                  fontSize: 14,
                  color: Color(0xFF2196F3),
                ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
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
                // Total orders/sales info
                Text(
                  '${product['total_orders'] ?? 0} Sold',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[600],
                  ),
                ),
              ],
            ),
            
            SizedBox(height: 6),
            
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
} 