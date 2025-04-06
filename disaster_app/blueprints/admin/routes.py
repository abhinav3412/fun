from flask import render_template, request, jsonify, flash, redirect, url_for
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
    """Render the sensor management page."""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'static', 'data')
    try:
        with open(os.path.join(data_dir, 'sensor_data.json'), 'r') as f:
            sensor_data = json.load(f)
    except FileNotFoundError:
        sensor_data = []
    return render_template('admin/sensor.html', sensor_data=sensor_data)

@admin_bp.route('/add_sensor', methods=['POST'])
@login_required
def add_sensor():
    """Add a new sensor."""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'static', 'data')
    try:
        with open(os.path.join(data_dir, 'sensor_data.json'), 'r') as f:
            sensor_data = json.load(f)
    except FileNotFoundError:
        sensor_data = []
    
    new_sensor = {
        'id': len(sensor_data) + 1,
        'name': request.form['name'],
        'latitude': float(request.form['latitude']),
        'longitude': float(request.form['longitude']),
        'soil_type': request.form['soil_type'],
        'status': 'Active',
        'operational_status': 'Active'
    }
    
    sensor_data.append(new_sensor)
    
    with open(os.path.join(data_dir, 'sensor_data.json'), 'w') as f:
        json.dump(sensor_data, f, indent=4)
    
    flash('Sensor added successfully!', 'success')
    return redirect(url_for('admin.sensor'))

@admin_bp.route('/delete_sensor/<int:sensor_id>', methods=['POST'])
@login_required
def delete_sensor(sensor_id):
    """Delete a sensor."""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'static', 'data')
    try:
        with open(os.path.join(data_dir, 'sensor_data.json'), 'r') as f:
            sensor_data = json.load(f)
    except FileNotFoundError:
        sensor_data = []
    
    sensor_data = [s for s in sensor_data if s['id'] != sensor_id]
    
    with open(os.path.join(data_dir, 'sensor_data.json'), 'w') as f:
        json.dump(sensor_data, f, indent=4)
    
    flash('Sensor deleted successfully!', 'success')
    return redirect(url_for('admin.sensor'))

@admin_bp.route('/get_sensors')
@login_required
def get_sensors():
    """Get all sensors."""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'static', 'data')
    try:
        with open(os.path.join(data_dir, 'sensor_data.json'), 'r') as f:
            sensor_data = json.load(f)
    except FileNotFoundError:
        sensor_data = []
    return jsonify(sensor_data)

@admin_bp.route('/get_sensor/<int:sensor_id>')
@login_required
def get_sensor(sensor_id):
    """Get a specific sensor."""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'static', 'data')
    try:
        with open(os.path.join(data_dir, 'sensor_data.json'), 'r') as f:
            sensor_data = json.load(f)
    except FileNotFoundError:
        sensor_data = []
    
    sensor = next((s for s in sensor_data if s['id'] == sensor_id), None)
    if sensor:
        return jsonify(sensor)
    return jsonify({'error': 'Sensor not found'}), 404

@admin_bp.route('/update_sensor/<int:sensor_id>', methods=['POST'])
@login_required
def update_sensor(sensor_id):
    """Update a sensor."""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'static', 'data')
    try:
        with open(os.path.join(data_dir, 'sensor_data.json'), 'r') as f:
            sensor_data = json.load(f)
    except FileNotFoundError:
        sensor_data = []
    
    for sensor in sensor_data:
        if sensor['id'] == sensor_id:
            sensor['name'] = request.form['name']
            sensor['latitude'] = float(request.form['latitude'])
            sensor['longitude'] = float(request.form['longitude'])
            sensor['soil_type'] = request.form['soil_type']
            sensor['status'] = request.form['status']
            sensor['operational_status'] = request.form['operational_status']
            break
    
    with open(os.path.join(data_dir, 'sensor_data.json'), 'w') as f:
        json.dump(sensor_data, f, indent=4)
    
    flash('Sensor updated successfully!', 'success')
    return redirect(url_for('admin.sensor'))

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
        
        # Combine and deduplicate sensors
        all_sensors = []
        seen_ids = set()
        
        # Add JSON sensors first
        for sensor in json_sensor_list:
            if sensor['sid'] not in seen_ids:
                all_sensors.append(sensor)
                seen_ids.add(sensor['sid'])
        
        # Add database sensors
        for sensor in db_sensors:
            if sensor.sid not in seen_ids:
                all_sensors.append({
                    'sid': sensor.sid,
                    'name': sensor.name,
                    'latitude': sensor.latitude,
                    'longitude': sensor.longitude,
                    'soil_type': sensor.soil_type,
                    'status': sensor.status,
                    'operational_status': sensor.operational_status
                })
                seen_ids.add(sensor.sid)
        
        return jsonify({
            'success': True,
            'sensors': all_sensors
        })
    except Exception as e:
        print(f"Error in get_sensor_data: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500