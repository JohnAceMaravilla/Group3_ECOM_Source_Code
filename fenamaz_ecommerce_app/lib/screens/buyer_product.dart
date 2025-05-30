import 'package:flutter/material.dart';
import 'package:fenamaz_ecommerce_app/services/buyer_service.dart';
import 'package:fenamaz_ecommerce_app/services/user_session.dart';
import 'dart:convert';

class BuyerProductScreen extends StatefulWidget {
  final int productInfoId;

  BuyerProductScreen({required this.productInfoId});

  @override
  _BuyerProductScreenState createState() => _BuyerProductScreenState();
}

class _BuyerProductScreenState extends State<BuyerProductScreen> {
  Map<String, dynamic>? _productData;
  bool _isLoading = true;
  String? _errorMessage;
  int? _userId;
  
  // Selection state
  String? _selectedVariant;
  String? _selectedColor;
  int _quantity = 1;
  int _maxStock = 0;
  double _selectedPrice = 0;
  
  // Image carousel
  int _currentImageIndex = 0;
  List<String> _allImages = [];

  @override
  void initState() {
    super.initState();
    _loadUserData();
    _loadProductDetails();
  }

  Future<void> _loadUserData() async {
    final userData = await UserSession.getUserData();
    setState(() {
      _userId = userData?['user_id'] != null 
          ? int.tryParse(userData!['user_id'].toString()) 
          : null;
    });
  }

