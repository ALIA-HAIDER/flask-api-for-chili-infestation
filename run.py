import os
from flask_sqlalchemy import SQLAlchemy
from app import create_app, db

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Render sets $PORT
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=port, debug=True)
