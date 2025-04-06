from flask import Blueprint, render_template, redirect, session, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required
from disaster_app.extensions import db, bcrypt
from disaster_app.models import User
from . import auth_bp
from werkzeug.security import generate_password_hash

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        #  user login
        if user and user.check_password(password) and user.role == 'user':
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('user.index'))
        
        #  admin login
        elif user and user.check_password(password) and user.role == 'admin':
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('admin.index'))
        
        # camp head login
        elif user and user.check_password(password) and user.role == 'local_auth':
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('local_auth.index'))
        
        # local auth login
        elif user and user.check_password(password) and user.role == 'camp_manager':
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('camp_manager.index'))
        
        # warehouse manager login
        elif user and user.check_password(password) and user.role == 'warehouse_manager':
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('warehouse_manager.index'))
        
        else:
            flash('Invalid email or password', 'danger')
            return redirect(url_for('auth.login'))
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email    = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        mobile   = request.form.get('mobile')
        
        # Log the mobile number for debugging
        print(f"Mobile number received: {mobile}")

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered.', 'danger')
            return redirect(url_for('auth.login'))
            
        # Check if username already exists
        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            flash('Username already taken. Please choose a different username.', 'danger')
            return redirect(url_for('auth.login'))

        # Validate email format
        if not email or '@' not in email:
            flash('Please enter a valid email address.', 'danger')
            return redirect(url_for('auth.login'))
            
        # Validate password
        if not password or len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return redirect(url_for('auth.login'))
            
        # Validate username
        if not username or len(username) < 3:
            flash('Username must be at least 3 characters long.', 'danger')
            return redirect(url_for('auth.login'))

        # Create new user
        user = User(username=username, email=email, role='user', mobile=mobile)
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            # Log the stored mobile number for debugging
            print(f"Mobile number stored: {user.mobile}")
            login_user(user)
            flash('Registration successful!', 'success')
            return redirect(url_for('user.index'))
        except Exception as e:
            db.session.rollback()
            print(f"Registration error: {str(e)}")
            flash('An error occurred during registration. Please try again.', 'danger')
            return redirect(url_for('auth.login'))
    return redirect(url_for('auth.login'))


@auth_bp.route('/admin_register', methods=['GET', 'POST'])
def adminregister():
    if request.method == 'POST':
        email    = request.values.get('email')
        username = request.values.get('username','admin')
        password = request.values.get('password')

        user = User(username=username, email=email, role='admin')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Account created! You can now log in.', 'success')
        return redirect(url_for('admin.index'))
    return redirect(url_for('auth.login'))


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/check_email', methods=['POST'])
def check_email():
    """
    Check if an email already exists in the database.
    """
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    # Check if email already exists
    existing_user = User.query.filter_by(email=email).first()
    
    return jsonify({'exists': existing_user is not None}), 200

@auth_bp.route('/check_username', methods=['POST'])
def check_username():
    """
    Check if a username already exists in the database.
    """
    data = request.get_json()
    username = data.get('username')
    
    if not username:
        return jsonify({'error': 'Username is required'}), 400
    
    # Check if username already exists
    existing_user = User.query.filter_by(username=username).first()
    
    return jsonify({'exists': existing_user is not None}), 200
