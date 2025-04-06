from flask import render_template, jsonify, request
from flask_login import login_required
from disaster_app.models import Volunteer
from disaster_app.extensions import db
from . import admin_bp

@admin_bp.route('/volunteer')
@login_required
def volunteer():
    """
    Render the volunteer management page.
    """
    return render_template('admin/volunteer.html')

@admin_bp.route('/get_all_volunteers')
@login_required
def get_all_volunteers():
    """
    Get all volunteers.
    """
    try:
        volunteers = Volunteer.query.all()
        return jsonify([{
            'role_id': volunteer.role_id,
            'name': volunteer.name,
            'email': volunteer.email,
            'mobile': volunteer.mobile,
            'role': volunteer.role,
            'location': volunteer.location
        } for volunteer in volunteers]), 200
    except Exception as e:
        current_app.logger.error(f'Error getting volunteers: {str(e)}')
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/add_volunteer', methods=['POST'])
@login_required
def add_volunteer():
    """
    Add a new volunteer.
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ["name", "email", "mobile", "location", "role"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Create new volunteer
        new_volunteer = Volunteer(
            name=data["name"],
            email=data["email"],
            mobile=data["mobile"],
            location=data["location"],
            role=data["role"],
            status="pending"
        )
        
        db.session.add(new_volunteer)
        db.session.commit()
        
        return jsonify({
            "message": "Volunteer added successfully",
            "volunteer": {
                "id": new_volunteer.id,
                "name": new_volunteer.name,
                "email": new_volunteer.email,
                "mobile": new_volunteer.mobile,
                "role": new_volunteer.role,
                "location": new_volunteer.location,
                "status": new_volunteer.status
            }
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/update_volunteer/<int:volunteer_id>', methods=['PUT'])
@login_required
def update_volunteer(volunteer_id):
    """
    Update volunteer details.
    """
    try:
        volunteer = Volunteer.query.get_or_404(volunteer_id)
        data = request.get_json()
        
        if "name" in data:
            volunteer.name = data["name"]
        if "email" in data:
            volunteer.email = data["email"]
        if "mobile" in data:
            volunteer.mobile = data["mobile"]
        if "location" in data:
            volunteer.location = data["location"]
        if "role" in data:
            volunteer.role = data["role"]
        if "status" in data:
            volunteer.status = data["status"]
            
        db.session.commit()
        
        return jsonify({
            "message": "Volunteer updated successfully",
            "volunteer": {
                "id": volunteer.id,
                "name": volunteer.name,
                "email": volunteer.email,
                "mobile": volunteer.mobile,
                "role": volunteer.role,
                "location": volunteer.location,
                "status": volunteer.status
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/delete_volunteer/<int:volunteer_id>', methods=['DELETE'])
@login_required
def delete_volunteer(volunteer_id):
    """
    Delete a volunteer.
    """
    try:
        volunteer = Volunteer.query.get_or_404(volunteer_id)
        db.session.delete(volunteer)
        db.session.commit()
        
        return jsonify({
            "message": "Volunteer deleted successfully"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500 