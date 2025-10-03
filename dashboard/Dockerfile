FROM python:3.11-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app and templates (relative to dashboard/)
COPY app.py .
COPY templates ./templates

ENV FLASK_ENV=production
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app", "--workers", "2"]
