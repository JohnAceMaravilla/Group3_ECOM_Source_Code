import 'package:flutter/material.dart';
import 'package:fenamaz_ecommerce_app/services/buyer_service.dart';
import 'package:fenamaz_ecommerce_app/services/user_session.dart';
import 'package:fenamaz_ecommerce_app/screens/buyer_product.dart';
import 'dart:convert';

class BuyerSearchScreen extends StatefulWidget {
  final String? initialQuery;
  
  BuyerSearchScreen({this.initialQuery});

  @override
  _BuyerSearchScreenState createState() => _BuyerSearchScreenState();
}

class _BuyerSearchScreenState extends State<BuyerSearchScreen> {
  final TextEditingController _searchController = TextEditingController();
  List<dynamic> _products = [];
  List<dynamic> _categories = [];
  bool _isLoading = false;
  bool _isInitialLoad = true;
  String? _errorMessage;
  int? _userId;
  
  // Filter and pagination
  String _sortBy = 'recent';
  String _pendingSortBy = 'recent';
  double _minPrice = 0;
  double _maxPrice = 0;
  double _pendingMinPrice = 0;
  double _pendingMaxPrice = 0;
  String _selectedCategory = '';
  String _pendingSelectedCategory = '';
  int _currentPage = 1;
  int _itemsPerPage = 20;
  bool _hasMoreProducts = true;
  String _currentQuery = '';

  // Price range options
  final List<Map<String, dynamic>> _priceOptions = [
    {'value': 0.0, 'label': '₱ 0'},
    {'value': 100.0, 'label': '₱ 100'},
    {'value': 200.0, 'label': '₱ 200'},
    {'value': 500.0, 'label': '₱ 500'},
    {'value': 1000.0, 'label': '₱ 1,000'},
    {'value': 5000.0, 'label': '₱ 5,000'},
    {'value': 10000.0, 'label': '₱ 10,000'},
    {'value': 20000.0, 'label': '₱ 20,000'},
    {'value': 30000.0, 'label': '₱ 30,000'},
    {'value': 40000.0, 'label': '₱ 40,000'},
    {'value': 50000.0, 'label': '₱ 50,000'},
    {'value': 60000.0, 'label': '₱ 60,000'},
    {'value': 70000.0, 'label': '₱ 70,000'},
    {'value': 80000.0, 'label': '₱ 80,000'},
    {'value': 90000.0, 'label': '₱ 90,000'},
    {'value': 100000.0, 'label': '₱ 100,000+'},
  ];

