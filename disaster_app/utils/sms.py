import os
from datetime import datetime
from flask import current_app
from disaster_app.models import User, db
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def send_sms(to_number, message):
    """
    Send SMS (mock implementation for testing)
    """
    try:
        print("\n===== SENDING SMS =====")
        
        # Format phone number to ensure it's in E.164 format
        if not to_number.startswith('+'):
            # If number doesn't start with +, assume it's an Indian number
            to_number = '+91' + to_number.lstrip('0')
        
        # Print debug information
        print(f"Would send SMS to {to_number}")
        print(f"Message: {message}")
        
        # Log the message
        logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
            
        log_file = os.path.join(logs_dir, 'sms_logs.txt')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] To: {to_number}\nMessage: {message}\n{'='*50}\n")
            
        current_app.logger.info(f"SMS would be sent to {to_number}")
        print(f"SMS would be sent to {to_number}")
        print("===== SMS SENDING SIMULATED =====\n")
        return True, "Message would be sent successfully"
    except Exception as e:
        current_app.logger.error(f"Error in SMS simulation: {str(e)}")
        print(f"Error in SMS simulation: {str(e)}")
        print("===== SMS SENDING FAILED =====\n")
        return False, str(e)

def send_alert_to_users(location, predicted_time, status):
    """
    Send landslide alert to all users with role 'user'
    """
    try:
        print("\n===== SENDING ALERT TO USERS =====")
        # Get all users with role 'user'
        users = User.query.filter_by(role='user').all()
        
        print(f"Found {len(users)} users with role 'user'")
        
        if not users:
            current_app.logger.warning("No users found to send alerts to")
            print("No users found to send alerts to")
            print("===== ALERT SENDING FAILED =====\n")
            return False
            
        # Prepare alert message
        message = f"🚨 LANDSLIDE ALERT 🚨\nLocation: {location}\nStatus: {status}\nPredicted Time: {predicted_time}\nPlease take necessary precautions and evacuate if advised."
        
        # Track if any SMS was sent successfully
        any_success = False
        
        # Send SMS to each user
        for user in users:
            if user.mobile:  # Only send if user has a mobile number
                print(f"Sending alert to user {user.uid} at {user.mobile}")
                success, result = send_sms(user.mobile, message)
                if success:
                    any_success = True
                    current_app.logger.info(f"Alert sent successfully to user {user.uid}")
                    print(f"Alert sent successfully to user {user.uid}")
                else:
                    current_app.logger.error(f"Failed to send SMS to user {user.uid}: {result}")
                    print(f"Failed to send SMS to user {user.uid}: {result}")
            else:
                current_app.logger.warning(f"User {user.uid} has no mobile number, skipping alert")
                print(f"User {user.uid} has no mobile number, skipping alert")
        
        if any_success:
            print("At least one alert was sent successfully")
            print("===== ALERT SENDING COMPLETED =====\n")
            return True
        else:
            print("No alerts were sent successfully")
            print("===== ALERT SENDING FAILED =====\n")
            return False
            
    except Exception as e:
        current_app.logger.error(f"Error in send_alert_to_users: {str(e)}")
        print(f"Error in send_alert_to_users: {str(e)}")
        print("===== ALERT SENDING FAILED =====\n")
        return False 