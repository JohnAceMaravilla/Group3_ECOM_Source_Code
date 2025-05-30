# IMPORTS
from flask import Blueprint, render_template, flash, session, redirect, url_for

seller_messages_bp = Blueprint('seller_messages', __name__)

@seller_messages_bp.route('/seller/messages')
def messages():
    
    if 'seller' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Seller':
        flash("Unauthorized access. Sellers only.", "danger")
        return redirect(url_for('login.login'))
    
    return render_template('seller_messages.html')