from flask import Flask, request, jsonify
from PIL import Image
import easyocr
import base64
import io
import json
import re
import logging
import numpy as np

app = Flask(__name__)

logging.basicConfig(
    filename='api.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@app.route('/extract-json', methods=['POST'])
def extract_json_from_image():
    try:
        payload = request.get_json()
        if not payload or 'imageBase64' not in payload:
            response = {"success": False, "message": "Missing 'imageBase64' in payload"}
            logging.error(f"Request failed: {response['message']}")
            return jsonify(response), 400

        base64_string = payload['imageBase64']
        if 'base64,' in base64_string:
            base64_string = base64_string.split('base64,')[1]

        image_data = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_data))
        image = image.resize((400, 300)).convert('L')  # Grayscale

        # Convert PIL Image to numpy array for EasyOCR
        image_np = np.array(image)

        reader = easyocr.Reader(['en'])
        extracted_text = ' '.join(reader.readtext(image_np, detail=0))
        logging.info(f"Extracted text: {extracted_text}")

        try:
            json_match = re.search(r'\{[\s\S]*\}', extracted_text)
            if not json_match:
                raise ValueError("No JSON found in image")
            json_str = json_match.group(0)
            extracted_json = json.loads(json_str)
        except json.JSONDecodeError:
            response = {"success": False, "message": "Invalid JSON in image"}
            logging.error(f"Request failed: {response['message']}")
            return jsonify(response), 400
        except ValueError as e:
            response = {"success": False, "message": str(e)}
            logging.error(f"Request failed: {response['message']}")
            return jsonify(response), 400

        required_fields = ['name', 'organization', 'address', 'mobile']
        if not all(field in extracted_json for field in required_fields):
            response = {"success": False, "message": "Missing required fields in JSON"}
            logging.error(f"Request failed: {response['message']}")
            return jsonify(response), 400

        response = {
            "success": True,
            "data": extracted_json,
            "message": "Successfully extracted JSON from image"
        }
        logging.info(f"Request succeeded: {json.dumps(response)}")
        return jsonify(response), 200

    except Exception as e:
        response = {"success": False, "message": f"Error: {str(e)}"}
        logging.error(f"Request failed: {response['message']}")
        return jsonify(response), 500

if __name__ == '__main__':
    app.run(debug=True)