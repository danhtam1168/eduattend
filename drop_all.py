from app import create_app
from app.extensions import db

app = create_app()
with app.app_context():
    db.reflect()
    db.drop_all()
    print("All tables dropped successfully.")
