from flask import Blueprint, jsonify, request, current_app
from disaster_app.models import db, Volunteer
from datetime import datetime

volunteer_bp = Blueprint('volunteer', __name__)

@volunteer_bp.route('/apply', methods=['POST'])
def apply():
    try:
        data = request.get_json()
        current_app.logger.info(f'Received volunteer application data: {data}')
        
        # Validate required fields
        required_fields = ['name', 'email', 'mobile', 'location', 'role', 'role_id']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            error_msg = f'Missing required fields: {", ".join(missing_fields)}'
            current_app.logger.error(error_msg)
            return jsonify({
                'status': 'error',
                'message': error_msg
            }), 400
            
        # Create new volunteer application
        try:
            new_volunteer = Volunteer(
                name=data['name'],
                email=data['email'],
                mobile=data['mobile'],
                location=data['location'],
                role=data['role'],
                role_id=data['role_id']
            )
            
            # Add to database
            db.session.add(new_volunteer)
            db.session.commit()
            
            current_app.logger.info(f'Successfully created volunteer application for {data["name"]}')
            return jsonify({
                'status': 'success',
                'message': 'Volunteer application submitted successfully'
            }), 200
            
        except Exception as e:
            db.session.rollback()
            error_msg = f'Database error: {str(e)}'
            current_app.logger.error(error_msg)
            return jsonify({
                'status': 'error',
                'message': error_msg
            }), 400
            
    except Exception as e:
        error_msg = f'Error processing request: {str(e)}'
        current_app.logger.error(error_msg)
        return jsonify({
            'status': 'error',
            'message': error_msg
        }), 400 