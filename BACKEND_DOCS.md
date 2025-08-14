# Backend Documentation: Chili Infestation Prediction API (PyTorch)

## 1. Overview

This document outlines the backend architecture and API for the Chili Infestation Prediction service. The service is a Flask-based web application that uses a **PyTorch** deep learning model to predict diseases in chili plants from user-uploaded images. It supports both single and batch image predictions.

## 2. Project Structure

The project is organized into the following key files and directories:

```
.
├── app.py                  # Main Flask application, handles routing and prediction logic.
├── requirements.txt        # Python dependencies.
├── uploads/                # Directory for storing uploaded images.
├── model/
│   └── model.pth           # The trained PyTorch model file.
└── utils/
    ├── model_loader.py     # Utility to load the PyTorch model.
    └── predict.py          # Functions for single and batch prediction.
```

-   **`app.py`**: The entry point of the Flask application. It defines the API endpoints, handles file uploads, and integrates the model for predictions.
-   **`utils/model_loader.py`**: Contains the logic to load the `model.pth` file and class names.
-   **`utils/predict.py`**: Contains the `predict_single` and `predict_batch` functions.
-   **`model/model.pth`**: The serialized, trained PyTorch model.
-   **`uploads/`**: Temporarily stores images uploaded by users for prediction.

## 3. Configuration (Environment Variables)

The application requires environment variables for configuration, particularly for Cloudinary integration.

1.  Create a file named `.env` in the project's root directory.
2.  Add your credentials to this file. It should look like this:

    ```
    # .env
    CLOUDINARY_CLOUD_NAME="your_cloud_name"
    CLOUDINARY_API_KEY="your_api_key"
    CLOUDINARY_API_SECRET="your_api_secret"
    ```

3.  **Important**: Add the `.env` file to your `.gitignore` file to prevent your secrets from being exposed in version control.
    ```
    # .gitignore
    .env
    venv/
    __pycache__/
    ```

## 4. Setup and Installation

To run the application locally, follow these steps.

**Prerequisites:**
- Python 3.8+
- `pip` package manager

**Steps:**

1.  **Clone the Repository**
    ```bash
    git clone <repository-url>
    cd flask-api-for-chili-infestation
    ```

2.  **Create and Activate a Virtual Environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies**
    Install all required packages using the new `requirements.txt` file.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Place the Model File**
    Ensure your trained PyTorch model is located at `model/model.pth`.

5.  **Run the Application**
    ```bash
    python app.py
    ```
    The application will be available at `http://127.0.0.1:5000`.

## 5. API Endpoints

The application exposes three endpoints.

### 5.1. Health Check

-   **Endpoint**: `/`
-   **Method**: `GET`
-   **Description**: A simple health check endpoint to confirm the API is running.
-   **Response**:
    -   `200 OK`: Returns the raw text `Image Classification API is running.`.

### 5.2. Predict Single Image

-   **Endpoint**: `/predict`
-   **Method**: `POST`
-   **Description**: Accepts a single image file and returns the predicted class.
-   **Request Body**: `multipart/form-data` with a key `image`.
-   **cURL Example**:
    ```bash
    curl -X POST http://127.0.0.1:5000/predict \
      -F "image=@/path/to/your/chilli_image.jpg"
    ```
-   **Success Response (`200 OK`)**:
    ```json
    {
      "filename": "chilli_image.jpg",
      "prediction": "Chilli_Leaf_Curl",
      "url": "http://res.cloudinary.com/..."
    }
    ```

### 5.3. Predict Batch of Images

-   **Endpoint**: `/predict_batch`
-   **Method**: `POST`
-   **Description**: Accepts multiple image files and returns predictions for each.
-   **Request Body**: `multipart/form-data` with multiple files attached to the key `images`.
-   **cURL Example**:
    ```bash
    curl -X POST http://127.0.0.1:5000/predict_batch \
      -F "images=@/path/to/image1.jpg" \
      -F "images=@/path/to/image2.png"
    ```
-   **Success Response (`200 OK`)**:
    ```json
    [
        {
            "filename": "image1.jpg",
            "prediction": "Healthy",
            "url": "http://res.cloudinary.com/..."
        },
        {
            "filename": "image2.png",
            "prediction": "Chilli_Whitefly",
            "url": "http://res.cloudinary.com/..."
        }
    ]
    ```

## 6. Model Information

-   **Framework**: PyTorch
-   **Model File**: The model is loaded from `model/model.pth`.

## 7. Troubleshooting

### Error: `Cloudinary upload failed: Invalid Signature`

This error means your Cloudinary credentials (`cloud_name`, `api_key`, `api_secret`) are incorrect or not being loaded. Follow this checklist:

1.  **Check the `.env` file**:
    *   Ensure the file is named exactly `.env` (starting with a dot) and is in the root directory of your project.
    *   Make sure the variable names are exactly `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, and `CLOUDINARY_API_SECRET`.
    *   Verify that you have copied the values from your Cloudinary Dashboard correctly, with no extra spaces or characters. Do **not** put quotes around the values in the `.env` file.

2.  **Check the Server Log**:
    *   Restart your Flask server (`python app.py`).
    *   Look for the "Cloudinary Configuration Check" output in your terminal.
    *   If it shows `None` for `Cloud Name` or `API Key`, or `API Secret: NOT FOUND`, it confirms the `.env` file is not being read correctly.

3.  **Restart the Server**:
    *   If you make any changes to the `.env` file, you **must** stop and restart the Flask server for the changes to take effect.
        }
        ```

    -   **Example 3: Disallowed file type**
        ```json
        {
          "error": "File type not allowed"
        }
        ```

## 7. Model Information

-   **Architecture**: Keras `Xception` model, pre-trained on ImageNet, with a custom classification head.
-   **Framework**: TensorFlow / Keras.
-   **Input Shape**: `(299, 299, 3)`. Images are automatically resized.
-   **Model File**: The model is loaded from `utils/model.h5`.
