from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app import db
from app.models.disease import Disease
from app.models.user_plant import User_Plant

disease_bp = Blueprint('disease', __name__)


@disease_bp.route('/populate_diseases', methods=['POST'])
@jwt_required()
def populate_diseases():
    """
    To populate database with dummy diseases.
    """
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


@disease_bp.route('/get_diseases', methods=['GET'])
@jwt_required()
def get_diseases():
    """
    Get all diseases in the database.
    """
    try:
        diseases = Disease.query.all()
        if not diseases:
            return jsonify({"message": "No diseases found."}), 404

        disease_list = [{"id": d.id, "name": d.name, "chategory": d.chategory, "solution": d.solution} for d in diseases]
        return jsonify(disease_list), 200
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve diseases: {str(e)}"}), 500


@disease_bp.route('/update_disease/<int:disease_id>', methods=['PUT']) # test
@jwt_required()
def update_disease(disease_id):
    """
    To update a disease in the database.
    """
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


@disease_bp.route('/delete_disease/<int:disease_id>', methods=['DELETE']) # test
@jwt_required()
def delete_disease(disease_id):
    """
    To delete a particular disease from the database.
    """
    try:
        disease = Disease.query.get(disease_id)
        if not disease:
            return jsonify({"error": "Disease not found"}), 404

        User_Plant.query.filter_by(disease_id=disease.id).delete()
        db.session.delete(disease)
        db.session.commit()
        print ("Disease deleted successfully", disease)
        return jsonify({"message": "Disease deleted successfully."}), 200   
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete disease: {str(e)}"}), 500


@disease_bp.route('/clear_diseases', methods=['DELETE']) # test
@jwt_required()
def clear_diseases():
    """
    To delete all diseases from the database.
    """
    try:
        db.session.query(Disease).delete()
        db.session.commit()
        print("All diseases cleared successfully")
        return jsonify({"message": "All diseases cleared successfully."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to clear diseases: {str(e)}"}), 500
