from app import create_app, db
from app.models import Volunteer

def upgrade():
    """
    Add status column to volunteer table
    """
    app = create_app()
    with app.app_context():
        # Add status column with default value 'pending'
        db.session.execute('ALTER TABLE volunteer ADD COLUMN status VARCHAR(20) DEFAULT "pending"')
        db.session.commit()
        print("Added status column to volunteer table")

def downgrade():
    """
    Remove status column from volunteer table
    """
    app = create_app()
    with app.app_context():
        # SQLite doesn't support DROP COLUMN directly, so we need to recreate the table
        # This is a simplified version - in production you'd want to preserve data
        db.session.execute('CREATE TABLE volunteer_new (vid INTEGER PRIMARY KEY, user_id INTEGER, name VARCHAR(100), email VARCHAR(100), mobile VARCHAR(20), location VARCHAR(100), role_id VARCHAR, FOREIGN KEY(user_id) REFERENCES users(uid), FOREIGN KEY(role_id) REFERENCES volunteer_role(role_id))')
        db.session.execute('INSERT INTO volunteer_new SELECT vid, user_id, name, email, mobile, location, role_id FROM volunteer')
        db.session.execute('DROP TABLE volunteer')
        db.session.execute('ALTER TABLE volunteer_new RENAME TO volunteer')
        db.session.commit()
        print("Removed status column from volunteer table")

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'downgrade':
        downgrade()
    else:
        upgrade() 