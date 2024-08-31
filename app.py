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
    crop_classifier_model = tf.keras.models.load_model("Trained Models/crop_classification_modell.h5")
    disease_detection_model = tf.keras.models.load_model("Trained Models/crop_disease_model.h5")
    print("Models loaded successfully.")
except Exception as e:
    print(f"Error loading models: {e}")

# Manually map class indices to class names (16 classes)
crop_class_labels = {
    0: 'Apple Blotch',
    1: 'Apple Healthy Apple',
    2: 'Apple Rotten Apple',
    3: 'Apple Scab',
    4: 'Corn (Maize) Ear Rot',
    5: 'Corn (Maize) Fall Armyworm',
    6: 'Corn (Maize) Healthy Corn (Maize)',
    7: 'Corn (Maize) Stem Borer',
    8: 'Grapes Healthy Grapes',
    9: 'Potato Healthy Potato',
    10: 'Potato Rotten Potato',
    11: 'Strawberry Healthy Strawberry or Pickable Strawberry',
    12: 'Strawberry Rotten Strawberry',
    13: 'Strawberry Unpickable Strawberry',
    14: 'Tomato Ripe Tomato or Healthy Tomato',
    15: 'Tomato Rotten Tomato'
}

def preprocess_image(image_path, target_size=(150, 150)):
    """Preprocess the image for model prediction."""
    try:
        image = load_img(image_path, target_size=target_size)
        image = img_to_array(image)
        image = np.expand_dims(image, axis=0)
        image = image / 255.0  # Normalize the image
        return image
    except Exception as e:
        print(f"Error preprocessing image: {e}")
        return None

def predict_with_crop_classifier(image_path):
    """Predict the crop type using the crop classifier model."""
    image = preprocess_image(image_path)
    if image is None:
        return -1
    try:
        output = crop_classifier_model.predict(image)
        return np.argmax(output)
    except Exception as e:
        print(f"Error predicting with crop classifier model: {e}")
        return -1

def predict_with_disease_detection_model(image_path):
    """Predict the disease using the disease detection model."""
    image = preprocess_image(image_path)
    if image is None:
        return -1
    try:
        output = disease_detection_model.predict(image)
        return np.argmax(output)
    except Exception as e:
        print(f"Error predicting with disease detection model: {e}")
        return -1

def format_disease_name(disease_name):
    """Format the disease name by replacing underscores with spaces, capitalizing each word, and removing duplicates."""
    words = disease_name.replace('__', ' ').replace('_', ' ').split()
    # Capitalize the first occurrence of each word
    formatted_words = [word.capitalize() for word in words]
    # Check if the crop name appears twice and remove the duplicate
    if formatted_words.count(formatted_words[0]) > 1:
        formatted_words = [formatted_words[0]] + [word for word in formatted_words[1:] if word != formatted_words[0]]
    return ' '.join(formatted_words)

@app.route('/')
def home_page():
    return render_template('home.html')

@app.route('/index')
def ai_engine_page():
    return render_template('index.html')

@app.route('/mobile-device')
def mobile_device_detected_page():
    return render_template('mobile-device.html')

@app.route('/chatbot')
def chatbot_page():
    return render_template('chatbot.html')

@app.route('/stats')
def stats():
    return render_template('stats.html')

@app.route('/weather')
def weather():
    return render_template('weather.html')

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        image = request.files['image']
        task = request.form.get('task')  # Get the task type from the form
        filename = secure_filename(image.filename)
        file_path = os.path.join('static/uploads', filename)
        image.save(file_path)

        if task == 'disease':
            # Predict with disease detection model
            disease_pred = predict_with_disease_detection_model(file_path)
            if disease_pred != -1:
                disease = disease_info['diseases'][disease_pred]
                formatted_name = format_disease_name(disease['name'])
                description = disease['description']
                prevent = disease['prevention']
                recommendation = recommendations.get(formatted_name, {})
                rec_name = recommendation.get('specialist_name', 'N/A')
                rec_description = recommendation.get('specialist_description', 'N/A')
                rec_contact = recommendation.get('specialist_contact', 'N/A')
                return render_template('submit.html',
                                       image_filename=filename,  # Pass image filename to the template
                                       title=formatted_name,
                                       desc=description,
                                       prevent=prevent,
                                       specialist_name=rec_name,
                                       specialist_description=rec_description,
                                       specialist_contact=rec_contact,
                                       is_disease=True)  # Indicate it's a disease detection
            else:
                return "Error with disease prediction."
        elif task == 'crop':
            # Predict crop type
            crop_pred = predict_with_crop_classifier(file_path)
            if crop_pred != -1:
                crop_class = crop_class_labels.get(crop_pred, 'Unknown Crop')
                crop_details = crop_info.get(crop_class, {})
                description = crop_details.get('description', 'No additional information available.')
                return render_template('crop_submit.html',
                                       image_filename=filename,  # Pass image filename to the template
                                       crop_type=crop_class,
                                       crop_details=description)
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
