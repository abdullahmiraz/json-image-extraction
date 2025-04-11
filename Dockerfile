FROM python:3.9-slim

RUN apt-get update && apt-get install -y tesseract-ocr

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]