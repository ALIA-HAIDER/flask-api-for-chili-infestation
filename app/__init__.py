import os
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required
from werkzeug.utils import secure_filename
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
from app.utils.model_loader import load_model, transform_image
from app.utils.predict import predict_single, predict_batch

load_dotenv() # Load environment variables from .env file

# ── Load model once on startup ───────────────────
model, class_names = load_model("app/model/model.pth")
db = SQLAlchemy()

def create_app() -> Flask:
    """
    Application-factory function.
    """
    app = Flask(__name__)

    # ── Core config ──────────────────────────────────
    
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("EXTERNAL_DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'alian_dev')
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'alian_dev_jwt_secret_dev')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)
    
    
    # ── JWT ──────────────────────────────────────────
    
    jwt = JWTManager(app)

    @jwt.user_identity_loader
    def user_identity_lookup(user_id):
        return str(user_id)


    # ── MySQL+SQLAlchemy database ────────────────────
    
    # Add debug print for database URL
    print(f"Database URL: {os.environ.get('POSTGRES_URL')}")
    db.init_app(app)

    print("SQLAlchemy initialized successfully")
    
    # create the database tables
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully")
        except Exception as e:
            print(f"Error creating tables: {e}")
                
    #check if the tables are created
    with app.app_context():
        try:
            # Use inspect to check tables instead of deprecated table_names()
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            table_names = inspector.get_table_names()
            if table_names:
                print(f"Tables found: {table_names}")
            else:
                print("No tables found in database")
        except Exception as e:
            print(f"Error checking tables: {e}")


    # ── Configure Cloudinary ─────────────────────────
    
    cloudinary.config(
        cloud_name = os.environ.get("CLOUDINARY_CLOUD_NAME"),
        api_key = os.environ.get("CLOUDINARY_API_KEY"),
        api_secret = os.environ.get("CLOUDINARY_API_SECRET")
    )

    # --- Debugging: Check if Cloudinary credentials are loaded ---
    print("--- Cloudinary Configuration Check ---")
    print(f"Cloud Name: {os.environ.get('CLOUDINARY_CLOUD_NAME')}")
    print(f"API Key: {os.environ.get('CLOUDINARY_API_KEY')}")
    if os.environ.get('CLOUDINARY_API_SECRET'):
        print("API Secret: Loaded successfully.")
    else:
        print("API Secret: NOT FOUND. Please check your .env file.")
    print("------------------------------------")
    # ---------------------------------------------------------


    # ── Register Blueprints ──────────────────────────

    from app.routes.auth import auth_bp    
    from app.routes.user_plant import plants_bp
    from app.routes.disease import disease_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(plants_bp)
    app.register_blueprint(disease_bp)


    # ── Other Routes ─────────────────────────────────
    
    @app.route('/')
    def home():
        return "Image Classification API is running."

    @app.route('/check_db', methods=['GET'])
    @jwt_required()
    def check_db():
        """
        To find all the tables in the database.
        """
        try:
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            table_names = inspector.get_table_names()
            if table_names:
                return jsonify({"message": f"Tables found: {table_names}"}), 200
            else:
                return jsonify({"message": "No tables found in database"}), 404
        except Exception as e:
            return jsonify({"error": f"Database connection failed: {str(e)}"}), 500


    @app.route('/delete_all',methods=['DELETE']) # test
    @jwt_required
    def delete_all():
        """
        To remove all records from the database.
        """
        try:
            db.drop_all_tables()
            db.create_all()
            print("All records deleted successfully")
            return jsonify({"message": "All records deleted successfully."}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Failed to delete all records: {str(e)}"}), 500

    return app
