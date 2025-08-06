from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
from utils.model_loader import load_model, transform_image
from utils.predict import predict_single, predict_batch

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load model once on startup
model, class_names = load_model("model/model.pth")

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

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    prediction = predict_single(filepath, model, class_names)
    return jsonify({"filename": filename, "prediction": prediction})

@app.route('/predict_batch', methods=['POST'])
def predict_batch_api():
    if 'images' not in request.files:
        return jsonify({"error": "No images part in the request"}), 400

    files = request.files.getlist('images')
    if not files:
        return jsonify({"error": "No images uploaded"}), 400

    filepaths = []
    for file in files:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        filepaths.append(filepath)

    predictions = predict_batch(filepaths, model, class_names)
    return jsonify(predictions)

if __name__ == '__main__':
    app.run(debug=True)
