# JSON Extraction API

A simple Flask API for the JSON Extraction Challenge.

## Setup
1. Install Python 3.8+.
2. Install dependencies: `pip install -r requirements.txt`.
3. Install Tesseract OCR (see below).
4. Run locally: `python app.py`.

## Tesseract Installation
- Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki, add to PATH.
- Mac: `brew install tesseract`.
- Linux: `sudo apt-get install tesseract-ocr`.

## Endpoint
- POST `/extract-json`: Accepts a base64-encoded PNG image and returns extracted JSON.

## Deployment
- Deployed on Render: [your-url-here]#   j s o n - i m a g e - e x t r a c t i o n  
 