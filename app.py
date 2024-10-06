import os
import json
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import img_to_array, load_img

# Initialize Flask app
app = Flask(__name__)

# Load disease information from JSON
with open('disease_info.json', 'r') as f:
    disease_info = json.load(f)

# Load recommendations from JSON
with open('recommendations.json', 'r') as f:
    recommendations = json.load(f)

# Load crop information from JSON
with open('crop_info.json', 'r') as f:
    crop_info = json.load(f)

# Load models
try:
    crop_classifier_model = tf.keras.models.load_model("Trained Models/balanced_crop_diseases_model.h5")  # Crop model with 15 classes
    disease_detection_model = tf.keras.models.load_model("Trained Models/crop_disease_model.h5")  # Disease detection model with 27 classes
    print("Models loaded successfully.")
except Exception as e:
    print(f"Error loading models: {e}")

# Crop class labels (15 classes)
crop_class_labels = {
    0: 'Apple Blotch',
    1: 'Apple Scab',
    2: 'Corn (Maize) Ear Rot',
    3: 'Corn (Maize) Fall Armyworm',
    4: 'Corn (Maize) Stem Borer',
    5: 'Healthy Apple',
    6: 'Healthy Corn (Maize)',
    7: 'Healthy Grapes',
    8: 'Healthy Potato',
    9: 'Healthy Strawberry',
    10: 'Healthy Tomato',
    11: 'Rotten Apple',
    12: 'Rotten Potato',
    13: 'Rotten Tomato',
    14: 'Unpickable Strawberry'
}

# Preprocess images for both models (224x224 for crop model, 150x150 for disease model)
def preprocess_image(image_path, target_size=(150, 150)):
    """Preprocess the image for model prediction based on target size."""
    try:
        image = load_img(image_path, target_size=target_size)
        image = img_to_array(image)
        image = np.expand_dims(image, axis=0)
        image = image / 255.0  # Normalize the image
        return image
    except Exception as e:
        print(f"Error preprocessing image: {e}")
        return None

# Predict crop type using the crop classifier model
def predict_with_crop_classifier(image_path):
    """Predict the crop type using the crop classifier model (15 classes)."""
    image = preprocess_image(image_path, target_size=(150, 150))  # Resize to 224x224 for crop model
    if image is None:
        return -1
    try:
        output = crop_classifier_model.predict(image)
        predicted_index = np.argmax(output)
        predicted_label = crop_class_labels.get(predicted_index, 'Unknown Crop')
        print(f"Predicted class index: {predicted_index}, Predicted label: {predicted_label}")
        return predicted_index
    except Exception as e:
        print(f"Error predicting with crop classifier model: {e}")
        return -1

# Predict disease using the disease detection model
def predict_with_disease_detection_model(image_path):
    """Predict the disease using the disease detection model (27 classes)."""
    image = preprocess_image(image_path, target_size=(150, 150))  # Resize to 150x150 for disease model
    if image is None:
        return -1
    try:
        output = disease_detection_model.predict(image)
        predicted_index = np.argmax(output)
        print(f"Predicted disease class index: {predicted_index}")
        return predicted_index
    except Exception as e:
        print(f"Error predicting with disease detection model: {e}")
        return -1

@app.route('/')
def home_page():
    return render_template('home.html')

@app.route('/index')
def ai_engine_page():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        image = request.files['image']
        task = request.form.get('task')  # Get the task type from the form
        filename = secure_filename(image.filename)
        file_path = os.path.join('static/uploads', filename)
        image.save(file_path)

        if task == 'disease':
            # Predict with disease detection model (27 classes)
            disease_pred = predict_with_disease_detection_model(file_path)
            if disease_pred != -1:
                disease = disease_info['diseases'][disease_pred]
                description = disease['description']
                prevention = disease['prevention']
                recommendation = recommendations.get(disease['name'], {})
                return render_template('submit.html',
                                       image_filename=filename,
                                       title=disease['name'],
                                       desc=description,
                                       prevent=prevention,
                                       recommendation=recommendation,
                                       is_disease=True)  # Indicate it's disease detection
            else:
                return "Error with disease prediction."

        elif task == 'crop':
            # Predict crop type with crop classifier model (15 classes)
            crop_pred = predict_with_crop_classifier(file_path)
            if crop_pred != -1:
                crop_class = crop_class_labels.get(crop_pred, 'Unknown Crop')

                # Search for the crop in crop_info.json based on name
                crop_details = next((crop for crop in crop_info['crops'] if crop['name'] == crop_class), None)

                if crop_details:
                    description = crop_details['description']
                    # Get recommendations for the crop
                    crop_recommendations = crop_details.get('recommendation', 'No preventive tips available.')

                    return render_template('crop_submit.html',
                                           image_filename=filename,
                                           crop_type=crop_class,
                                           crop_details=description,
                                           crop_recommendations=crop_recommendations)  # Pass preventive tips to the template
                else:
                    return "Crop information not available."

            else:
                return "Error with crop prediction."

        else:
            return "Invalid task selected."

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    bot_response = get_bot_response(user_message)
    return jsonify({"response": bot_response})

def get_bot_response(message):
    return "Hello, this is a placeholder response."

if __name__ == '__main__':
    app.run(debug=True)
