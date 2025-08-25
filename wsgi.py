"""
WSGI entry point for Gunicorn to serve the Flask application
"""
from app import app

# This file is the entry point that Gunicorn uses to run the Flask app
# It simply imports the app from app.py

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)