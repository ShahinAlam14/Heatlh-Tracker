# Health Tracker App Installation Guide

This guide will help you set up and run the Health Tracker App locally.

## System Requirements
- Python 3.10 or newer
- PostgreSQL database

## Installation Steps

### 1. Clone the repository
```bash
git clone <repository-url>
cd health-tracker-app
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
# You can copy these dependencies into your requirements.txt file
# and run: pip install -r requirements.txt

# Or install them individually:
pip install flask==2.3.3 flask-login==0.6.2 flask-sqlalchemy==3.1.1 flask-wtf==1.2.1 
pip install gunicorn==23.0.0 jinja2==3.1.2 openai==1.18.0 passlib==1.7.4 
pip install sqlalchemy==2.0.27 werkzeug==2.3.7 python-dotenv==1.0.0
```

Note: We removed psycopg2-binary since we're using SQLite instead of PostgreSQL.

### 4. Set up environment variables
Create a `.env` file in the root directory with the following variables:
```
OPENAI_API_KEY=your-openai-api-key
SESSION_SECRET=your-session-secret
```

The default session secret is "health_tracker_secret_key" if you don't set one.

### 5. Database setup
The application uses SQLite by default, which is a file-based database and doesn't need a separate installation. The database file will be created automatically when you first run the application.

### 6. Run the application
```bash
# Option 1: Using the run.py script
python run.py

# Option 2: Using Flask command (specify the app)
flask --app app:app run --host=0.0.0.0 --port=5000

# Option 3: Using Gunicorn (for production)
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload wsgi:app
```

## Application Structure

- `app.py` - Main Flask application with routes
- `models.py` - Database models
- `services/` - Business logic and external API integrations
- `templates/` - HTML templates using Jinja2
- `static/` - CSS, JavaScript, and static assets

## Features

- User authentication
- Health data tracking
- Goal setting and tracking
- AI-powered health insights
- Achievement badges and gamification
- Meal planning
- AI-powered health assistant chatbot

## Environment Variables

- `OPENAI_API_KEY`: API key for OpenAI integration (required for AI features)
- `SESSION_SECRET`: Secret key for Flask sessions (optional, default provided)

## Note for Production Deployment

When deploying to production:
1. Set `app.debug = False`
2. Use a proper WSGI server (e.g., Gunicorn)
3. Set up proper database connections with pooling
4. Set up proper security headers
5. Use HTTPS