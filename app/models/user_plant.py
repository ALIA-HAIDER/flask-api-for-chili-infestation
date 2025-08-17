from datetime import datetime
from app import db

class User_Plant(db.Model):
    __tablename__ = 'user_plant'
    id = db.Column(db.Integer, primary_key=True)
    plant_image = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    disease_id= db.Column(db.Integer ,db.ForeignKey('disease.id', ondelete="CASCADE"), nullable=False)
    datetime = db.Column(db.DateTime, default=datetime)