  Future<void> _loadProductDetails() async {
    try {
      final response = await BuyerService.getProductDetails(
        productInfoId: widget.productInfoId,
        userId: _userId,
      );

      if (response['status'] == 'success') {
        setState(() {
          _productData = response['data'];
          _prepareImagesList();
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
        _errorMessage = 'Failed to load product: $e';
        _isLoading = false;
      });
    }
  }

  void _prepareImagesList() {
    _allImages.clear();
    
    // Add main image
    if (_productData!['main_image_base64'] != null) {
      _allImages.add(_productData!['main_image_base64']);
    }
    
    // Add additional images
    final images = _productData!['images'] as List<dynamic>? ?? [];
    for (var image in images) {
      if (image['image_base64'] != null) {
        _allImages.add(image['image_base64']);
      }
    }
    
    if (_allImages.isEmpty) {
      _allImages.add(''); // Placeholder for no image
    }
  }

  Future<void> _toggleLike() async {
    if (_userId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Please login to like products'),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }

    try {
      final response = await BuyerService.toggleProductInfoLike(
        widget.productInfoId, 
        _userId!
      );
      
      if (response['success']) {
        setState(() {
          _productData!['is_liked'] = response['data']['is_liked'];
        });
        
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

  void _selectVariant(String variant) {
    setState(() {
      _selectedVariant = variant;
      _selectedColor = null; // Reset color selection
      _quantity = 1;
      _maxStock = 0;
      _selectedPrice = 0;
    });
  }

  void _selectColor(String color) {
    final variants = _productData!['variants'] as Map<String, dynamic>;
    final colorOptions = variants[_selectedVariant] as List<dynamic>;
    
    for (var option in colorOptions) {
      if (option['color'] == color) {
        setState(() {
          _selectedColor = color;
          _maxStock = option['stock'];
          _selectedPrice = option['price'].toDouble();
          _quantity = 1; // Reset quantity when changing color
        });
        break;
      }
    }
  }

  Future<void> _addToCart() async {
    if (_userId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Please login to add products to cart'),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }

    if (_selectedVariant == null || _selectedColor == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Please select variant and color'),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }

    try {
      final response = await BuyerService.addToCart(
        userId: _userId!,
        productInfoId: widget.productInfoId,
        variant: _selectedVariant!,
        color: _selectedColor!,
        quantity: _quantity,
      );

      if (response['status'] == 'success') {
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
          content: Text('Failed to add to cart'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  Future<void> _toggleShopProductLike(int productId, int index) async {
    if (_userId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Please login to like products'),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }

    try {
      final response = await BuyerService.toggleProductLike(productId, _userId!);
      
      if (response['success']) {
        setState(() {
          final shopProducts = _productData!['shop_products'] as List<dynamic>;
          shopProducts[index]['is_liked'] = response['data']['is_liked'];
        });
        
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

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Scaffold(
        appBar: AppBar(title: Text('Product Details')),
        body: Center(child: CircularProgressIndicator()),
      );
    }

    if (_errorMessage != null || _productData == null) {
      return Scaffold(
        appBar: AppBar(title: Text('Product Details')),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.error_outline, size: 64, color: Colors.grey),
              SizedBox(height: 16),
              Text(_errorMessage ?? 'Product not found'),
              SizedBox(height: 16),
              ElevatedButton(
                onPressed: _loadProductDetails,
                child: Text('Retry'),
              ),
            ],
          ),
        ),
      );
    }

    final variants = _productData!['variants'] as Map<String, dynamic>;
    final specs = _productData!['specs'] as List<dynamic>;
    final shop = _productData!['shop'] as Map<String, dynamic>;
    final shopProducts = _productData!['shop_products'] as List<dynamic>;
    
    final canAddToCart = _selectedVariant != null && 
                        _selectedColor != null && 
                        _maxStock > 0;

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: Text(_productData!['product_name']),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black,
        elevation: 1,
        actions: [
          IconButton(
            onPressed: _toggleLike,
            icon: Icon(
              _productData!['is_liked'] == true
                  ? Icons.favorite
                  : Icons.favorite_border,
              color: _productData!['is_liked'] == true
                  ? Colors.red
                  : Colors.grey[600],
            ),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: EdgeInsets.only(bottom: 80), // Add padding for fixed button
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Image Gallery
            _buildImageGallery(),
            
            // Product Info
            Padding(
              padding: EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Rating
                  _buildRating(),
                  
                  SizedBox(height: 12),
                  
                  // Product Name
                  Text(
                    _productData!['product_name'],
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: Colors.black87,
                    ),
                  ),
                  
                  SizedBox(height: 16),
                  
                  // Price
                  _buildPriceDisplay(),
                  
                  SizedBox(height: 24),
                  
                  // Variants
                  _buildVariantSelection(),
                  
                  SizedBox(height: 20),
                  
                  // Colors
                  if (_selectedVariant != null) _buildColorSelection(),
                  
                  SizedBox(height: 20),
                  
                  // Stock and Quantity
                  if (_selectedColor != null) _buildStockAndQuantity(),
                ],
              ),
            ),
            
            // Description and Specs
            _buildDescriptionAndSpecs(specs),
            
            // Shop Info
            _buildShopInfo(shop),
            
            // More Products from Shop
            if (shopProducts.isNotEmpty) _buildShopProducts(shopProducts),
          ],
        ),
      ),
      // Fixed Add to Cart Button at bottom
      bottomNavigationBar: Container(
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
        child: SizedBox(
          width: double.infinity,
          height: 50,
          child: ElevatedButton.icon(
            onPressed: canAddToCart ? _addToCart : null,
            icon: Icon(Icons.shopping_cart, color: Colors.white),
            label: Text(
              'Add to Cart',
              style: TextStyle(
                color: Colors.white,
                fontSize: 16,
                fontWeight: FontWeight.w600,
              ),
            ),
            style: ElevatedButton.styleFrom(
              backgroundColor: canAddToCart ? Color(0xFF2196F3) : Colors.grey[400],
              elevation: 0,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildImageGallery() {
    return Container(
      height: 300,
      child: Stack(
        children: [
          // Main Image
          PageView.builder(
            itemCount: _allImages.length,
            onPageChanged: (index) {
              setState(() {
                _currentImageIndex = index;
              });
            },
            itemBuilder: (context, index) {
              return Container(
                width: double.infinity,
                decoration: BoxDecoration(
                  color: Colors.grey[100],
                ),
                child: _allImages[index].isNotEmpty
                    ? Image.memory(
                        base64Decode(_allImages[index].split(',')[1]),
                        fit: BoxFit.cover,
                        errorBuilder: (context, error, stackTrace) {
                          return Center(
                            child: Icon(Icons.image, size: 64, color: Colors.grey[400]),
                          );
                        },
                      )
                    : Center(
                        child: Icon(Icons.image, size: 64, color: Colors.grey[400]),
                      ),
              );
            },
          ),
          
          // Image indicators
          if (_allImages.length > 1)
            Positioned(
              bottom: 16,
              left: 0,
              right: 0,
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: List.generate(_allImages.length, (index) {
                  return Container(
                    margin: EdgeInsets.symmetric(horizontal: 4),
                    width: 8,
                    height: 8,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: _currentImageIndex == index
                          ? Colors.white
                          : Colors.white.withOpacity(0.5),
                    ),
                  );
                }),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildRating() {
    final rating = (_productData!['average_rating'] ?? 0).toDouble();
    final totalRatings = _productData!['total_ratings'] ?? 0;
    
    return Row(
      children: [
        Row(
          children: List.generate(5, (index) {
            return Icon(
              index < rating.floor()
                  ? Icons.star
                  : Icons.star_border,
              color: Colors.amber,
              size: 20,
            );
          }),
        ),
        SizedBox(width: 8),
        Text(
          '$rating',
          style: TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
        ),
        SizedBox(width: 4),
        Text(
          '($totalRatings reviews)',
          style: TextStyle(fontSize: 14, color: Colors.grey[600]),
        ),
      ],
    );
  }

  Widget _buildPriceDisplay() {
    return Text(
      _selectedPrice > 0 
          ? '₱${_formatPrice(_selectedPrice)}'
          : 'Select variant to see price',
      style: TextStyle(
        fontSize: 20,
        fontWeight: FontWeight.bold,
        color: Color(0xFF2196F3),
      ),
    );
  }

  Widget _buildVariantSelection() {
    final variants = _productData!['variants'] as Map<String, dynamic>;
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Variant:',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w600,
            color: Colors.grey[700],
          ),
        ),
        SizedBox(height: 8),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: variants.keys.map((variant) {
            final isSelected = _selectedVariant == variant;
            return GestureDetector(
              onTap: () => _selectVariant(variant),
              child: Container(
                padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                decoration: BoxDecoration(
                  color: isSelected ? Color(0xFF2196F3) : Colors.white,
                  border: Border.all(
                    color: isSelected ? Color(0xFF2196F3) : Colors.grey[300]!,
                  ),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  variant,
                  style: TextStyle(
                    color: isSelected ? Colors.white : Colors.black87,
                    fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
                  ),
                ),
              ),
            );
          }).toList(),
        ),
      ],
    );
  }

  Widget _buildColorSelection() {
    final variants = _productData!['variants'] as Map<String, dynamic>;
    final colorOptions = variants[_selectedVariant] as List<dynamic>;
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Color:',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w600,
            color: Colors.grey[700],
          ),
        ),
        SizedBox(height: 8),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: colorOptions.map<Widget>((option) {
            final color = option['color'];
            final stock = option['stock'];
            final isSelected = _selectedColor == color;
            final isOutOfStock = stock == 0;
            
            return GestureDetector(
              onTap: isOutOfStock ? null : () => _selectColor(color),
              child: Container(
                padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                decoration: BoxDecoration(
                  color: isOutOfStock 
                      ? Colors.grey[100]
                      : isSelected 
                          ? Color(0xFF2196F3) 
                          : Colors.white,
                  border: Border.all(
                    color: isOutOfStock
                        ? Colors.grey[300]!
                        : isSelected 
                            ? Color(0xFF2196F3) 
                            : Colors.grey[300]!,
                  ),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  '$color (Stock: $stock)',
                  style: TextStyle(
                    color: isOutOfStock
                        ? Colors.grey[500]
                        : isSelected 
                            ? Colors.white 
                            : Colors.black87,
                    fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
                  ),
                ),
              ),
            );
          }).toList(),
        ),
      ],
    );
  }

  Widget _buildStockAndQuantity() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Available Stock: $_maxStock items',
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w600,
            color: _maxStock > 0 ? Color(0xFF2196F3) : Colors.red,
          ),
        ),
        SizedBox(height: 12),
        Row(
          children: [
            Text(
              'Quantity:',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: Colors.grey[700],
              ),
            ),
            SizedBox(width: 16),
            Container(
              decoration: BoxDecoration(
                border: Border.all(color: Colors.grey[300]!),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  IconButton(
                    onPressed: _quantity > 1 
                        ? () => setState(() => _quantity--) 
                        : null,
                    icon: Icon(Icons.remove, size: 18),
                    constraints: BoxConstraints(minWidth: 32, minHeight: 32),
                  ),
                  Container(
                    padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    child: Text(
                      '$_quantity',
                      style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                    ),
                  ),
                  IconButton(
                    onPressed: _quantity < _maxStock 
                        ? () => setState(() => _quantity++) 
                        : null,
                    icon: Icon(Icons.add, size: 18),
                    constraints: BoxConstraints(minWidth: 32, minHeight: 32),
                  ),
                ],
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildDescriptionAndSpecs(List<dynamic> specs) {
    return Container(
      margin: EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Description
          Container(
            width: double.infinity,
            padding: EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.grey[50],
              borderRadius: BorderRadius.circular(8),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Description',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.black87,
                  ),
                ),
                SizedBox(height: 12),
                Text(
                  _productData!['product_description'] ?? 'No description available',
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.black87,
                    height: 1.5,
                  ),
                ),
              ],
            ),
          ),
          
          SizedBox(height: 16),
          
          // Specifications
          if (specs.isNotEmpty)
            Container(
              width: double.infinity,
              padding: EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.grey[50],
                borderRadius: BorderRadius.circular(8),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Specifications',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Colors.black87,
                    ),
                  ),
                  SizedBox(height: 12),
                  ...specs.map((spec) => Padding(
                    padding: EdgeInsets.only(bottom: 8),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        RichText(
                          text: TextSpan(
                            children: [
                              TextSpan(
                                text: '${spec['specs_type'] ?? ''}: ',
                                style: TextStyle(
                                  fontSize: 14,
                                  fontWeight: FontWeight.w600,
                                  color: Colors.black87,
                                ),
                              ),
                              TextSpan(
                                text: spec['specs_content'] ?? '',
                                style: TextStyle(
                                  fontSize: 14,
                                  color: Colors.black87,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  )).toList(),
                ],
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildShopInfo(Map<String, dynamic> shop) {
    return Container(
      margin: EdgeInsets.all(16),
      padding: EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[50],
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          // Shop Image
          Container(
            width: 60,
            height: 60,
            decoration: BoxDecoration(
              color: Colors.grey[200],
              borderRadius: BorderRadius.circular(8),
            ),
            child: shop['shop_image_base64'] != null
                ? ClipRRect(
                    borderRadius: BorderRadius.circular(8),
                    child: Image.memory(
                      base64Decode(shop['shop_image_base64'].split(',')[1]),
                      fit: BoxFit.cover,
                      errorBuilder: (context, error, stackTrace) {
                        return Icon(Icons.store, size: 30, color: Colors.grey[400]);
                      },
                    ),
                  )
                : Icon(Icons.store, size: 30, color: Colors.grey[400]),
          ),
          
          SizedBox(width: 16),
          
          // Shop Info
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  shop['shop_name'] ?? 'Unknown Shop',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.black87,
                  ),
                ),
                SizedBox(height: 4),
                Text(
                  'Seller: ${shop['seller_name'] ?? 'Unknown'}',
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey[600],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildShopProducts(List<dynamic> shopProducts) {
    return Container(
      margin: EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'More Products from this Shop',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Colors.black87,
            ),
          ),
          SizedBox(height: 16),
          GridView.builder(
            shrinkWrap: true,
            physics: NeverScrollableScrollPhysics(),
            gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 2,
              childAspectRatio: 0.62, // Same as categories
              crossAxisSpacing: 12,
              mainAxisSpacing: 12,
            ),
            itemCount: shopProducts.length,
            itemBuilder: (context, index) {
              final product = shopProducts[index];
              double minPrice = product['min_price']?.toDouble() ?? 0.0;
              double maxPrice = product['max_price']?.toDouble() ?? 0.0;

              return GestureDetector(
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
                child: Card(
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
                                onTap: () => _toggleShopProductLike(product['product_info_id'], index),
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
                            // Single star with rating - default to 0 if no rating data
                            Row(
                              children: [
                                Icon(Icons.star, color: Colors.amber, size: 16),
                                SizedBox(width: 4),
                                Text(
                                  '0.0', // Shop products don't have rating in current API
                                  style: TextStyle(
                                    fontSize: 12,
                                    color: Colors.grey[600],
                                  ),
                                ),
                              ],
                            ),
                            // Sales info - show number sold if available
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
                ),
              );
            },
          ),
        ],
      ),
    );
  }
} 