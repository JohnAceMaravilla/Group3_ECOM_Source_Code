# IMPORTS
from flask import Blueprint, render_template, flash, session, redirect, url_for

courier_messages_bp = Blueprint('courier_messages', __name__)

@courier_messages_bp.route('/courier/messages')
def messages():
    
    if 'courier' not in session:
        flash("You must log in first.", "danger")
        return redirect(url_for('login.login'))
    
    return render_template('courier_messages.html')