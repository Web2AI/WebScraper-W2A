import logging
from io import BytesIO

import requests
import torch
from flask import Flask, jsonify, request
from PIL import Image
from transformers import BlipForConditionalGeneration, BlipProcessor

app = Flask(__name__)
logger = logging.getLogger()

model_name = "Salesforce/blip-image-captioning-base"
device = "cuda" if torch.cuda.is_available() else "cpu"
processor = BlipProcessor.from_pretrained(model_name)
model = BlipForConditionalGeneration.from_pretrained(model_name).to(device)


@app.route("/generate-description/", methods=["POST"])
def generate_description():
    try:
        data = request.get_json()
        if not data or "url" not in data:
            return jsonify({"error": "URL parameter is required"}), 400

        image_url = data["url"]
        response = requests.get(image_url, timeout=5)
        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch image from URL"}), 400

        img = Image.open(BytesIO(response.content)).convert("RGB")

        # Preprocess image and generate caption
        inputs = processor(images=img, return_tensors="pt").to(device)
        output_ids = model.generate(**inputs, max_new_tokens=50)
        caption = processor.decode(output_ids[0], skip_special_tokens=True)

        logger.info(f"Generated caption: {caption}")
        return jsonify({"description": caption})

    except Exception as e:
        logger.error(f"Error generating description: {e}")
        return jsonify({"error": f"Error generating description: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)  # nosec
