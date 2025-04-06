from flask import flash, jsonify, redirect, request, url_for
from flask_login import current_user, login_required
from disaster_app.db_manager import UserManager, CampManager, get_user_activity, log_recent_activity
from disaster_app.models import User, Warehouse, Camp, UserActivity, Donation
from . import admin_bp
from disaster_app.extensions import db

################## User Management APIs ##################

@admin_bp.route('/get_all_users')
@login_required
def get_all_users():
    """
    List all users.
    """
    try:
        users = User.query.all()
        return jsonify([{
            'uid': user.uid,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'location': user.location,
            'mobile': user.mobile,
            'managed_warehouse': {
                'wid': user.managed_warehouse.wid,
                'name': user.managed_warehouse.name
            } if hasattr(user, 'managed_warehouse') and user.managed_warehouse else None
        } for user in users]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route('/get_user/<int:user_id>')
@login_required
def get_user(user_id):
    """
    List all users.
    """
    try:
        users = UserManager.get_user(user_id)
        return jsonify(users), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route('/get_user_activity/<int:uid>')
@login_required
def user_activity(uid):
    data = get_user_activity(uid)
    
    return jsonify(data)

@admin_bp.route("/add_user", methods=["POST"])
@login_required
def add_user():
    try:
        data = request.json
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        location = data.get("location")
        mobile = data.get("mobile")
        role = data.get("role")
        associated_camp_id = data.get("associated_camp_id")
        warehouse_id = data.get("warehouse_id")

        if not all([username, email, password, role]):  
            return jsonify({"error": "Username, email, password, and role are required"}), 400
        
        # Create the user
        response, status_code = UserManager.create_user(username, email, password, location, mobile, role, associated_camp_id)

        if status_code == 201 and role == "warehouse_manager" and warehouse_id:
            # Assign warehouse to the manager
            warehouse = Warehouse.query.get(warehouse_id)
            if warehouse:
                warehouse.manager_id = response['user']['uid']
                db.session.commit()
                log_recent_activity(user_id=current_user.uid, action=f"Assigned warehouse {warehouse.name} to manager {username}")

        return jsonify(response), status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
@admin_bp.route('/update_user/<int:uid>', methods=['PUT'])
@login_required
def update_user(uid):
    """
    Edit user details.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Prevent admin from editing their own role
        if uid == current_user.uid and 'role' in data:
            return jsonify({'error': 'Cannot change your own role'}), 400

        # Update user
        response, status_code = UserManager.update_user(uid, data)
        return jsonify(response), status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route('/delete_user/<int:uid>', methods=['DELETE'])
@login_required
def delete_user(uid):
    """
    Delete a user.
    """
    try:
        # Prevent admin from deleting themselves
        if uid == current_user.uid:
            return jsonify({'error': 'Cannot delete your own account'}), 400

        # Delete user
        response, status_code = UserManager.delete_user(uid)
        return jsonify(response), status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

################## Camp Management APIs ##################

@admin_bp.route('/get_all_camps')
@login_required
def get_all_camps():
    """
    List all camps.
    """
    try:
        camps = Camp.query.all()
        return jsonify([{
            'cid': camp.cid,
            'name': camp.name,
            'location': camp.location,
            'capacity': camp.capacity,
            'current_occupancy': camp.current_occupancy,
            'status': camp.status,
            'camp_head': {
                'uid': camp.camp_head.uid,
                'username': camp.camp_head.username
            } if camp.camp_head else None
        } for camp in camps]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route('/get_camp/<int:camp_id>')
@login_required
def get_camp(camp_id):
    """
    Get a specific camp.
    """
    try:
        camp = Camp.query.get(camp_id)
        if not camp:
            return jsonify({"error": "Camp not found"}), 404

        return jsonify({
            'cid': camp.cid,
            'name': camp.name,
            'location': camp.location,
            'capacity': camp.capacity,
            'current_occupancy': camp.current_occupancy,
            'status': camp.status,
            'camp_head': {
                'uid': camp.camp_head.uid,
                'username': camp.camp_head.username
            } if camp.camp_head else None
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/add_camp", methods=["POST"])
@login_required
def add_camp():
    """
    Add a new camp.
    """
    try:
        data = request.json
        name = data.get("name")
        location = data.get("location")
        capacity = data.get("capacity")
        camp_head_id = data.get("camp_head_id")

        if not all([name, location, capacity]):
            return jsonify({"error": "Name, location, and capacity are required"}), 400

        # Create the camp
        response, status_code = CampManager.create_camp(name, location, capacity, camp_head_id)
        return jsonify(response), status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/update_camp/<int:camp_id>", methods=["PUT"])
@login_required
def update_camp(camp_id):
    """
    Update a camp.
    """
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Update camp
        response, status_code = CampManager.update_camp(camp_id, data)
        return jsonify(response), status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route('/delete_camp/<int:camp_id>', methods=['DELETE'])
@login_required
def delete_camp(camp_id):
    """
    Delete a camp.
    """
    try:
        # Delete camp
        response, status_code = CampManager.delete_camp(camp_id)
        return jsonify(response), status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

################## Warehouse Management APIs ##################

@admin_bp.route('/get_all_warehouses')
@login_required
def get_all_warehouses():
    """
    List all warehouses.
    """
    try:
        warehouses = Warehouse.query.all()
        return jsonify([{
            'wid': warehouse.wid,
            'name': warehouse.name,
            'location': warehouse.location,
            'capacity': warehouse.capacity,
            'current_stock': warehouse.current_stock,
            'status': warehouse.status,
            'manager': {
                'uid': warehouse.manager.uid,
                'username': warehouse.manager.username
            } if warehouse.manager else None
        } for warehouse in warehouses]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route('/create_warehouse', methods=['POST'])
@login_required
def create_warehouse():
    """
    Create a new warehouse.
    """
    try:
        data = request.json
        name = data.get("name")
        location = data.get("location")
        capacity = data.get("capacity")
        manager_id = data.get("manager_id")

        if not all([name, location, capacity]):
            return jsonify({"error": "Name, location, and capacity are required"}), 400

        # Create the warehouse
        warehouse = Warehouse(
            name=name,
            location=location,
            capacity=capacity,
            manager_id=manager_id
        )

        db.session.add(warehouse)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Warehouse created successfully',
            'warehouse': {
                'wid': warehouse.wid,
                'name': warehouse.name,
                'location': warehouse.location,
                'capacity': warehouse.capacity,
                'manager_id': warehouse.manager_id
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@admin_bp.route('/update_warehouse/<int:warehouse_id>', methods=['PUT'])
@login_required
def update_warehouse(warehouse_id):
    """
    Update a warehouse.
    """
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        warehouse = Warehouse.query.get(warehouse_id)
        if not warehouse:
            return jsonify({"error": "Warehouse not found"}), 404

        # Update warehouse
        for key, value in data.items():
            if hasattr(warehouse, key):
                setattr(warehouse, key, value)

        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Warehouse updated successfully',
            'warehouse': {
                'wid': warehouse.wid,
                'name': warehouse.name,
                'location': warehouse.location,
                'capacity': warehouse.capacity,
                'manager_id': warehouse.manager_id
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@admin_bp.route('/delete_warehouse/<int:warehouse_id>', methods=['DELETE'])
@login_required
def delete_warehouse(warehouse_id):
    """
    Delete a warehouse.
    """
    try:
        warehouse = Warehouse.query.get(warehouse_id)
        if not warehouse:
            return jsonify({"error": "Warehouse not found"}), 404

        db.session.delete(warehouse)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Warehouse deleted successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@admin_bp.route('/assign_warehouse_manager', methods=['POST'])
@login_required
def assign_warehouse_manager():
    """
    Assign a manager to a warehouse.
    """
    try:
        data = request.json
        warehouse_id = data.get("warehouse_id")
        manager_id = data.get("manager_id")

        if not all([warehouse_id, manager_id]):
            return jsonify({"error": "Warehouse ID and manager ID are required"}), 400

        warehouse = Warehouse.query.get(warehouse_id)
        if not warehouse:
            return jsonify({"error": "Warehouse not found"}), 404

        manager = User.query.get(manager_id)
        if not manager:
            return jsonify({"error": "Manager not found"}), 404

        if manager.role != "warehouse_manager":
            return jsonify({"error": "User is not a warehouse manager"}), 400

        warehouse.manager_id = manager_id
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Warehouse manager assigned successfully',
            'warehouse': {
                'wid': warehouse.wid,
                'name': warehouse.name,
                'manager_id': warehouse.manager_id
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@admin_bp.route('/get_warehouse_managers')
@login_required
def get_warehouse_managers():
    """
    Get all warehouse managers.
    """
    try:
        managers = User.query.filter_by(role="warehouse_manager").all()
        return jsonify([{
            'uid': manager.uid,
            'username': manager.username,
            'email': manager.email,
            'location': manager.location,
            'mobile': manager.mobile
        } for manager in managers]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/get_camp_managers", methods=["GET"])
@login_required
def get_camp_managers():
    """
    Get all camp managers.
    """
    try:
        managers = User.query.filter_by(role="camp_manager").all()
        return jsonify([{
            'uid': manager.uid,
            'username': manager.username,
            'email': manager.email,
            'location': manager.location,
            'mobile': manager.mobile
        } for manager in managers]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route('/get_recent_activities')
@login_required
def get_recent_activities():
    """
    Get recent activities.
    """
    try:
        activities = UserActivity.query.order_by(UserActivity.timestamp.desc()).limit(50).all()
        return jsonify([{
            'id': activity.id,
            'user_id': activity.user_id,
            'action': activity.action,
            'timestamp': activity.timestamp.isoformat()
        } for activity in activities]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500