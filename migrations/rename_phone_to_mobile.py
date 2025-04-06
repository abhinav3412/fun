from app import create_app, db
from sqlalchemy import text

def upgrade():
    """
    Rename phone column to mobile in volunteers table
    """
    app = create_app()
    with app.app_context():
        # Rename phone column to mobile
        db.session.execute(text('ALTER TABLE volunteers RENAME COLUMN phone TO mobile'))
        db.session.commit()
        print("Renamed phone column to mobile in volunteers table")

def downgrade():
    """
    Rename mobile column back to phone in volunteers table
    """
    app = create_app()
    with app.app_context():
        # Rename mobile column back to phone
        db.session.execute(text('ALTER TABLE volunteers RENAME COLUMN mobile TO phone'))
        db.session.commit()
        print("Renamed mobile column back to phone in volunteers table") 