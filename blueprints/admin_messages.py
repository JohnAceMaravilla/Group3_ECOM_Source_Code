# IMPORTS
from flask import Blueprint, render_template, flash, session, redirect, url_for

admin_messages_bp = Blueprint('admin_messages', __name__)

@admin_messages_bp.route('/admin/messages')
def messages():
    
    if 'admin' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Admin':
        flash("Unauthorized access. Admins only.", "danger")
        return redirect(url_for('login.login'))
    
    return render_template('admin_messages.html')