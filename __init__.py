from flask import Flask, session, redirect, url_for, flash
import base64
from datetime import datetime, timedelta

# LOGIN
from blueprints.login import login_bp

# REGISTRATION
from blueprints.buyer_registration import buyer_registration_bp
from blueprints.seller_registration import seller_registration_bp
from blueprints.courier_registration import courier_registration_bp
from blueprints.get_user_info import get_user_info_bp

# MOBILE API
from blueprints.mobile_api import mobile_api_bp
from blueprints.buyer_api import buyer_api_bp
from blueprints.buyer_product_api import buyer_product_api_bp
from blueprints.buyer_likes_api import buyer_likes_api_bp
from blueprints.buyer_cart_api import buyer_cart_api_bp
from blueprints.buyer_orders_api import buyer_orders_api_bp
from blueprints.buyer_notifications_api import buyer_notifications_api_bp
from blueprints.buyer_search_api import buyer_search_api_bp

# BUYER 
from blueprints.buyer_homepage import buyer_homepage_bp
from blueprints.buyer_categories import buyer_categories_bp
from blueprints.buyer_search import buyer_search_bp
from blueprints.buyer_product import buyer_product_bp
from blueprints.buyer_like import buyer_like_bp
from blueprints.buyer_cart import buyer_cart_bp
from blueprints.buyer_orders import buyer_orders_bp
from blueprints.buyer_notifications import buyer_notifications_bp
from blueprints.buyer_settings import buyer_settings_bp


# SELLER
from blueprints.seller_dashboard import seller_dashboard_bp
from blueprints.seller_shop_profile import seller_shop_profile_bp
from blueprints.seller_inventory import seller_inventory_bp
from blueprints.seller_vouchers import seller_vouchers_bp
from blueprints.seller_orders import seller_orders_bp
from blueprints.seller_finance import seller_finance_bp
from blueprints.seller_messages import seller_messages_bp
from blueprints.seller_notifications import seller_notifications_bp
from blueprints.seller_settings import seller_settings_bp

from blueprints.seller_inventory import check_and_notify_stock
from blueprints.seller_vouchers import check_and_notify_voucher


# COURIER 
from blueprints.courier_dashboard import courier_dashboard_bp
from blueprints.courier_delivery import courier_delivery_bp
from blueprints.courier_application import courier_application_bp
from blueprints.courier_messages import courier_messages_bp
from blueprints.courier_notifications import courier_notifications_bp
from blueprints.courier_settings import courier_settings_bp
from blueprints.courier_finance import courier_finance_bp

# ADMIN
from blueprints.admin_dashboard import admin_dashboard_bp
from blueprints.admin_user_mgmt import admin_user_mgmt_bp
from blueprints.admin_order_records import admin_order_records_bp
from blueprints.admin_commision import admin_commision_bp
from blueprints.admin_reports import admin_reports_bp
from blueprints.admin_messages import admin_messages_bp
from blueprints.admin_notifications import admin_notifications_bp
from blueprints.admin_settings import admin_settings_bp



# CREATE APP
def create_app():
    app = Flask(__name__, static_folder='static')
    app.secret_key = 'fenamazecommerce2024'
    
    # SESSION EXPIRATION - Updated for mobile compatibility
    app.config['SESSION_COOKIE_HTTPONLY'] = False  # Allow mobile apps to access cookies
    app.config['SESSION_COOKIE_SECURE'] = False    # Allow HTTP for development/mobile
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)  # Extended for mobile
    app.config['SESSION_COOKIE_SAMESITE'] = None   # More permissive for mobile apps
    
    @app.before_request
    def enforce_session_timeout():
        # Skip session timeout for mobile API endpoints
        from flask import request
        if request.path.startswith('/api/mobile'):
            return None
            
        if 'login_time' in session:
            try:
                login_time = datetime.strptime(session['login_time'], "%Y-%m-%d %H:%M:%S")
                if datetime.now() - login_time > timedelta(days=1):
                    session.clear()
                    flash("Session expired. Please log in again.", "warning")
                    return redirect(url_for('login.login'))
            except Exception as e:
                print(f"[Session Timeout Error] {e}")
                session.clear()
                return redirect(url_for('login.login'))
    
    # AUTOMATIC STOCK ALERT NOTIFICATION
    @app.before_request
    def check_stock_notifications():
        if session.get('seller'):  
            check_and_notify_stock()
            check_and_notify_voucher()
    
    # HANDLES IMAGES
    @app.template_filter('b64encode')
    def b64encode_filter(data):
        """Encodes binary data to base64 for use in Jinja templates."""
        if data:
            return base64.b64encode(data).decode('utf-8')
        return ''   
    
    app.jinja_env.filters['b64encode'] = b64encode_filter
    
    
    # AUTH
    app.register_blueprint(login_bp)
    app.register_blueprint(buyer_registration_bp)
    app.register_blueprint(seller_registration_bp)
    app.register_blueprint(courier_registration_bp)
    app.register_blueprint(get_user_info_bp)

    # MOBILE API
    app.register_blueprint(mobile_api_bp)
    app.register_blueprint(buyer_api_bp)
    app.register_blueprint(buyer_product_api_bp)
    app.register_blueprint(buyer_likes_api_bp)
    app.register_blueprint(buyer_cart_api_bp)
    app.register_blueprint(buyer_orders_api_bp)
    app.register_blueprint(buyer_notifications_api_bp)
    app.register_blueprint(buyer_search_api_bp)

    # BUYER 
    app.register_blueprint(buyer_homepage_bp)
    app.register_blueprint(buyer_categories_bp)
    app.register_blueprint(buyer_search_bp)
    app.register_blueprint(buyer_product_bp)
    app.register_blueprint(buyer_like_bp)
    app.register_blueprint(buyer_cart_bp)
    app.register_blueprint(buyer_orders_bp)
    app.register_blueprint(buyer_notifications_bp)
    app.register_blueprint(buyer_settings_bp)

    # SELLER 
    app.register_blueprint(seller_dashboard_bp)
    app.register_blueprint(seller_shop_profile_bp)
    app.register_blueprint(seller_inventory_bp)
    app.register_blueprint(seller_vouchers_bp)
    app.register_blueprint(seller_orders_bp)
    app.register_blueprint(seller_finance_bp)
    app.register_blueprint(seller_messages_bp)
    app.register_blueprint(seller_notifications_bp)
    app.register_blueprint(seller_settings_bp)
    
    # COURIER  
    app.register_blueprint(courier_dashboard_bp)
    app.register_blueprint(courier_delivery_bp)
    app.register_blueprint(courier_application_bp)
    app.register_blueprint(courier_messages_bp)
    app.register_blueprint(courier_notifications_bp)
    app.register_blueprint(courier_settings_bp)
    app.register_blueprint(courier_finance_bp)

    # ADMIN 
    app.register_blueprint(admin_dashboard_bp)
    app.register_blueprint(admin_user_mgmt_bp)
    app.register_blueprint(admin_order_records_bp)
    app.register_blueprint(admin_commision_bp)
    app.register_blueprint(admin_reports_bp)
    app.register_blueprint(admin_messages_bp)
    app.register_blueprint(admin_notifications_bp)
    app.register_blueprint(admin_settings_bp)
    
    return app