import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../services/auth_service.dart';
import 'login_screen.dart';
import 'dart:io';
import 'package:image_picker/image_picker.dart';
import 'dart:convert';
import 'package:flutter/services.dart' show rootBundle;

class RegistrationScreen extends StatefulWidget {
  final String userType;
  
  const RegistrationScreen({super.key, required this.userType});

  @override
  State<RegistrationScreen> createState() => _RegistrationScreenState();
}

class _RegistrationScreenState extends State<RegistrationScreen> {
  final PageController _pageController = PageController();
  final _formKey = GlobalKey<FormState>();
  
  int _currentStep = 0;
  bool _isLoading = false;
  
  // Form controllers
  final _firstnameController = TextEditingController();
  final _lastnameController = TextEditingController();
  final _houseNoController = TextEditingController();
  final _streetController = TextEditingController();
  final _phoneController = TextEditingController();
  final _emailController = TextEditingController();
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  final _idNoController = TextEditingController();
  final _otpController = TextEditingController();
  
  String _selectedSex = '';
  DateTime? _selectedBirthdate;
  String _selectedIdType = '';
  File? _idPicture;
  bool _isPasswordVisible = false;
  bool _isConfirmPasswordVisible = false;
  String? _errorMessage;
  String? _otpSent;

  // Address selection variables for cascading dropdowns
  String? _selectedRegionCode;
  String? _selectedProvinceCode;
  String? _selectedCityCode;
  String? _selectedBarangayCode;
  
  // Address text values for API submission
  String _regionText = '';
  String _provinceText = '';
  String _cityText = '';
  String _barangayText = '';

  final List<String> _idTypes = [
    'Driver\'s License',
    'Passport',
    'SSS',
    'PhilHealth',
    'TIN ID',
    'Voter\'s ID',
    'UMID',
    'Postal ID',
    'Senior Citizen ID',
    'Police Clearance',
    'Birth Certificate',
    'Other'
  ];

  // Address data from JSON files
  List<Map<String, dynamic>> _regionsData = [];
  List<Map<String, dynamic>> _provincesData = [];
  List<Map<String, dynamic>> _citiesData = [];
  List<Map<String, dynamic>> _barangaysData = [];

  @override
  void initState() {
    super.initState();
    _loadRegions();
    
    // Auto-fill username from email
    _emailController.addListener(() {
      _usernameController.text = _emailController.text;
    });
    
    // Set default ID type for couriers
    if (widget.userType == 'courier') {
      _selectedIdType = 'Driver\'s License';
    }
  }

  @override
  void dispose() {
    _pageController.dispose();
    _firstnameController.dispose();
    _lastnameController.dispose();
    _houseNoController.dispose();
    _streetController.dispose();
    _phoneController.dispose();
    _emailController.dispose();
    _usernameController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    _idNoController.dispose();
    _otpController.dispose();
    super.dispose();
  }

  void _nextStep() {
    if (_currentStep < 5) { // 6 steps total (0-5)
      setState(() {
        _currentStep++;
      });
      _pageController.nextPage(
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeInOut,
      );
    }
  }

  void _previousStep() {
    if (_currentStep > 0) {
      setState(() {
        _currentStep--;
      });
      _pageController.previousPage(
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeInOut,
      );
    }
  }

  Future<void> _pickImage() async {
    final ImagePicker picker = ImagePicker();
    final XFile? image = await picker.pickImage(
      source: ImageSource.gallery,
      maxWidth: 1024,
      maxHeight: 1024,
      imageQuality: 85,
    );
    
    if (image != null) {
      setState(() {
        _idPicture = File(image.path);
      });
    }
  }

  Future<void> _sendOTP() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final userData = {
        'firstname': _firstnameController.text.trim(),
        'lastname': _lastnameController.text.trim(),
        'sex': _selectedSex,
        'birthdate': _selectedBirthdate?.toIso8601String().split('T')[0],
        'house_no': _houseNoController.text.trim(),
        'street': _streetController.text.trim(),
        'barangay': _barangayText,
        'city': _cityText,
        'province': _provinceText,
        'region': _regionText,
        'phone': _phoneController.text.trim(),
        'email': _emailController.text.trim(),
        'id_type': _selectedIdType,
        'id_no': _idNoController.text.trim(),
        'username': _usernameController.text.trim(),
        'password': _passwordController.text,
      };

      final response = await AuthService.sendRegistrationOTP(widget.userType, userData, _idPicture);

