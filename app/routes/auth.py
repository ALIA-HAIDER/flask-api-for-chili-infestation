from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models.admin import Admin

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':
        try:
            data = request.get_json()
            email = data.get('email')
            name = data.get('name')
            password = data.get('password')

            admin = Admin.query.filter_by(email=email).first()
            if admin:
                return jsonify({"error": "Admin with same email already exists."}), 401
            
            new_admin = Admin(email=email, name=name)
            new_admin.set_password(password)
            db.session.add(new_admin)
            db.session.commit()
            token = create_access_token(identity=str(new_admin.id))
            return jsonify({"message": "Admin created successfully", "token": token}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Failed to create admin: {str(e)}"}), 500

@auth_bp.route('/signin', methods=['POST'])
def login():
    if request.method == 'POST':
        try:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            remember = data.get('remember', False)
            
            if not all([email, password]):
                return jsonify({"error": "Email and password are required"}), 400
            
            admin = Admin.query.filter_by(email=email).first()
            if not admin or not admin.check_password(password):
                return jsonify({"error": "Please check your login details and try again."}), 404
            
            # login_user(admin, remember=remember)
            token = create_access_token(identity=str(admin.id))
            return jsonify({"message": "Admin login successful", "token": token}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Failed to signin: {str(e)}"}), 500
