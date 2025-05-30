import 'package:flutter/material.dart';
import 'package:fenamaz_ecommerce_app/services/buyer_service.dart';
import 'package:fenamaz_ecommerce_app/screens/buyer_category_products.dart';

class BuyerCategoriesScreen extends StatefulWidget {
  @override
  _BuyerCategoriesScreenState createState() => _BuyerCategoriesScreenState();
}

class _BuyerCategoriesScreenState extends State<BuyerCategoriesScreen> {
  List<dynamic> _categories = [];
  bool _isLoading = true;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _loadCategories();
  }

  Future<void> _loadCategories() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final response = await BuyerService.getCategories();
      
      if (response['success']) {
        setState(() {
          _categories = response['data'] ?? [];
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
        _errorMessage = 'Failed to load categories';
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Center(child: CircularProgressIndicator());
    }

    return Padding(
      padding: EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Shop by Category',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
          ),
          SizedBox(height: 20),
          Expanded(
            child: _categories.isEmpty
                ? Center(
                    child: Text(
                      'No categories available',
                      style: TextStyle(color: Colors.grey[600]),
                    ),
                  )
                : GridView.builder(
                    gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: 2,
                      crossAxisSpacing: 12,
                      mainAxisSpacing: 12,
                      childAspectRatio: 1.0,
                    ),
                    itemCount: _categories.length,
                    itemBuilder: (context, index) {
                      final category = _categories[index];
                      return _buildCategoryCard(
                        category['product_category'] ?? 'Unknown',
                        _getCategoryIcon(category['product_category']),
                        _getCategoryColor(index),
                        category['product_count'] ?? 0,
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }

  Widget _buildCategoryCard(String title, IconData icon, Color color, int productCount) {
    return Card(
      elevation: 3,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: InkWell(
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => BuyerCategoryProductsScreen(category: title),
            ),
          );
        },
        borderRadius: BorderRadius.circular(12),
        child: Container(
          padding: EdgeInsets.all(16),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(12),
            color: Colors.white,
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                padding: EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(icon, size: 32, color: color),
              ),
              SizedBox(height: 12),
              Text(
                title,
                style: TextStyle(
                  color: Colors.black87,
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                ),
                textAlign: TextAlign.center,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              SizedBox(height: 4),
              Text(
                '$productCount items',
                style: TextStyle(
                  color: Colors.grey[600],
                  fontSize: 12,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  IconData _getCategoryIcon(String? category) {
    switch (category?.toLowerCase()) {
      case 'mobile phone':
      case 'mobile phones':
        return Icons.smartphone;
      case 'laptop':
      case 'laptops':
        return Icons.laptop;
      case 'desktop':
      case 'desktops':
        return Icons.desktop_windows;
      case 'audio equipment':
      case 'audio':
        return Icons.headphones;
      case 'video equipment':
      case 'video':
        return Icons.videocam;
      case 'smart home devices':
      case 'smart home':
        return Icons.home_outlined;
      case 'photography':
      case 'camera':
        return Icons.camera_alt;
      case 'wearable tech':
      case 'wearables':
        return Icons.watch;
      case 'digital accessories':
      case 'accessories':
        return Icons.cable;
      case 'gaming':
      case 'games':
        return Icons.sports_esports;
      case 'tablets':
      case 'tablet':
        return Icons.tablet;
      case 'monitors':
      case 'monitor':
        return Icons.monitor;
      case 'keyboards':
      case 'keyboard':
        return Icons.keyboard;
      case 'mouse':
      case 'mice':
        return Icons.mouse;
      case 'speakers':
      case 'speaker':
        return Icons.speaker;
      case 'storage':
      case 'hard drives':
        return Icons.storage;
      case 'networking':
      case 'wifi':
        return Icons.wifi;
      case 'printers':
      case 'printer':
        return Icons.print;
      case 'tv':
      case 'television':
        return Icons.tv;
      case 'others':
      case 'miscellaneous':
        return Icons.more_horiz;
      default:
        return Icons.category;
    }
  }

  Color _getCategoryColor(int index) {
    final colors = [
      Colors.blue,
      Colors.pink,
      Colors.green,
      Colors.orange,
      Colors.purple,
      Colors.red,
      Colors.teal,
      Colors.indigo,
      Colors.brown,
      Colors.cyan,
      Colors.amber,
      Colors.deepOrange,
    ];
    return colors[index % colors.length];
  }
} 