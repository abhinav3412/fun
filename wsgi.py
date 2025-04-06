import os
import sys
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from app import create_app
    logger.info("Successfully imported create_app from app module")
except Exception as e:
    logger.error(f"Failed to import create_app: {str(e)}")
    raise

try:
    # Create the application instance
    app = create_app()
    logger.info("Successfully created Flask application instance")
except Exception as e:
    logger.error(f"Failed to create Flask application: {str(e)}")
    raise

if __name__ == '__main__':
    # Set up file handler for logging
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/disaster_management.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Disaster Management System startup')
    
    # Run the application
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port) 