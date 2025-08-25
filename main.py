"""
Main entry point for the Flask application
"""
from wsgi import app

# This file is used by Gunicorn to run the Flask application
# It simply imports the app from wsgi.py

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)