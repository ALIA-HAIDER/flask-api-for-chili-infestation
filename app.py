from datetime import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
from utils.model_loader import load_model, transform_image
from utils.predict import predict_single, predict_batch
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("POSTGRES_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Add debug print for database URL
print(f"Database URL: {os.environ.get('POSTGRES_URL')}")


db = SQLAlchemy(app)
print("SQLAlchemy initialized successfully")

 

# Configure Cloudinary
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


# Load model once on startup
model, class_names = load_model("model/model.pth")

# os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
# Ensure the UPLOAD_FOLDER exists


# UPLOAD_FOLDER = 'uploads'
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



#schema models 

class Disease(db.Model):
    __tablename__ ='disease'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    chategory= db.Column(db.String(100), nullable=False)
    solution = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime)
    updated_at = db.Column(db.DateTime, default=datetime, onupdate=datetime)


class User_Plant(db.Model):
    __tablename__ = 'user_plant'
    id = db.Column(db.Integer, primary_key=True)
    plant_image = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    disease_id= db.Column(db.Integer ,db.ForeignKey('disease.id'), nullable=False)
    datetime = db.Column(db.DateTime, default=datetime)


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




#  Routes

@app.route('/check_db', methods=['GET'])
def check_db():
    try:
        with app.app_context():
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            table_names = inspector.get_table_names()
            if table_names:
                return jsonify({"message": f"Tables found: {table_names}"}), 200
            else:
                return jsonify({"message": "No tables found in database"}), 404
    except Exception as e:
        return jsonify({"error": f"Database connection failed: {str(e)}"}), 500

@app.route('/')
def home():
    return "Image Classification API is running."

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({"error": "No image part in the request"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected image"}), 400

    # Upload to Cloudinary
    try:
        upload_result = cloudinary.uploader.upload(file)
        print (f"Image uploaded to Cloudinary: {upload_result['secure_url']}")

    except Exception as e:
        return jsonify({"error": f"Cloudinary upload failed: {str(e)}"}), 500
    
    # The image is now on Cloudinary, we can use its URL for prediction
    image_url = upload_result['secure_url']
    print (f"Image uploaded to Cloudinary: {image_url}")

    # Note: Your predict_single function must be able to handle a URL.
    # If it only handles local filepaths, you would first save locally,
    # then upload, then predict from the local path.
    # This example assumes predict_single can handle URLs.
    prediction = predict_single(image_url, model, class_names)
    
    return jsonify({"filename": file.filename, "prediction": prediction, "url": image_url})

@app.route('/predict_batch', methods=['POST'])
def predict_batch_api():
    if 'images' not in request.files:
        return jsonify({"error": "No images part in the request"}), 400

    files = request.files.getlist('images')
    if not files or all(f.filename == '' for f in files):
        return jsonify({"error": "No images uploaded"}), 400

    results = []
    image_urls_for_batch = []
    filenames_for_batch = []

    for file in files:
        if file and file.filename:
            try:
                upload_result = cloudinary.uploader.upload(file)
                image_urls_for_batch.append(upload_result['secure_url'])
                filenames_for_batch.append(secure_filename(file.filename))
            except Exception as e:
                # Add error to results and continue with other files
                results.append({"filename": secure_filename(file.filename), "error": f"Cloudinary upload failed: {str(e)}"})

    # Assuming predict_batch can handle a list of URLs
    if image_urls_for_batch:
        predictions = predict_batch(image_urls_for_batch, model, class_names)
        # Combine results
        for i, prediction in enumerate(predictions):
            results.append({
                "filename": filenames_for_batch[i],
                "prediction": prediction,
                "url": image_urls_for_batch[i]
            })

    return jsonify(results)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Render sets $PORT
    app.run(host='0.0.0.0', port=port)
