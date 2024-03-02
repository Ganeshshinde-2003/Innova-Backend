import re
from flask import Flask, request, jsonify
import cv2
import easyocr
import numpy as np
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

with open('data.json', 'r') as file:
    ingredient_data = json.load(file)

def extract_words(text):
    return re.findall(r'\b\w+\b', text.lower())

def calculate_overall_rating(matching_ingredients):
    total_rating = 0
    total_weight = 0

    for ingredient in matching_ingredients:
        weight = 1

        total_rating += ingredient.get("rating", 0) * weight

        total_weight += weight

    overall_rating = total_rating / total_weight if total_weight > 0 else 0
    return overall_rating

@app.route('/api/ocr', methods=['POST'])
def ocr():
    try:
        file = request.files['image']

        image = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)

        reader = easyocr.Reader(['en'], gpu=False)
        text_data = ' '.join([t[1] for t in reader.readtext(image)])

        text_words = extract_words(text_data)

        matching_ingredients = []
        for ingredient in ingredient_data["ingredients"]:
            ingredient_tokens = extract_words(ingredient["name"])
            if any(token in text_words for token in ingredient_tokens):
                matching_ingredients.append(ingredient)

        matching_ingredients = list({ingredient["name"]: ingredient for ingredient in matching_ingredients}.values())

        overall_rating = calculate_overall_rating(matching_ingredients)

        response_data = {"text": text_data, "matching_ingredients": matching_ingredients, "overall_rating": overall_rating}
        
        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
