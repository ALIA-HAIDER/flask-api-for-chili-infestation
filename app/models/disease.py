from datetime import datetime
from app import db

class Disease(db.Model):
    __tablename__ ='disease'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    chategory= db.Column(db.String(100), nullable=False)
    solution = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())