  @override
  void initState() {
    super.initState();
    _loadUserData();
    _loadCategories();
    
    // Set initial query if provided
    if (widget.initialQuery != null && widget.initialQuery!.isNotEmpty) {
      _searchController.text = widget.initialQuery!;
      _currentQuery = widget.initialQuery!;
      // Perform initial search after a short delay to ensure everything is loaded
      Future.delayed(Duration(milliseconds: 500), () {
        if (mounted) {
          _searchProducts(refresh: true);
        }
      });
    }
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _loadUserData() async {
    final userData = await UserSession.getUserData();
    setState(() {
      _userId = userData?['user_id'] != null 
          ? int.tryParse(userData!['user_id'].toString()) 
          : null;
    });
  }

  Future<void> _loadCategories() async {
    try {
      final response = await BuyerService.getSearchCategories();
      
      if (response['success']) {
        setState(() {
          _categories = response['data'] ?? [];
          _isInitialLoad = false;
        });
      }
    } catch (e) {
      setState(() {
        _isInitialLoad = false;
      });
    }
  }

  Future<void> _searchProducts({bool refresh = false}) async {
    if (refresh) {
      setState(() {
        _products.clear();
        _currentPage = 1;
        _hasMoreProducts = true;
        _isLoading = true;
        _errorMessage = null;
      });
    } else {
      setState(() {
        _isLoading = true;
      });
    }

    try {
      final response = await BuyerService.searchProductsAdvanced(
        query: _currentQuery.isNotEmpty ? _currentQuery : null,
        category: _selectedCategory.isNotEmpty ? _selectedCategory : null,
        userId: _userId,
        limit: _itemsPerPage,
        offset: (_currentPage - 1) * _itemsPerPage,
        minPrice: _minPrice,
        maxPrice: _maxPrice,
        sort: _sortBy,
      );

      if (response['success']) {
        final newProducts = response['data'] as List<dynamic>;
        setState(() {
          if (refresh) {
            _products = newProducts;
          } else {
            _products.addAll(newProducts);
          }
          _hasMoreProducts = newProducts.length == _itemsPerPage;
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
        _errorMessage = 'Failed to search products: $e';
        _isLoading = false;
      });
    }
  }

  Future<void> _loadMoreProducts() async {
    if (!_hasMoreProducts || _isLoading) return;
    
    setState(() {
      _currentPage++;
    });
    
    await _searchProducts();
  }

  void _performSearch() {
    setState(() {
      _currentQuery = _searchController.text.trim();
    });
    _searchProducts(refresh: true);
  }

  void _clearSearch() {
    setState(() {
      _searchController.clear();
      _currentQuery = '';
      _selectedCategory = '';
      _minPrice = 0;
      _maxPrice = 0;
      _sortBy = 'recent';
      _products.clear();
    });
  }

  Future<void> _toggleProductLike(int productId, int index) async {
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
          _products[index]['is_liked'] = response['data']['is_liked'];
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

  void _showFilterBottomSheet() {
    // Reset pending state to current applied state when opening filter
    _pendingSortBy = _sortBy;
    _pendingMinPrice = _minPrice;
    _pendingMaxPrice = _maxPrice;
    _pendingSelectedCategory = _selectedCategory;
    
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (context) => StatefulBuilder(
        builder: (context, setStateModal) => Container(
          padding: EdgeInsets.all(16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Filter & Sort',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  IconButton(
                    onPressed: () => Navigator.pop(context),
                    icon: Icon(Icons.close),
                  ),
                ],
              ),
              SizedBox(height: 16),
              
              // Category filter
              Text('Category:', style: TextStyle(fontWeight: FontWeight.w600)),
              SizedBox(height: 8),
              Container(
                width: double.infinity,
                padding: EdgeInsets.symmetric(horizontal: 12),
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.grey[300]!),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: DropdownButtonHideUnderline(
                  child: DropdownButton<String>(
                    value: _pendingSelectedCategory.isEmpty ? null : _pendingSelectedCategory,
                    hint: Text('All Categories'),
                    isExpanded: true,
                    onChanged: (value) {
                      setStateModal(() {
                        _pendingSelectedCategory = value ?? '';
                      });
                    },
                    items: [
                      DropdownMenuItem<String>(
                        value: '',
                        child: Text('All Categories'),
                      ),
                      ..._categories.map<DropdownMenuItem<String>>((category) {
                        return DropdownMenuItem<String>(
                          value: category['product_category'],
                          child: Text(
                            '${category['product_category']} (${category['product_count']})',
                            style: TextStyle(fontSize: 14),
                          ),
                        );
                      }).toList(),
                    ],
                  ),
                ),
              ),
              
              SizedBox(height: 20),
              
              // Sort options
              Text('Sort By:', style: TextStyle(fontWeight: FontWeight.w600)),
              SizedBox(height: 8),
              Wrap(
                spacing: 8,
                children: [
                  _buildSortChip('recent', 'Most Recent', setStateModal),
                  _buildSortChip('price_low', 'Price: Low to High', setStateModal),
                  _buildSortChip('price_high', 'Price: High to Low', setStateModal),
                  _buildSortChip('rating', 'Highest Rated', setStateModal),
                  _buildSortChip('popular', 'Most Popular', setStateModal),
                ],
              ),
              
              SizedBox(height: 20),
              
              // Price range
              Text('Price Range:', style: TextStyle(fontWeight: FontWeight.w600)),
              SizedBox(height: 8),
              Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Min Price', style: TextStyle(fontSize: 12, color: Colors.grey[600])),
                        SizedBox(height: 4),
                        Container(
                          padding: EdgeInsets.symmetric(horizontal: 12),
                          decoration: BoxDecoration(
                            border: Border.all(color: Colors.grey[300]!),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: DropdownButtonHideUnderline(
                            child: DropdownButton<double>(
                              value: _pendingMinPrice,
                              isExpanded: true,
                              onChanged: (value) {
                                setStateModal(() {
                                  _pendingMinPrice = value!;
                                  if (_pendingMaxPrice > 0 && _pendingMaxPrice < _pendingMinPrice) {
                                    _pendingMaxPrice = _pendingMinPrice;
                                  }
                                });
                              },
                              items: _priceOptions.map<DropdownMenuItem<double>>((option) {
                                return DropdownMenuItem<double>(
                                  value: option['value'],
                                  child: Text(option['label'], style: TextStyle(fontSize: 14)),
                                );
                              }).toList(),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                  SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Max Price', style: TextStyle(fontSize: 12, color: Colors.grey[600])),
                        SizedBox(height: 4),
                        Container(
                          padding: EdgeInsets.symmetric(horizontal: 12),
                          decoration: BoxDecoration(
                            border: Border.all(color: Colors.grey[300]!),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: DropdownButtonHideUnderline(
                            child: DropdownButton<double>(
                              value: _pendingMaxPrice,
                              isExpanded: true,
                              onChanged: (value) {
                                setStateModal(() {
                                  _pendingMaxPrice = value!;
                                  if (_pendingMaxPrice > 0 && _pendingMinPrice > _pendingMaxPrice) {
                                    _pendingMinPrice = _pendingMaxPrice;
                                  }
                                });
                              },
                              items: _priceOptions.map<DropdownMenuItem<double>>((option) {
                                return DropdownMenuItem<double>(
                                  value: option['value'],
                                  child: Text(option['label'], style: TextStyle(fontSize: 14)),
                                );
                              }).toList(),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              
              SizedBox(height: 20),
              
              // Apply and Clear buttons
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton(
                      onPressed: () {
                        setStateModal(() {
                          _pendingSortBy = 'recent';
                          _pendingMinPrice = 0;
                          _pendingMaxPrice = 0;
                          _pendingSelectedCategory = '';
                        });
                      },
                      style: OutlinedButton.styleFrom(
                        padding: EdgeInsets.symmetric(vertical: 12),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                      ),
                      child: Text('Clear'),
                    ),
                  ),
                  SizedBox(width: 12),
                  Expanded(
                    flex: 2,
                    child: ElevatedButton(
                      onPressed: () {
                        setState(() {
                          _sortBy = _pendingSortBy;
                          _minPrice = _pendingMinPrice;
                          _maxPrice = _pendingMaxPrice;
                          _selectedCategory = _pendingSelectedCategory;
                        });
                        Navigator.pop(context);
                        _searchProducts(refresh: true);
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Color(0xFF2196F3),
                        padding: EdgeInsets.symmetric(vertical: 12),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                      ),
                      child: Text('Apply Filters', style: TextStyle(color: Colors.white)),
                    ),
                  ),
                ],
              ),
              
              SizedBox(height: MediaQuery.of(context).viewInsets.bottom),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSortChip(String value, String label, StateSetter setStateModal) {
    bool isActive = _sortBy == value;
    bool isPending = _pendingSortBy == value && _pendingSortBy != _sortBy;
    
    return FilterChip(
      label: Text(
        label,
        style: TextStyle(
          color: isActive 
              ? Colors.white 
              : isPending 
                  ? Color(0xFF2196F3)
                  : Colors.black87,
          fontWeight: isActive || isPending ? FontWeight.w600 : FontWeight.normal,
        ),
      ),
      selected: isActive,
      onSelected: (selected) {
        if (selected) {
          setStateModal(() {
            _pendingSortBy = value;
          });
        }
      },
      selectedColor: Color(0xFF2196F3),
      backgroundColor: isPending 
          ? Color(0xFF2196F3).withOpacity(0.1)
          : Colors.grey[100],
      checkmarkColor: Colors.white,
      side: isPending 
          ? BorderSide(color: Color(0xFF2196F3), width: 1.5)
          : BorderSide.none,
    );
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
      appBar: AppBar(
        title: Text('Search Products'),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black,
        elevation: 1,
        actions: [
          IconButton(
            onPressed: _showFilterBottomSheet,
            icon: Icon(Icons.filter_list),
          ),
        ],
      ),
      body: Column(
        children: [
          // Search Bar
          Container(
            padding: EdgeInsets.all(16),
            color: Colors.white,
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _searchController,
                    decoration: InputDecoration(
                      hintText: 'Search products...',
                      prefixIcon: Icon(Icons.search, color: Colors.grey[600]),
                      suffixIcon: _searchController.text.isNotEmpty
                          ? IconButton(
                              onPressed: _clearSearch,
                              icon: Icon(Icons.clear, color: Colors.grey[600]),
                            )
                          : null,
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: BorderSide(color: Colors.grey[300]!),
                      ),
                      enabledBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: BorderSide(color: Colors.grey[300]!),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: BorderSide(color: Color(0xFF2196F3)),
                      ),
                      filled: true,
                      fillColor: Colors.grey[50],
                    ),
                    onSubmitted: (_) => _performSearch(),
                  ),
                ),
                SizedBox(width: 12),
                ElevatedButton(
                  onPressed: _performSearch,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Color(0xFF2196F3),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    padding: EdgeInsets.symmetric(horizontal: 20, vertical: 16),
                  ),
                  child: Text('Search', style: TextStyle(color: Colors.white)),
                ),
              ],
            ),
          ),
          
          // Applied Filters Display
          if (_selectedCategory.isNotEmpty || _minPrice > 0 || _maxPrice > 0 || _sortBy != 'recent')
            Container(
              padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              color: Colors.grey[50],
              child: SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: Row(
                  children: [
                    Text('Filters: ', style: TextStyle(fontWeight: FontWeight.w500)),
                    if (_selectedCategory.isNotEmpty) ...[
                      Chip(
                        label: Text(_selectedCategory),
                        backgroundColor: Color(0xFF2196F3).withOpacity(0.1),
                        deleteIcon: Icon(Icons.close, size: 16),
                        onDeleted: () {
                          setState(() {
                            _selectedCategory = '';
                          });
                          _searchProducts(refresh: true);
                        },
                      ),
                      SizedBox(width: 8),
                    ],
                    if (_minPrice > 0 || _maxPrice > 0) ...[
                      Chip(
                        label: Text(_maxPrice > 0 
                            ? '₱${_formatPrice(_minPrice)}-₱${_formatPrice(_maxPrice)}'
                            : '₱${_formatPrice(_minPrice)}+'),
                        backgroundColor: Color(0xFF2196F3).withOpacity(0.1),
                        deleteIcon: Icon(Icons.close, size: 16),
                        onDeleted: () {
                          setState(() {
                            _minPrice = 0;
                            _maxPrice = 0;
                          });
                          _searchProducts(refresh: true);
                        },
                      ),
                      SizedBox(width: 8),
                    ],
                    if (_sortBy != 'recent') ...[
                      Chip(
                        label: Text(_getSortLabel(_sortBy)),
                        backgroundColor: Color(0xFF2196F3).withOpacity(0.1),
                        deleteIcon: Icon(Icons.close, size: 16),
                        onDeleted: () {
                          setState(() {
                            _sortBy = 'recent';
                          });
                          _searchProducts(refresh: true);
                        },
                      ),
                    ],
                  ],
                ),
              ),
            ),
          
          // Results
          Expanded(
            child: _isInitialLoad
                ? Center(child: CircularProgressIndicator())
                : _products.isEmpty && !_isLoading
                    ? _buildEmptyState()
                    : _buildProductGrid(),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    if (_currentQuery.isEmpty && _selectedCategory.isEmpty && _minPrice == 0 && _maxPrice == 0) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.search, size: 64, color: Colors.grey[400]),
            SizedBox(height: 16),
            Text(
              'Search for products',
              style: TextStyle(fontSize: 18, color: Colors.grey[600]),
            ),
            SizedBox(height: 8),
            Text(
              'Enter a product name, category, or use filters',
              style: TextStyle(fontSize: 14, color: Colors.grey[500]),
            ),
          ],
        ),
      );
    } else {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.search_off, size: 64, color: Colors.grey[400]),
            SizedBox(height: 16),
            Text(
              'No products found',
              style: TextStyle(fontSize: 18, color: Colors.grey[600]),
            ),
            SizedBox(height: 8),
            Text(
              'Try adjusting your search or filters',
              style: TextStyle(fontSize: 14, color: Colors.grey[500]),
            ),
            SizedBox(height: 16),
            ElevatedButton(
              onPressed: _clearSearch,
              child: Text('Clear Search'),
            ),
          ],
        ),
      );
    }
  }

  Widget _buildProductGrid() {
    return RefreshIndicator(
      onRefresh: () => _searchProducts(refresh: true),
      child: NotificationListener<ScrollNotification>(
        onNotification: (ScrollNotification scrollInfo) {
          if (scrollInfo.metrics.pixels == scrollInfo.metrics.maxScrollExtent) {
            _loadMoreProducts();
          }
          return false;
        },
        child: GridView.builder(
          padding: EdgeInsets.all(16),
          gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 2,
            childAspectRatio: 0.62,
            crossAxisSpacing: 12,
            mainAxisSpacing: 12,
          ),
          itemCount: _products.length + (_hasMoreProducts ? 1 : 0),
          itemBuilder: (context, index) {
            if (index >= _products.length) {
              return Center(child: CircularProgressIndicator());
            }
            
            final product = _products[index];
            return _buildProductCard(product, index);
          },
        ),
      ),
    );
  }

  Widget _buildProductCard(dynamic product, int index) {
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
                    onTap: () => _toggleProductLike(product['product_info_id'], index),
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

  String _getSortLabel(String sort) {
    switch (sort) {
      case 'price_low':
        return 'Price: Low to High';
      case 'price_high':
        return 'Price: High to Low';
      case 'rating':
        return 'Highest Rated';
      case 'popular':
        return 'Most Popular';
      default:
        return 'Most Recent';
    }
  }
}
