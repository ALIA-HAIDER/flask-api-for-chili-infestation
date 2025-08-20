from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_login import current_user
from flask_jwt_extended import jwt_required
from app import db, cloudinary, model, class_names
from app.utils.predict import predict_single, predict_batch
from app.models.disease import Disease
from app.models.user_plant import User_Plant

plants_bp = Blueprint('plants', __name__)


@plants_bp.route('/upload_plant',methods=['POST'])
# @jwt_required()
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


@plants_bp.route('/get_user_plants', methods=['GET'])
@jwt_required()
def get_user_plants():
    """
    To get all the user plants in the database.
    """
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
