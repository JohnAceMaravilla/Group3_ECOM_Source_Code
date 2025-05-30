# IMPORTS
from flask import Blueprint, render_template, flash, session, redirect, url_for

admin_reports_bp = Blueprint('admin_reports', __name__)

@admin_reports_bp.route('/admin/reports')
def reports():
    
    if 'admin' not in session or session.get('status') != 'Approved' or session.get('user_role') != 'Admin':
        flash("Unauthorized access. Admins only.", "danger")
        return redirect(url_for('login.login'))
    
    return render_template('admin_reports.html')