from flask import render_template, request, jsonify, flash
from flask_login import login_required
from disaster_app.db_manager import get_table_count
from disaster_app.data import load_sensor_configs, save_sensor_configs, generate_sensor_data, save_sensor_data_to_json
from . import admin_bp
import json
import os
from disaster_app.models import User, Camp, Warehouse, Sensor, Request
from disaster_app.extensions import db

def get_table_count():
    """Get count of records from various tables"""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'static', 'data')
    try:
        with open(os.path.join(data_dir, 'sensor_data.json'), 'r') as f:
            sensor_data = json.load(f)
    except FileNotFoundError:
        sensor_data = []
    return {
        'users': User.query.count(),
        'camps': Camp.query.count(),
        'warehouses': Warehouse.query.count(),
        'sensors': len(sensor_data)
    }

@admin_bp.route('/')
@login_required
def index():
    counts = get_table_count()
    return render_template('admin/index.html', counts=counts)

@admin_bp.route('/user')
@login_required
def user():
    return render_template('admin/user.html')

@admin_bp.route('/camp')
@login_required
def camp():
    return render_template('admin/camp.html')

@admin_bp.route('/warehouse')
@login_required
def warehouse():
    return render_template('admin/warehouse.html')

@admin_bp.route('/sensor')
@login_required
def sensor():
    try:
        # Get sensors from database
        db_sensors = Sensor.query.all()
        
        # Get sensors from JSON file
        try:
            with open('disaster_app/static/data/sensor_data.json', 'r') as f:
                json_sensors = json.load(f)
                json_sensor_list = [{
                    'sid': sensor['id'],
                    'name': sensor['name'],
                    'latitude': sensor['latitude'],
                    'longitude': sensor['longitude'],
                    'soil_type': sensor['soil_type'],
                    'status': sensor.get('status', 'Active'),
                    'operational_status': sensor.get('operational_status', 'Active')
                } for sensor in json_sensors]
        except (FileNotFoundError, json.JSONDecodeError):
            json_sensor_list = []
        
        # Combine both lists, avoiding duplicates based on sensor ID
        all_sensors = []
        seen_ids = set()
        
        # Add database sensors first
        for sensor in db_sensors:
            seen_ids.add(sensor.sid)
            all_sensors.append(sensor)
        
        # Add JSON sensors that aren't in the database
        for sensor_data in json_sensor_list:
            if sensor_data['sid'] not in seen_ids:
                # Create a Sensor object from the JSON data
                json_sensor = Sensor(
                    sid=sensor_data['sid'],
                    name=sensor_data['name'],
                    latitude=sensor_data['latitude'],
                    longitude=sensor_data['longitude'],
                    soil_type=sensor_data['soil_type'],
                    status=sensor_data['status'],
                    operational_status=sensor_data['operational_status']
                )
                all_sensors.append(json_sensor)
        
        return render_template('admin/sensor.html', sensors=all_sensors)
    except Exception as e:
        flash(f"Error loading sensors: {str(e)}", "error")
        return render_template('admin/sensor.html', sensors=[])