      if (response['status'] == 'success') {
        setState(() {
          _otpSent = response['otp'];
        });
        _nextStep(); // Move to OTP verification step
      } else {
        setState(() {
          _errorMessage = response['message'] ?? 'Failed to send OTP';
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Connection error. Please check your internet connection and try again.';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _verifyOTPAndRegister() async {
    if (_otpController.text.trim() != _otpSent) {
      setState(() {
        _errorMessage = 'Invalid OTP. Please try again.';
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final userData = {
        'firstname': _firstnameController.text.trim(),
        'lastname': _lastnameController.text.trim(),
        'sex': _selectedSex,
        'birthdate': _selectedBirthdate?.toIso8601String().split('T')[0],
        'house_no': _houseNoController.text.trim(),
        'street': _streetController.text.trim(),
        'barangay': _barangayText,
        'city': _cityText,
        'province': _provinceText,
        'region': _regionText,
        'phone': _phoneController.text.trim(),
        'email': _emailController.text.trim(),
        'id_type': _selectedIdType,
        'id_no': _idNoController.text.trim(),
        'username': _usernameController.text.trim(),
        'password': _passwordController.text,
        'otp': _otpController.text.trim(),
      };

      final response = await AuthService.register(widget.userType, userData, _idPicture);

      if (response['status'] == 'success') {
        _showSuccessDialog(response);
      } else {
        setState(() {
          _errorMessage = response['message'] ?? 'Registration failed';
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Connection error. Please check your internet connection and try again.';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  void _showSuccessDialog(Map<String, dynamic> response) {
    final requiresApproval = response['data']?['requires_approval'] ?? false;
    
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
        title: Column(
          children: [
            Icon(
              Icons.check_circle, 
              color: Colors.green, 
              size: 64
            ),
            SizedBox(height: 16),
            Text(
              'Registration Successful!',
              style: TextStyle(
                fontSize: 20, 
                fontWeight: FontWeight.bold,
                color: widget.userType == 'courier' ? Colors.orange : Colors.blue,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
        content: Text(
          requiresApproval
              ? 'Your ${widget.userType} account has been created and is pending admin approval. You will be notified once approved.'
              : 'Your ${widget.userType} account has been created successfully! You can now sign in.',
          textAlign: TextAlign.center,
          style: TextStyle(fontSize: 16),
        ),
        actions: [
          Container(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: () {
                Navigator.of(context).pop();
                Navigator.pushReplacement(
                  context,
                  MaterialPageRoute(
                    builder: (context) => LoginScreen(),
                  ),
                );
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: widget.userType == 'courier' ? Colors.orange : Colors.blue,
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                padding: EdgeInsets.symmetric(vertical: 12),
              ),
              child: Text(
                'Sign In Now',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final isCoruier = widget.userType == 'courier';
    final primaryColor = isCoruier ? Colors.orange : Colors.blue;
    
    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              primaryColor,
              primaryColor.withOpacity(0.8),
            ],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              // Header
              Padding(
                padding: const EdgeInsets.all(24.0),
                child: Column(
                  children: [
                    Row(
                      children: [
                        IconButton(
                          onPressed: _currentStep > 0 ? _previousStep : () => Navigator.pop(context),
                          icon: const Icon(Icons.arrow_back, color: Colors.white),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    Icon(
                      isCoruier ? Icons.delivery_dining_rounded : Icons.shopping_bag_rounded,
                      size: 60,
                      color: Colors.white,
                    ),
                    const SizedBox(height: 12),
                    Text(
                      '${widget.userType.toUpperCase()} REGISTRATION',
                      style: const TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 20),
                    
                    // Progress Indicator
                    Row(
                      children: List.generate(6, (index) {
                        return Expanded(
                          child: Container(
                            margin: EdgeInsets.only(right: index < 5 ? 8 : 0),
                            height: 4,
                            decoration: BoxDecoration(
                              color: index <= _currentStep ? Colors.white : Colors.white30,
                              borderRadius: BorderRadius.circular(2),
                            ),
                          ),
                        );
                      }),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Step ${_currentStep + 1} of 6',
                      style: const TextStyle(color: Colors.white70),
                    ),
                  ],
                ),
              ),
              
              // Form Content
              Expanded(
                child: Container(
                  decoration: const BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
                  ),
                  child: Form(
                    key: _formKey,
                    child: PageView(
                      controller: _pageController,
                      physics: const NeverScrollableScrollPhysics(),
                      children: [
                        _buildPersonalInfoStep(),
                        _buildAddressInfoStep(),
                        _buildContactInfoStep(),
                        _buildValidIdInfoStep(),
                        _buildLoginInfoStep(),
                        _buildOTPVerificationStep(),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildPersonalInfoStep() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Personal Information',
            style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 6),
          const Text(
            'Tell us about yourself',
            style: TextStyle(color: Colors.grey, fontSize: 14),
          ),
          const SizedBox(height: 24),
          
          // First Name
          TextFormField(
            controller: _firstnameController,
            textCapitalization: TextCapitalization.words,
            decoration: InputDecoration(
              labelText: 'First Name *',
              prefixIcon: const Icon(Icons.person),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
              filled: true,
              fillColor: Colors.grey[50],
              contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 12),
            ),
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'Please enter your first name';
              }
              if (!RegExp(r'^[A-Za-z\s]+$').hasMatch(value)) {
                return 'First name should only contain letters and spaces';
              }
              return null;
            },
          ),
          
          const SizedBox(height: 12),
          
          // Last Name
          TextFormField(
            controller: _lastnameController,
            textCapitalization: TextCapitalization.words,
            decoration: InputDecoration(
              labelText: 'Last Name *',
              prefixIcon: const Icon(Icons.person),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
              filled: true,
              fillColor: Colors.grey[50],
              contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 12),
            ),
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'Please enter your last name';
              }
              if (!RegExp(r'^[A-Za-z\s]+$').hasMatch(value)) {
                return 'Last name should only contain letters and spaces';
              }
              return null;
            },
          ),
          
          const SizedBox(height: 12),
          
          // Sex Selection
          DropdownButtonFormField<String>(
            value: _selectedSex.isEmpty ? null : _selectedSex,
            decoration: InputDecoration(
              labelText: 'Sex *',
              prefixIcon: const Icon(Icons.wc),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
              filled: true,
              fillColor: Colors.grey[50],
              contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 12),
            ),
            items: ['Male', 'Female'].map((String value) {
              return DropdownMenuItem<String>(
                value: value,
                child: Text(value),
              );
            }).toList(),
            onChanged: (String? value) {
              setState(() {
                _selectedSex = value ?? '';
              });
            },
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'Please select your sex';
              }
              return null;
            },
          ),
          
          const SizedBox(height: 12),
          
          // Birthdate
          InkWell(
            onTap: () async {
              final date = await showDatePicker(
                context: context,
                initialDate: DateTime.now().subtract(const Duration(days: 365 * 18)),
                firstDate: DateTime(1950),
                lastDate: DateTime.now().subtract(const Duration(days: 365 * 13)),
                helpText: 'Select your birthdate',
                cancelText: 'Cancel',
                confirmText: 'OK',
              );
              if (date != null) {
                final today = DateTime.now();
                final age = today.year - date.year;
                final hasHadBirthdayThisYear = today.month > date.month || 
                    (today.month == date.month && today.day >= date.day);
                final actualAge = hasHadBirthdayThisYear ? age : age - 1;
                
                if (actualAge < 18) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('You must be 18 years old or above to create an account'),
                      backgroundColor: Colors.red,
                    ),
                  );
                  return;
                }
                
                setState(() {
                  _selectedBirthdate = date;
                });
              }
            },
            child: Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                border: Border.all(color: _selectedBirthdate == null ? Colors.red : Colors.grey[400]!),
                borderRadius: BorderRadius.circular(12),
                color: Colors.grey[50],
              ),
              child: Row(
                children: [
                  const Icon(Icons.calendar_today, color: Colors.grey),
                  const SizedBox(width: 12),
                  Text(
                    _selectedBirthdate != null
                        ? '${_selectedBirthdate!.day}/${_selectedBirthdate!.month}/${_selectedBirthdate!.year}'
                        : 'Select Birthdate *',
                    style: TextStyle(
                      fontSize: 16,
                      color: _selectedBirthdate != null ? Colors.black : Colors.grey[600],
                    ),
                  ),
                ],
              ),
            ),
          ),
          
          if (_selectedBirthdate == null) ...[
            const SizedBox(height: 6),
            Text(
              'Please select your birthdate',
              style: TextStyle(
                color: Colors.red[700],
                fontSize: 12,
              ),
            ),
          ],
          
          const SizedBox(height: 24),
          
          // Next Button
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: () {
                if (_firstnameController.text.trim().isEmpty ||
                    _lastnameController.text.trim().isEmpty ||
                    _selectedSex.isEmpty ||
                    _selectedBirthdate == null) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Please fill all required fields'),
                      backgroundColor: Colors.red,
                    ),
                  );
                  return;
                }

                if (!RegExp(r'^[A-Za-z\s]+$').hasMatch(_firstnameController.text.trim()) ||
                    !RegExp(r'^[A-Za-z\s]+$').hasMatch(_lastnameController.text.trim())) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Names should only contain letters and spaces'),
                      backgroundColor: Colors.red,
                    ),
                  );
                  return;
                }

                _nextStep();
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: widget.userType == 'courier' ? Colors.orange : Colors.blue,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
              child: const Text(
                'Next',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAddressInfoStep() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Address Information',
            style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 6),
          const Text(
            'Where do you live?',
            style: TextStyle(color: Colors.grey, fontSize: 14),
          ),
          const SizedBox(height: 24),
          
          // Region
          DropdownButtonFormField<String>(
            value: _selectedRegionCode,
            decoration: InputDecoration(
              labelText: 'Region *',
              prefixIcon: const Icon(Icons.location_on),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
              filled: true,
              fillColor: Colors.grey[50],
              contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 12),
            ),
            isExpanded: true,
            items: _regionsData.map((region) {
              return DropdownMenuItem<String>(
                value: region['region_code'],
                child: Text(
                  region['region_name'], 
                  style: TextStyle(fontSize: 12),
                  overflow: TextOverflow.ellipsis,
                ),
              );
            }).toList(),
            onChanged: (String? value) {
              if (value != null) {
                final selectedRegion = _regionsData.firstWhere(
                  (region) => region['region_code'] == value,
                );
                setState(() {
                  _selectedRegionCode = value;
                  _regionText = selectedRegion['region_name'];
                  _selectedProvinceCode = null;
                  _selectedCityCode = null;
                  _selectedBarangayCode = null;
                  _provinceText = '';
                  _cityText = '';
                  _barangayText = '';
                  _provincesData.clear();
                  _citiesData.clear();
                  _barangaysData.clear();
                });
                _loadProvinces(value);
              }
            },
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'Please select your region';
              }
              return null;
            },
          ),
          
          const SizedBox(height: 12),
          
          // Province
          DropdownButtonFormField<String>(
            value: _selectedProvinceCode,
            decoration: InputDecoration(
              labelText: 'Province *',
              prefixIcon: const Icon(Icons.location_city),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
              filled: true,
              fillColor: Colors.grey[50],
              contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 12),
            ),
            isExpanded: true,
            items: _provincesData.map((province) {
              return DropdownMenuItem<String>(
                value: province['province_code'],
                child: Text(
                  province['province_name'], 
                  overflow: TextOverflow.ellipsis
                ),
              );
            }).toList(),
            onChanged: _selectedRegionCode == null ? null : (String? value) {
              if (value != null) {
                final selectedProvince = _provincesData.firstWhere(
                  (province) => province['province_code'] == value,
                );
                setState(() {
                  _selectedProvinceCode = value;
                  _provinceText = selectedProvince['province_name'];
                  _selectedCityCode = null;
                  _selectedBarangayCode = null;
                  _cityText = '';
                  _barangayText = '';
                  _citiesData.clear();
                  _barangaysData.clear();
                });
                _loadCities(value);
              }
            },
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'Please select your province';
              }
              return null;
            },
          ),
          
          const SizedBox(height: 12),
          
          // City
          DropdownButtonFormField<String>(
            value: _selectedCityCode,
            decoration: InputDecoration(
              labelText: 'City / Municipality *',
              prefixIcon: const Icon(Icons.location_city),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
              filled: true,
              fillColor: Colors.grey[50],
              contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 12),
            ),
            isExpanded: true,
            items: _citiesData.map((city) {
              return DropdownMenuItem<String>(
                value: city['city_code'],
                child: Text(
                  city['city_name'], 
                  overflow: TextOverflow.ellipsis
                ),
              );
            }).toList(),
            onChanged: _selectedProvinceCode == null ? null : (String? value) {
              if (value != null) {
                final selectedCity = _citiesData.firstWhere(
                  (city) => city['city_code'] == value,
                );
                setState(() {
                  _selectedCityCode = value;
                  _cityText = selectedCity['city_name'];
                  _selectedBarangayCode = null;
                  _barangayText = '';
                  _barangaysData.clear();
                });
                _loadBarangays(value);
              }
            },
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'Please select your city/municipality';
              }
              return null;
            },
          ),
          
          const SizedBox(height: 12),
          
          // Barangay
          DropdownButtonFormField<String>(
            value: _selectedBarangayCode,
            decoration: InputDecoration(
              labelText: 'Barangay *',
              prefixIcon: const Icon(Icons.location_on),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
              filled: true,
              fillColor: Colors.grey[50],
              contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 12),
            ),
            isExpanded: true,
            items: _barangaysData.map((barangay) {
              return DropdownMenuItem<String>(
                value: barangay['brgy_code'],
                child: Text(
                  barangay['brgy_name'], 
                  overflow: TextOverflow.ellipsis
                ),
              );
            }).toList(),
            onChanged: _selectedCityCode == null ? null : (String? value) {
              if (value != null) {
                final selectedBarangay = _barangaysData.firstWhere(
                  (barangay) => barangay['brgy_code'] == value,
                );
                setState(() {
                  _selectedBarangayCode = value;
                  _barangayText = selectedBarangay['brgy_name'];
                });
              }
            },
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'Please select your barangay';
              }
              return null;
            },
          ),
          
          const SizedBox(height: 12),
          
          // Street
          TextFormField(
            controller: _streetController,
            textCapitalization: TextCapitalization.words,
            decoration: InputDecoration(
              labelText: 'Street (Optional)',
              prefixIcon: const Icon(Icons.location_on),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
              filled: true,
              fillColor: Colors.grey[50],
              contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 12),
            ),
          ),
          
          const SizedBox(height: 12),
          
          // House No
          TextFormField(
            controller: _houseNoController,
            textCapitalization: TextCapitalization.words,
            decoration: InputDecoration(
              labelText: 'House Number *',
              prefixIcon: const Icon(Icons.home),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
              filled: true,
              fillColor: Colors.grey[50],
              contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 12),
            ),
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'Please enter your house number';
              }
              return null;
            },
          ),
          
          const SizedBox(height: 24),
          
          // Next Button
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: () {
                if (_formKey.currentState!.validate()) {
                  _nextStep();
                }
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: widget.userType == 'courier' ? Colors.orange : Colors.blue,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
              child: const Text(
                'Next',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildContactInfoStep() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Contact Information',
            style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 6),
          const Text(
            'How can we reach you?',
            style: TextStyle(color: Colors.grey, fontSize: 14),
          ),
          const SizedBox(height: 24),
          
          // Phone Number
          TextFormField(
            controller: _phoneController,
            keyboardType: TextInputType.phone,
            inputFormatters: [
              FilteringTextInputFormatter.digitsOnly,
              LengthLimitingTextInputFormatter(11),
            ],
            decoration: InputDecoration(
              labelText: 'Phone Number *',
              prefixIcon: const Icon(Icons.phone),
              hintText: '09123456789',
              helperText: 'Format: 09XXXXXXXXX',
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
              filled: true,
              fillColor: Colors.grey[50],
              contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 12),
            ),
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'Please enter your phone number';
              }
              if (!RegExp(r'^09\d{9}$').hasMatch(value)) {
                return 'Invalid phone number format. Must be 09XXXXXXXXX';
              }
              return null;
            },
          ),
          
          const SizedBox(height: 12),
          
          // Email
          TextFormField(
            controller: _emailController,
            keyboardType: TextInputType.emailAddress,
            decoration: InputDecoration(
              labelText: 'Email Address *',
              prefixIcon: const Icon(Icons.email),
              hintText: 'example@email.com',
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
              filled: true,
              fillColor: Colors.grey[50],
              contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 12),
            ),
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'Please enter your email address';
              }
              if (!RegExp(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$').hasMatch(value)) {
                return 'Please enter a valid email address';
              }
              return null;
            },
          ),
          
          const SizedBox(height: 24),
          
          // Next Button
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: () {
                if (_formKey.currentState!.validate()) {
                  _nextStep();
                }
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: widget.userType == 'courier' ? Colors.orange : Colors.blue,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
              child: const Text(
                'Next',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildValidIdInfoStep() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Valid ID Information',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          const Text(
            'Upload your valid ID for verification',
            style: TextStyle(color: Colors.grey, fontSize: 16),
          ),
          const SizedBox(height: 32),
          
          // ID Type
          DropdownButtonFormField<String>(
            value: _selectedIdType.isEmpty ? null : _selectedIdType,
            decoration: InputDecoration(
              labelText: widget.userType == 'courier' 
                  ? 'Type of Valid ID (Driver\'s License Required)' 
                  : 'Type of Valid ID *',
              prefixIcon: const Icon(Icons.credit_card),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
              filled: true,
              fillColor: widget.userType == 'courier' ? Colors.grey[100] : Colors.grey[50],
            ),
            items: widget.userType == 'courier' 
                ? [DropdownMenuItem<String>(
                    value: 'Driver\'s License',
                    child: Text('Driver\'s License'),
                  )]
                : _idTypes.map((String value) {
                    return DropdownMenuItem<String>(
                      value: value,
                      child: Text(value),
                    );
                  }).toList(),
            onChanged: widget.userType == 'courier' 
                ? null  // Disable dropdown for couriers
                : (String? value) {
                    setState(() {
                      _selectedIdType = value ?? '';
                    });
                  },
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'Please select your ID type';
              }
              return null;
            },
          ),
          
          // Add helpful text for couriers
          if (widget.userType == 'courier') ...[
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.orange[50],
                border: Border.all(color: Colors.orange[200]!),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  Icon(Icons.info, color: Colors.orange[600], size: 20),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Driver\'s License is required for courier registration to verify your driving qualification.',
                      style: TextStyle(
                        color: Colors.orange[700],
                        fontSize: 13,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
          
          const SizedBox(height: 16),
          
          // ID Number
          TextFormField(
            controller: _idNoController,
            textCapitalization: TextCapitalization.characters,
            decoration: InputDecoration(
              labelText: widget.userType == 'courier' 
                  ? 'Driver\'s License Number *'
                  : 'Valid ID Number *',
              prefixIcon: const Icon(Icons.confirmation_number),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
              filled: true,
              fillColor: Colors.grey[50],
              contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 12),
            ),
            validator: (value) {
              if (value == null || value.isEmpty) {
                return widget.userType == 'courier' 
                    ? 'Please enter your driver\'s license number'
                    : 'Please enter your ID number';
              }
              return null;
            },
          ),
          
          const SizedBox(height: 16),
          
          // ID Picture Upload
          GestureDetector(
            onTap: _pickImage,
            child: Container(
              width: double.infinity,
              height: 200,
              decoration: BoxDecoration(
                border: Border.all(
                  color: _idPicture == null ? Colors.red : Colors.grey[400]!,
                  width: 2,
                  style: BorderStyle.solid,
                ),
                borderRadius: BorderRadius.circular(12),
                color: Colors.grey[50],
              ),
              child: _idPicture != null
                  ? Stack(
                      children: [
                        ClipRRect(
                          borderRadius: BorderRadius.circular(10),
                          child: Image.file(
                            _idPicture!,
                            width: double.infinity,
                            height: double.infinity,
                            fit: BoxFit.cover,
                          ),
                        ),
                        Positioned(
                          top: 8,
                          right: 8,
                          child: Container(
                            decoration: BoxDecoration(
                              color: Colors.black54,
                              borderRadius: BorderRadius.circular(20),
                            ),
                            child: IconButton(
                              icon: Icon(Icons.close, color: Colors.white),
                              onPressed: () {
                                setState(() {
                                  _idPicture = null;
                                });
                              },
                            ),
                          ),
                        ),
                      ],
                    )
                  : Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          Icons.upload_file,
                          size: 64,
                          color: Colors.grey[400],
                        ),
                        const SizedBox(height: 16),
                        Text(
                          widget.userType == 'courier'
                              ? 'Upload Driver\'s License Picture *'
                              : 'Upload Valid ID Picture *',
                          style: TextStyle(
                            fontSize: 16,
                            color: Colors.grey[600],
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Tap to select image',
                          style: TextStyle(
                            fontSize: 14,
                            color: Colors.grey[500],
                          ),
                        ),
                      ],
                    ),
            ),
          ),
          
          if (_idPicture == null) ...[
            const SizedBox(height: 8),
            Text(
              widget.userType == 'courier'
                  ? 'Please upload your driver\'s license picture'
                  : 'Please upload your valid ID picture',
              style: TextStyle(
                color: Colors.red[700],
                fontSize: 12,
              ),
            ),
          ],
          
          const SizedBox(height: 32),
          
          // Next Button
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: () {
                if (_selectedIdType.isEmpty || _idNoController.text.trim().isEmpty || _idPicture == null) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text(
                        widget.userType == 'courier'
                            ? 'Please fill all required fields and upload driver\'s license picture'
                            : 'Please fill all required fields and upload ID picture'
                      ),
                      backgroundColor: Colors.red,
                    ),
                  );
                  return;
                }
                _nextStep();
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: widget.userType == 'courier' ? Colors.orange : Colors.blue,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
              child: const Text(
                'Next',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLoginInfoStep() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Account Information',
            style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 6),
          const Text(
            'Create your login credentials',
            style: TextStyle(color: Colors.grey, fontSize: 14),
          ),
          const SizedBox(height: 24),
          
          // Username (Email)
          TextFormField(
            controller: _usernameController,
            keyboardType: TextInputType.emailAddress,
            enabled: false,
            decoration: InputDecoration(
              labelText: 'Username (Auto-filled from email)',
              prefixIcon: const Icon(Icons.account_circle),
              hintText: 'Will be filled automatically',
              helperText: 'Username is automatically set to your email address',
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
              filled: true,
              fillColor: Colors.grey[100],
              disabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide(color: Colors.grey[300]!),
              ),
              contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 12),
            ),
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'Email must be provided first';
              }
              if (!RegExp(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$').hasMatch(value)) {
                return 'Invalid email format';
              }
              return null;
            },
          ),
          
          const SizedBox(height: 12),
          
          // Password
          TextFormField(
            controller: _passwordController,
            obscureText: !_isPasswordVisible,
            decoration: InputDecoration(
              labelText: 'Password *',
              prefixIcon: const Icon(Icons.lock),
              suffixIcon: IconButton(
                icon: Icon(_isPasswordVisible ? Icons.visibility : Icons.visibility_off),
                onPressed: () {
                  setState(() {
                    _isPasswordVisible = !_isPasswordVisible;
                  });
                },
              ),
              helperText: 'At least 8 characters with uppercase, lowercase, number, and special character',
              helperMaxLines: 2,
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
              filled: true,
              fillColor: Colors.grey[50],
              contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 12),
            ),
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'Please enter a password';
              }
              if (value.length < 8) {
                return 'Password must be at least 8 characters long';
              }
              if (!RegExp(r'[A-Z]').hasMatch(value)) {
                return 'Password must contain at least one uppercase letter';
              }
              if (!RegExp(r'[a-z]').hasMatch(value)) {
                return 'Password must contain at least one lowercase letter';
              }
              if (!RegExp(r'\d').hasMatch(value)) {
                return 'Password must contain at least one number';
              }
              if (!RegExp(r'[!@#$%^&*(),.?":{}|<>]').hasMatch(value)) {
                return 'Password must contain at least one special character';
              }
              return null;
            },
          ),
          
          const SizedBox(height: 16),
          
          // Confirm Password
          TextFormField(
            controller: _confirmPasswordController,
            obscureText: !_isConfirmPasswordVisible,
            decoration: InputDecoration(
              labelText: 'Confirm Password *',
              prefixIcon: const Icon(Icons.lock),
              suffixIcon: IconButton(
                icon: Icon(_isConfirmPasswordVisible ? Icons.visibility : Icons.visibility_off),
                onPressed: () {
                  setState(() {
                    _isConfirmPasswordVisible = !_isConfirmPasswordVisible;
                  });
                },
              ),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
              filled: true,
              fillColor: Colors.grey[50],
            ),
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'Please confirm your password';
              }
              if (value != _passwordController.text) {
                return 'Passwords do not match';
              }
              return null;
            },
          ),
          
          if (_errorMessage != null) ...[
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.red[50],
                border: Border.all(color: Colors.red[200]!),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  Icon(Icons.error, color: Colors.red[600], size: 20),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      _errorMessage!,
                      style: TextStyle(color: Colors.red[600]),
                    ),
                  ),
                ],
              ),
            ),
          ],
          
          const SizedBox(height: 32),
          
          // Send OTP Button
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: _isLoading ? null : () {
                if (_formKey.currentState!.validate()) {
                  if (_passwordController.text != _confirmPasswordController.text) {
                    setState(() {
                      _errorMessage = 'Passwords do not match';
                    });
                    return;
                  }
                  _sendOTP();
                }
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: widget.userType == 'courier' ? Colors.orange : Colors.blue,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
              child: _isLoading
                  ? const CircularProgressIndicator(color: Colors.white)
                  : const Text(
                      'Send OTP',
                      style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                    ),
            ),
          ),
          
          const SizedBox(height: 16),
          
          // Already have account
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Text('Already have an account? '),
              TextButton(
                onPressed: () {
                  Navigator.pushReplacement(
                    context,
                    MaterialPageRoute(
                      builder: (context) => LoginScreen(),
                    ),
                  );
                },
                child: Text(
                  'Sign In',
                  style: TextStyle(
                    color: widget.userType == 'courier' ? Colors.orange : Colors.blue,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildOTPVerificationStep() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Email Verification',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          Text(
            'A One-Time-Password (OTP) has been sent to ${_emailController.text}. Please check your inbox or spam/junk folder.',
            style: const TextStyle(color: Colors.grey, fontSize: 16),
          ),
          const SizedBox(height: 32),
          
          // OTP Input
          TextFormField(
            controller: _otpController,
            keyboardType: TextInputType.number,
            inputFormatters: [
              FilteringTextInputFormatter.digitsOnly,
              LengthLimitingTextInputFormatter(6),
            ],
            decoration: InputDecoration(
              labelText: 'OTP Code *',
              prefixIcon: const Icon(Icons.verified),
              hintText: 'Enter 6-digit OTP',
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
              filled: true,
              fillColor: Colors.grey[50],
            ),
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'Please enter the OTP code';
              }
              if (value.length != 6) {
                return 'OTP must be 6 digits';
              }
              return null;
            },
          ),
          
          if (_errorMessage != null) ...[
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.red[50],
                border: Border.all(color: Colors.red[200]!),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  Icon(Icons.error, color: Colors.red[600], size: 20),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      _errorMessage!,
                      style: TextStyle(color: Colors.red[600]),
                    ),
                  ),
                ],
              ),
            ),
          ],
          
          const SizedBox(height: 32),
          
          // Verify Button
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: _isLoading ? null : _verifyOTPAndRegister,
              style: ElevatedButton.styleFrom(
                backgroundColor: widget.userType == 'courier' ? Colors.orange : Colors.blue,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
              child: _isLoading
                  ? const CircularProgressIndicator(color: Colors.white)
                  : const Text(
                      'Verify & Create Account',
                      style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                    ),
            ),
          ),
          
          const SizedBox(height: 16),
          
          // Resend OTP
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Text("Didn't receive OTP? "),
              TextButton(
                onPressed: () {
                  _sendOTP();
                },
                child: Text(
                  'Resend OTP',
                  style: TextStyle(
                    color: widget.userType == 'courier' ? Colors.orange : Colors.blue,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  // Load regions from JSON
  Future<void> _loadRegions() async {
    try {
      final String response = await rootBundle.loadString('assets/data/region.json');
      final List<dynamic> data = json.decode(response);
      setState(() {
        _regionsData = data.cast<Map<String, dynamic>>();
      });
    } catch (e) {
      print('Error loading regions: $e');
    }
  }

  // Load provinces based on selected region
  Future<void> _loadProvinces(String regionCode) async {
    try {
      final String response = await rootBundle.loadString('assets/data/province.json');
      final List<dynamic> data = json.decode(response);
      setState(() {
        _provincesData = data
            .cast<Map<String, dynamic>>()
            .where((province) => province['region_code'] == regionCode)
            .toList();
        _provincesData.sort((a, b) => a['province_name'].compareTo(b['province_name']));
        
        // Clear dependent dropdowns
        _selectedProvinceCode = null;
        _selectedCityCode = null;
        _selectedBarangayCode = null;
        _citiesData.clear();
        _barangaysData.clear();
      });
    } catch (e) {
      print('Error loading provinces: $e');
    }
  }

  // Load cities based on selected province
  Future<void> _loadCities(String provinceCode) async {
    try {
      final String response = await rootBundle.loadString('assets/data/city.json');
      final List<dynamic> data = json.decode(response);
      setState(() {
        _citiesData = data
            .cast<Map<String, dynamic>>()
            .where((city) => city['province_code'] == provinceCode)
            .toList();
        _citiesData.sort((a, b) => a['city_name'].compareTo(b['city_name']));
        
        // Clear dependent dropdowns
        _selectedCityCode = null;
        _selectedBarangayCode = null;
        _barangaysData.clear();
      });
    } catch (e) {
      print('Error loading cities: $e');
    }
  }

  // Load barangays based on selected city
  Future<void> _loadBarangays(String cityCode) async {
    try {
      final String response = await rootBundle.loadString('assets/data/barangay.json');
      final List<dynamic> data = json.decode(response);
      setState(() {
        _barangaysData = data
            .cast<Map<String, dynamic>>()
            .where((barangay) => barangay['city_code'] == cityCode)
            .toList();
        _barangaysData.sort((a, b) => a['brgy_name'].compareTo(b['brgy_name']));
        
        // Clear dependent dropdown
        _selectedBarangayCode = null;
      });
    } catch (e) {
      print('Error loading barangays: $e');
    }
  }
} 