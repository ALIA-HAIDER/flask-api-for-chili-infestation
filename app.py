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
from flask_cors import CORS

load_dotenv() # Load environment variables from .env file

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "https://chilli-infestation-detection-web-ap.vercel.app"]}})


app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("EXTERNAL_DATABASE_URL")
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
    name = db.Column(db.String(100), nullable=False, unique=True)
    chategory= db.Column(db.String(100), nullable=False)
    solution = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())


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

@app.route('/populate_diseases', methods=['POST'])
def populate_diseases():
    try:
        # Example data to populate the diseases table
        diseases = [
            {"name": "Aphids", "chategory": "Insect", "solution": "Use insecticidal soap or neem oil."},
            {"name": "Healthy", "chategory": "Healthy", "solution": "No action needed."},
            {"name": "mites+thrips", "chategory": "Insect", "solution": "Use miticides or insecticidal soap."}
        ]

        for disease in diseases:
            new_disease = Disease(**disease)
            db.session.add(new_disease)
        db.session.commit()
        return jsonify({"message": "Diseases populated successfully."}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to populate diseases: {str(e)}"}), 500

@app.route('/get_diseases', methods=['GET'])
def get_diseases():
    try:
        diseases = Disease.query.all()
        if not diseases:
            return jsonify({"message": "No diseases found."}), 404

        disease_list = [{"id": d.id, "name": d.name, "chategory": d.chategory, "solution": d.solution} for d in diseases]
        return jsonify(disease_list), 200
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve diseases: {str(e)}"}), 500

@app.route('/update_disease/<int:disease_id>', methods=['PUT'])
def update_disease(disease_id):
    try:
        disease = Disease.query.get(disease_id)
        if not disease:
            return jsonify({"error": "Disease not found"}), 404

        data = request.get_json()
        disease.solution = data.get("solution", disease.solution)

        db.session.commit()
        print ("Disease updated successfully", disease)
        return jsonify({"message": "Disease updated successfully."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update disease: {str(e)}"}), 500

@app.route('/delete_disease/<int:disease_id>', methods=['DELETE'])
def delete_disease(disease_id):
    try:
        disease = Disease.query.get(disease_id)
        if not disease:
            return jsonify({"error": "Disease not found"}), 404

        db.session.delete(disease)
        db.session.commit()
        print ("Disease deleted successfully", disease)
        return jsonify({"message": "Disease deleted successfully."}), 200   
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete disease: {str(e)}"}), 500

@app.route('/clear_diseases', methods=['DELETE'])
def clear_diseases():
    try:
        db.session.query(Disease).delete()
        db.session.commit()
        print("All diseases cleared successfully")
        return jsonify({"message": "All diseases cleared successfully."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to clear diseases: {str(e)}"}), 500


@app.route('/upload_plant',methods=['POST'])
def upload_plant():
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

    try:
        prediction = predict_single(image_url, model, class_names)
        print(f"Prediction: {prediction}")
        # return jsonify({"filename": file.filename, "prediction": prediction, "url": image_url})
    except Exception as e:
        print(f"Prediction failed: {str(e)}")

    try:
        res=Disease.query.filter_by(name=prediction).first()
        if not res:
            return jsonify({"error": "Disease not found"}), 404
        new_plant = User_Plant(
            plant_image=image_url,
            location=request.form.get('location', 'Unknown'),
            disease_id=res.id,
            datetime=datetime.now()
        )

        db.session.add(new_plant)
        db.session.commit()
        print("New plant record added successfully", new_plant)
    except Exception as e:
        db.session.rollback()
        print(f"Error adding new plant record: {str(e)}")
        return jsonify({"error": f"Failed to add plant record: {str(e)}"}), 500

    return jsonify({"id": new_plant.id, "filename": file.filename,"disease_id": res.id, "prediction": res.name, "url": new_plant.plant_image ,"Solution": res.solution}), 200


@app.route('/get_user_plants', methods=['GET'])
def get_user_plants():
    try:
        User_Plants= User_Plant.query.all()
        if not User_Plants:
            return jsonify({"message": "No user plants found."}), 404

        user_plants_list = [{
            "id": up.id,
            "plant_image": up.plant_image,
            "location": up.location,
            "disease_id": up.disease_id,
            "datetime": up.datetime.strftime("%Y-%m-%d %H:%M:%S")
        } for up in User_Plants]
        
        return jsonify(user_plants_list), 200
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve user plants: {str(e)}"}), 500

    # @app.route('/predict', methods=['POST'])
    # def predict():
    #     if 'image' not in request.files:
    #         return jsonify({"error": "No image part in the request"}), 400


@app.route('/delete_all',methods=['DELETE'])
def delete_all():
    try:
        db.drop_all_tables()
        db.create_all()
        print("All records deleted successfully")
        return jsonify({"message": "All records deleted successfully."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete all records: {str(e)}"}), 500



#     file = request.files['image']
#     if file.filename == '':
#         return jsonify({"error": "No selected image"}), 400

#     # Upload to Cloudinary
#     try:
#         upload_result = cloudinary.uploader.upload(file)
#         print (f"Image uploaded to Cloudinary: {upload_result['secure_url']}")

#     except Exception as e:
#         return jsonify({"error": f"Cloudinary upload failed: {str(e)}"}), 500
    
#     # The image is now on Cloudinary, we can use its URL for prediction
#     image_url = upload_result['secure_url']
#     print (f"Image uploaded to Cloudinary: {image_url}")


#     # Note: Your predict_single function must be able to handle a URL.
#     # If it only handles local filepaths, you would first save locally,
#     # then upload, then predict from the local path.
#     # This example assumes predict_single can handle URLs.
#     prediction = predict_single(image_url, model, class_names)
    
#     return jsonify({"filename": file.filename, "prediction": prediction, "url": image_url})

# @app.route('/predict_batch', methods=['POST'])
# def predict_batch_api():
#     if 'images' not in request.files:
#         return jsonify({"error": "No images part in the request"}), 400

#     files = request.files.getlist('images')
#     if not files or all(f.filename == '' for f in files):
#         return jsonify({"error": "No images uploaded"}), 400

#     results = []
#     image_urls_for_batch = []
#     filenames_for_batch = []

#     for file in files:
#         if file and file.filename:
#             try:
#                 upload_result = cloudinary.uploader.upload(file)
#                 image_urls_for_batch.append(upload_result['secure_url'])
#                 filenames_for_batch.append(secure_filename(file.filename))
#             except Exception as e:
#                 # Add error to results and continue with other files
#                 results.append({"filename": secure_filename(file.filename), "error": f"Cloudinary upload failed: {str(e)}"})

#     # Assuming predict_batch can handle a list of URLs
#     if image_urls_for_batch:
#         predictions = predict_batch(image_urls_for_batch, model, class_names)
#         # Combine results
#         for i, prediction in enumerate(predictions):
#             results.append({
#                 "filename": filenames_for_batch[i],
#                 "prediction": prediction,
#                 "url": image_urls_for_batch[i]
#             })

#     return jsonify(results)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Render sets $PORT
    app.run(host='0.0.0.0', port=port)