@admin_bp.route('/add_sensor', methods=['POST'])
@login_required
def add_sensor():
    try:
        data = request.get_json()

        # Create new sensor in database
        new_sensor = Sensor(
            sid=data['id'],
            name=data['name'],
            latitude=data['latitude'],
            longitude=data['longitude'],
            soil_type=data['soil_type'],
            status=data.get('status', 'Active'),
            operational_status=data.get('operational_status', 'Active')
        )

        db.session.add(new_sensor)
        db.session.commit()

        # Save to JSON file
        try:
            with open('disaster_app/static/data/sensor_data.json', 'r') as f:
                sensors = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            sensors = []

        sensors.append({
            'id': data['id'],
            'name': data['name'],
            'latitude': data['latitude'],
            'longitude': data['longitude'],
            'soil_type': data['soil_type'],
            'status': data.get('status', 'Active'),
            'operational_status': data.get('operational_status', 'Active')
        })

        with open('disaster_app/static/data/sensor_data.json', 'w') as f:
            json.dump(sensors, f, indent=4)

        return jsonify({
            'status': 'success',
            'message': 'Sensor added successfully',
            'sensor': {
                'sid': new_sensor.sid,
                'name': new_sensor.name,
                'latitude': new_sensor.latitude,
                'longitude': new_sensor.longitude,
                'soil_type': new_sensor.soil_type,
                'status': new_sensor.status,
                'operational_status': new_sensor.operational_status
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@admin_bp.route('/delete_sensor/<int:sensor_id>', methods=['POST'])
@login_required
def delete_sensor(sensor_id):
    try:
        # Delete from database
        sensor = Sensor.query.get(sensor_id)
        if not sensor:
            return jsonify({
                'status': 'error',
                'message': 'Sensor not found'
            }), 404

        db.session.delete(sensor)
        db.session.commit()

        # Delete from JSON file
        try:
            with open('disaster_app/static/data/sensor_data.json', 'r') as f:
                sensors = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            sensors = []

        sensors = [s for s in sensors if s['id'] != sensor_id]

        with open('disaster_app/static/data/sensor_data.json', 'w') as f:
            json.dump(sensors, f, indent=4)

        return jsonify({
            'status': 'success',
            'message': 'Sensor deleted successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@admin_bp.route('/get_sensors')
@login_required
def get_sensors():
    try:
        # Get sensors from database
        db_sensors = Sensor.query.all()
        
        # Get sensors from JSON file
        try:
            with open('disaster_app/static/data/sensor_data.json', 'r') as f:
                json_sensors = json.load(f)
                json_sensor_list = [{
                    'sid': sensor['id'],
                    'name': sensor['name'],
                    'latitude': sensor['latitude'],
                    'longitude': sensor['longitude'],
                    'soil_type': sensor['soil_type'],
                    'status': sensor.get('status', 'Active'),
                    'operational_status': sensor.get('operational_status', 'Active')
                } for sensor in json_sensors]
        except (FileNotFoundError, json.JSONDecodeError):
            json_sensor_list = []
        
        # Combine both lists, avoiding duplicates based on sensor ID
        all_sensors = []
        seen_ids = set()
        
        # Add database sensors first
        for sensor in db_sensors:
            seen_ids.add(sensor.sid)
            all_sensors.append({
                'sid': sensor.sid,
                'name': sensor.name,
                'latitude': sensor.latitude,
                'longitude': sensor.longitude,
                'soil_type': sensor.soil_type,
                'status': sensor.status,
                'operational_status': sensor.operational_status
            })
        
        # Add JSON sensors that aren't in the database
        for sensor_data in json_sensor_list:
            if sensor_data['sid'] not in seen_ids:
                all_sensors.append(sensor_data)
        
        return jsonify(all_sensors), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@admin_bp.route('/get_sensor/<int:sensor_id>')
@login_required
def get_sensor(sensor_id):
    try:
        # Try to get sensor from database first
        sensor = Sensor.query.get(sensor_id)
        if sensor:
            return jsonify({
                'sid': sensor.sid,
                'name': sensor.name,
                'latitude': sensor.latitude,
                'longitude': sensor.longitude,
                'soil_type': sensor.soil_type,
                'status': sensor.status,
                'operational_status': sensor.operational_status
            }), 200

        # If not in database, try to get from JSON file
        try:
            with open('disaster_app/static/data/sensor_data.json', 'r') as f:
                sensors = json.load(f)
                for sensor_data in sensors:
                    if sensor_data['id'] == sensor_id:
                        return jsonify({
                            'sid': sensor_data['id'],
                            'name': sensor_data['name'],
                            'latitude': sensor_data['latitude'],
                            'longitude': sensor_data['longitude'],
                            'soil_type': sensor_data['soil_type'],
                            'status': sensor_data.get('status', 'Active'),
                            'operational_status': sensor_data.get('operational_status', 'Active')
                        }), 200
        except (FileNotFoundError, json.JSONDecodeError):
            pass

        return jsonify({
            'status': 'error',
            'message': 'Sensor not found'
        }), 404

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@admin_bp.route('/update_sensor/<int:sensor_id>', methods=['POST'])
@login_required
def update_sensor(sensor_id):
    try:
        data = request.get_json()

        # Try to update in database first
        sensor = Sensor.query.get(sensor_id)
        if sensor:
            for key, value in data.items():
                if hasattr(sensor, key):
                    setattr(sensor, key, value)
            db.session.commit()

            # Update in JSON file
            try:
                with open('disaster_app/static/data/sensor_data.json', 'r') as f:
                    sensors = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                sensors = []

            for i, sensor_data in enumerate(sensors):
                if sensor_data['id'] == sensor_id:
                    sensors[i].update({
                        'name': data.get('name', sensor_data['name']),
                        'latitude': data.get('latitude', sensor_data['latitude']),
                        'longitude': data.get('longitude', sensor_data['longitude']),
                        'soil_type': data.get('soil_type', sensor_data['soil_type']),
                        'status': data.get('status', sensor_data.get('status', 'Active')),
                        'operational_status': data.get('operational_status', sensor_data.get('operational_status', 'Active'))
                    })
                    break

            with open('disaster_app/static/data/sensor_data.json', 'w') as f:
                json.dump(sensors, f, indent=4)

            return jsonify({
                'status': 'success',
                'message': 'Sensor updated successfully',
                'sensor': {
                    'sid': sensor.sid,
                    'name': sensor.name,
                    'latitude': sensor.latitude,
                    'longitude': sensor.longitude,
                    'soil_type': sensor.soil_type,
                    'status': sensor.status,
                    'operational_status': sensor.operational_status
                }
            }), 200

        # If not in database, try to update in JSON file
        try:
            with open('disaster_app/static/data/sensor_data.json', 'r') as f:
                sensors = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return jsonify({
                'status': 'error',
                'message': 'Sensor not found'
            }), 404

        for i, sensor_data in enumerate(sensors):
            if sensor_data['id'] == sensor_id:
                sensors[i].update({
                    'name': data.get('name', sensor_data['name']),
                    'latitude': data.get('latitude', sensor_data['latitude']),
                    'longitude': data.get('longitude', sensor_data['longitude']),
                    'soil_type': data.get('soil_type', sensor_data['soil_type']),
                    'status': data.get('status', sensor_data.get('status', 'Active')),
                    'operational_status': data.get('operational_status', sensor_data.get('operational_status', 'Active'))
                })

                with open('disaster_app/static/data/sensor_data.json', 'w') as f:
                    json.dump(sensors, f, indent=4)

                return jsonify({
                    'status': 'success',
                    'message': 'Sensor updated successfully',
                    'sensor': sensors[i]
                }), 200

        return jsonify({
            'status': 'error',
            'message': 'Sensor not found'
        }), 404

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@admin_bp.route('/delete_json_sensor', methods=['POST'])
@login_required
def delete_json_sensor():
    try:
        data = request.get_json()
        sensor_id = data.get('id')

        if not sensor_id:
            return jsonify({
                'status': 'error',
                'message': 'Sensor ID is required'
            }), 400

        try:
            with open('disaster_app/static/data/sensor_data.json', 'r') as f:
                sensors = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return jsonify({
                'status': 'error',
                'message': 'No sensors found'
            }), 404

        sensors = [s for s in sensors if s['id'] != sensor_id]

        with open('disaster_app/static/data/sensor_data.json', 'w') as f:
            json.dump(sensors, f, indent=4)

        return jsonify({
            'status': 'success',
            'message': 'Sensor deleted successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@admin_bp.route('/warehouse_manager/get_warehouse_details')
@login_required
def get_warehouse_details():
    try:
        warehouse = Warehouse.query.filter_by(manager_id=current_user.uid).first()
        if not warehouse:
            return jsonify({
                'status': 'error',
                'message': 'No warehouse assigned'
            }), 404

        return jsonify({
            'status': 'success',
            'warehouse': {
                'wid': warehouse.wid,
                'name': warehouse.name,
                'location': warehouse.location,
                'capacity': warehouse.capacity,
                'current_stock': warehouse.current_stock,
                'status': warehouse.status
            }
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@admin_bp.route('/get_sensor_data')
@login_required
def get_sensor_data():
    try:
        # Get sensors from database
        db_sensors = Sensor.query.all()
        
        # Get sensors from JSON file
        try:
            with open('disaster_app/static/data/sensor_data.json', 'r') as f:
                json_sensors = json.load(f)
                json_sensor_list = [{
                    'sid': sensor['id'],
                    'name': sensor['name'],
                    'latitude': sensor['latitude'],
                    'longitude': sensor['longitude'],
                    'soil_type': sensor['soil_type'],
                    'status': sensor.get('status', 'Active'),
                    'operational_status': sensor.get('operational_status', 'Active')
                } for sensor in json_sensors]
        except (FileNotFoundError, json.JSONDecodeError):
            json_sensor_list = []
        
        # Combine both lists, avoiding duplicates based on sensor ID
        all_sensors = []
        seen_ids = set()
        
        # Add database sensors first
        for sensor in db_sensors:
            seen_ids.add(sensor.sid)
            all_sensors.append({
                'sid': sensor.sid,
                'name': sensor.name,
                'latitude': sensor.latitude,
                'longitude': sensor.longitude,
                'soil_type': sensor.soil_type,
                'status': sensor.status,
                'operational_status': sensor.operational_status
            })
        
        # Add JSON sensors that aren't in the database
        for sensor_data in json_sensor_list:
            if sensor_data['sid'] not in seen_ids:
                all_sensors.append(sensor_data)
        
        return jsonify(all_sensors), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500