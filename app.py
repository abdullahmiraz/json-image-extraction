from flask import Flask, request, jsonify
from PIL import Image
import pytesseract
import base64
import io
import json
import re

app = Flask(__name__)


@app.route("/extract-json", methods=["POST"])
def extract_json_from_image():
    try:
        # Get JSON payload
        payload = request.get_json()
        if not payload or "imageBase64" not in payload:
            return (
                jsonify(
                    {"success": False, "message": "Missing 'imageBase64' in payload"}
                ),
                400,
            )

        # Extract base64 string
        base64_string = payload["imageBase64"]
        if "base64," in base64_string:
            base64_string = base64_string.split("base64,")[1]

        # Decode base64 to image
        image_data = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_data))

        # Extract text using OCR
        extracted_text = pytesseract.image_to_string(image)

        # Find JSON in text
        try:
            json_match = re.search(r"\{.*\}", extracted_text, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON found in image")

            json_str = json_match.group(0)
            extracted_json = json.loads(json_str)
        except json.JSONDecodeError:
            return jsonify({"success": False, "message": "Invalid JSON in image"}), 400
        except ValueError as e:
            return jsonify({"success": False, "message": str(e)}), 400

        # Validate required fields
        required_fields = ["name", "organization", "address", "mobile"]
        if not all(field in extracted_json for field in required_fields):
            return (
                jsonify(
                    {"success": False, "message": "Missing required fields in JSON"}
                ),
                400,
            )

        # Return extracted JSON
        return (
            jsonify(
                {
                    "success": True,
                    "data": extracted_json,
                    "message": "Successfully extracted JSON from image",
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
