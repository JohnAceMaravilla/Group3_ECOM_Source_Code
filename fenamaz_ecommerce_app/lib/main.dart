import 'package:flutter/material.dart';
import 'package:fenamaz_ecommerce_app/screens/login_screen.dart';
import 'package:fenamaz_ecommerce_app/screens/buyer_homepage.dart';
import 'package:fenamaz_ecommerce_app/screens/courier_dashboard.dart';
import 'package:fenamaz_ecommerce_app/services/user_session.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Fenamaz Ecommerce',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      home: SplashScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class SplashScreen extends StatefulWidget {
  @override
  _SplashScreenState createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _checkAuthStatus();
  }

  Future<void> _checkAuthStatus() async {
    // Small delay for splash effect
    await Future.delayed(Duration(milliseconds: 1000));
    
    bool isLoggedIn = await UserSession.isLoggedIn();
    
    if (isLoggedIn) {
      final userData = await UserSession.getUserData();
      
      if (userData != null) {
        String userRole = userData['user_type'] ?? '';
        String userStatus = userData['profile']['status'] ?? '';
        
        if (userStatus == 'Approved') {
          if (userRole == 'Buyer') {
            Navigator.pushReplacement(
              context,
              MaterialPageRoute(builder: (context) => BuyerHomepage()),
            );
          } else if (userRole == 'Courier') {
            Navigator.pushReplacement(
              context,
              MaterialPageRoute(builder: (context) => CourierDashboard()),
            );
          } else {
            // Handle other roles or redirect to login
            Navigator.pushReplacement(
              context,
              MaterialPageRoute(builder: (context) => LoginScreen()),
            );
          }
        } else {
          // User account not approved, redirect to login
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(builder: (context) => LoginScreen()),
          );
        }
      } else {
        // No user data, redirect to login
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (context) => LoginScreen()),
        );
      }
    } else {
      // User not logged in, redirect to login
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (context) => LoginScreen()),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Color(0xFF2196F3),
              Color(0xFF1976D2),
            ],
          ),
        ),
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // App Logo
              Container(
                width: 120,
                height: 120,
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black26,
                      blurRadius: 10,
                      offset: Offset(0, 5),
                    ),
                  ],
                ),
                child: Icon(
                  Icons.shopping_bag,
                  size: 60,
                  color: Color(0xFF2196F3),
                ),
              ),
              SizedBox(height: 30),
              // App Name
              Text(
                'Fenamaz',
                style: TextStyle(
                  fontSize: 32,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                  letterSpacing: 2,
                ),
              ),
              Text(
                'Ecommerce',
                style: TextStyle(
                  fontSize: 18,
                  color: Colors.white70,
                  letterSpacing: 1,
                ),
              ),
              SizedBox(height: 50),
              // Loading indicator
              CircularProgressIndicator(
                valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
