import base64
import json
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from PIL import Image
import pytesseract
import io

HOST = "localhost"
PORT = 8000


class SimpleJSONExtractor(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/extract-json":
            self.send_error(404, "Not Found")
            return

        print("[10%] Received POST request")
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            data = json.loads(body)
            print("[30%] Parsed JSON body")

            if "image_base64" not in data:
                self.send_error(400, "Missing image_base64 field")
                return

            image_base64 = data["image_base64"]

            # Remove prefix if exists
            if image_base64.startswith("data:image"):
                image_base64 = image_base64.split(",", 1)[1]

            # Sanitize the base64 string
            image_base64 = re.sub(r"\s+", "", image_base64)
            missing_padding = len(image_base64) % 4
            if missing_padding:
                image_base64 += "=" * (4 - missing_padding)

            print("[50%] Extracted and sanitized base64")

            # Decode base64
            decoded_bytes = base64.b64decode(image_base64)
            print("[70%] Decoded base64")

            try:
                # Load image from decoded bytes
                image = Image.open(io.BytesIO(decoded_bytes))
                print("[80%] Image loaded for OCR")

                # Extract text using OCR
                extracted_text = pytesseract.image_to_string(image)
                print(
                    f"[85%] OCR extraction complete. Extracted Text: {extracted_text}"
                )

                # Try to parse the extracted text as JSON
                extracted_json = json.loads(extracted_text)
                print("[90%] Parsed extracted text as JSON")

                # Respond with the extracted JSON
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(
                    json.dumps(
                        {"status": "success", "extracted_json": extracted_json}
                    ).encode()
                )
                print("[100%] Done — response sent")

            except Exception as e:
                self.send_error(400, f"Failed to extract JSON from image: {str(e)}")

        except json.JSONDecodeError:
            self.send_error(400, "Request body is not valid JSON")
        except Exception as e:
            self.send_error(500, f"Internal server error: {str(e)}")


def run_server():
    print(f"Server running at http://{HOST}:{PORT}/extract-json")
    httpd = HTTPServer((HOST, PORT), SimpleJSONExtractor)
    httpd.serve_forever()


if __name__ == "__main__":
    run_server()
