import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing.image import load_img, img_to_array

def preprocess_image(image_path, target_size=(150, 150)):
    image = load_img(image_path, target_size=target_size)
    image = img_to_array(image)
    image = np.expand_dims(image, axis=0)
    image = image / 255.0
    return image

# Load the intermediate model
intermediate_model = tf.keras.models.load_model("intermediate_classifier_model.h5")

def detect_image_type(image_path):
    image = preprocess_image(image_path)
    output = intermediate_model.predict(image)
    prob = output[0][0]  # Adjust index based on model output
    return 'crop' if prob > 0.5 else 'leaf'

# Path to your test image
test_image_path = 'fresa_000.jpg'

# Test the function
result = detect_image_type(test_image_path)
print(f'The image is classified as: {result}')
