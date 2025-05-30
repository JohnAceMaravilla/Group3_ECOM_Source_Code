# IMPORTS
from flask import Blueprint, render_template, flash, session, redirect, url_for

courier_application_bp = Blueprint('courier_application', __name__)

@courier_application_bp.route('/courier/delivery_application')
def application():
    
    if 'courier' not in session:
        flash("You must log in first.", "danger")
        return redirect(url_for('login.login'))
    
    return render_template('courier_application.html')