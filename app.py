"""
Flask application for Health Tracker
"""
import os
from datetime import datetime

from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "health_tracker_secret_key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# configure the database
# Use SQLite for development/testing
sqlite_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'health_tracker.db')
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{sqlite_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# initialize the app with the extension
db.init_app(app)

# Import models after db is defined
from models import ActivityEntry, Goal, HealthData, Insight, NutritionEntry, User  # noqa: E402

# Create all tables
with app.app_context():
    db.create_all()


@app.route("/")
def home():
    """Home page route"""
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Login page route"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Please provide both username and password", "danger")
            return render_template("login.html")

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session["user_id"] = user.id
            session["username"] = user.username
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password", "danger")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Registration page route"""
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        # Validate input
        if not username or not email or not password:
            flash("Please fill in all required fields", "danger")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match", "danger")
            return render_template("register.html")

        # Check if username or email already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists", "danger")
            return render_template("register.html")

        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash("Email already registered", "danger")
            return render_template("register.html")

        # Create new user
        new_user = User(
            username=username,
            email=email,
            full_name=request.form.get("full_name", ""),
            created_at=datetime.utcnow(),
            is_active=True
        )
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/logout")
def logout():
    """Logout route"""
    session.pop("user_id", None)
    session.pop("username", None)
    flash("You have been logged out", "info")
    return redirect(url_for("home"))


@app.route("/dashboard")
def dashboard():
    """Dashboard page route"""
    if "user_id" not in session:
        flash("Please log in to access your dashboard", "warning")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    user = User.query.get(user_id)

    # Get the latest health data
    latest_health_data = HealthData.query.filter_by(user_id=user_id).order_by(HealthData.date.desc()).first()

    # Get active goals
    active_goals = Goal.query.filter_by(user_id=user_id, is_achieved=False).all()

    # Get recent insights
    recent_insights = Insight.query.filter_by(user_id=user_id).order_by(Insight.created_at.desc()).limit(3).all()

    return render_template(
        "dashboard.html",
        user=user,
        health_data=latest_health_data,
        active_goals=active_goals,
        recent_insights=recent_insights
    )


@app.route("/health-data", methods=["GET", "POST"])
def health_data():
    """Health data page route"""
    if "user_id" not in session:
        flash("Please log in to access your health data", "warning")
        return redirect(url_for("login"))

    user_id = session["user_id"]

    if request.method == "POST":
        # Get form data
        weight = request.form.get("weight", type=float)
        height = request.form.get("height", type=float)
        steps = request.form.get("steps", type=int)
        sleep_hours = request.form.get("sleep_hours", type=float)
        water_intake = request.form.get("water_intake", type=float)
        calories_consumed = request.form.get("calories_consumed", type=int)
        calories_burned = request.form.get("calories_burned", type=int)
        heart_rate = request.form.get("heart_rate", type=int)
        blood_pressure_systolic = request.form.get("blood_pressure_systolic", type=int)
        blood_pressure_diastolic = request.form.get("blood_pressure_diastolic", type=int)
        notes = request.form.get("notes")

        # Create new health data entry
        health_data_entry = HealthData(
            user_id=user_id,
            date=datetime.utcnow(),
            weight=weight,
            height=height,
            steps=steps,
            sleep_hours=sleep_hours,
            water_intake=water_intake,
            calories_consumed=calories_consumed,
            calories_burned=calories_burned,
            heart_rate=heart_rate,
            blood_pressure_systolic=blood_pressure_systolic,
            blood_pressure_diastolic=blood_pressure_diastolic,
            notes=notes
        )

        db.session.add(health_data_entry)
        db.session.commit()
        
        # Update streak and check for new achievements
        from services.gamification_service import update_user_streak, check_achievements
        update_user_streak(user_id)
        new_achievements = check_achievements(user_id)
        
        if new_achievements:
            achievement_names = [a['name'] for a in new_achievements]
            flash(f"Health data recorded successfully! You've earned {len(new_achievements)} new achievement(s): {', '.join(achievement_names)}", "success")
        else:
            flash("Health data recorded successfully", "success")
            
        return redirect(url_for("health_data"))

    # Get health data history
    health_history = HealthData.query.filter_by(user_id=user_id).order_by(HealthData.date.desc()).all()

    return render_template("health_data.html", health_history=health_history)


@app.route("/add-nutrition", methods=["POST"])
def add_nutrition_entry():
    """Add a nutrition entry"""
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Not logged in"})

    user_id = session["user_id"]
    health_data_id = request.form.get("health_data_id", type=int)
    
    if not health_data_id:
        # Get or create a health data entry for today
        today = datetime.utcnow().date()
        health_data = HealthData.query.filter_by(
            user_id=user_id
        ).filter(
            db.func.date(HealthData.date) == today
        ).first()
        
        if not health_data:
            health_data = HealthData(user_id=user_id, date=datetime.utcnow())
            db.session.add(health_data)
            db.session.commit()
        
        health_data_id = health_data.id

    # Create nutrition entry
    nutrition_entry = NutritionEntry(
        health_data_id=health_data_id,
        meal_type=request.form.get("meal_type"),
        food_name=request.form.get("food_name"),
        calories=request.form.get("calories", type=int),
        protein=request.form.get("protein", type=float),
        carbs=request.form.get("carbs", type=float),
        fat=request.form.get("fat", type=float),
        time=datetime.utcnow()
    )

    db.session.add(nutrition_entry)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Nutrition entry added",
        "entry_id": nutrition_entry.id
    })


@app.route("/add-activity", methods=["POST"])
def add_activity_entry():
    """Add an activity entry"""
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Not logged in"})

    user_id = session["user_id"]
    health_data_id = request.form.get("health_data_id", type=int)
    
    if not health_data_id:
        # Get or create a health data entry for today
        today = datetime.utcnow().date()
        health_data = HealthData.query.filter_by(
            user_id=user_id
        ).filter(
            db.func.date(HealthData.date) == today
        ).first()
        
        if not health_data:
            health_data = HealthData(user_id=user_id, date=datetime.utcnow())
            db.session.add(health_data)
            db.session.commit()
        
        health_data_id = health_data.id

    # Create activity entry
    activity_entry = ActivityEntry(
        health_data_id=health_data_id,
        activity_type=request.form.get("activity_type"),
        duration=request.form.get("duration", type=int),
        calories_burned=request.form.get("calories_burned", type=int),
        time=datetime.utcnow()
    )

    db.session.add(activity_entry)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Activity entry added",
        "entry_id": activity_entry.id
    })


@app.route("/insights")
def insights():
    """Insights page route"""
    if "user_id" not in session:
        flash("Please log in to access your insights", "warning")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    
    # Get user's health data
    health_data = HealthData.query.filter_by(user_id=user_id).order_by(HealthData.date.desc()).first()
    
    # Get insights
    insights = Insight.query.filter_by(user_id=user_id).order_by(Insight.created_at.desc()).all()

    return render_template("insights.html", health_data=health_data, insights=insights)


@app.route("/generate-insight", methods=["POST"])
def generate_insight():
    """Generate a new AI insight"""
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Not logged in"})

    user_id = session["user_id"]
    
    # Get the user's recent health data
    health_data = HealthData.query.filter_by(user_id=user_id).order_by(HealthData.date.desc()).first()
    
    if not health_data:
        return jsonify({"success": False, "error": "No health data available for insights"})
    
    # Import Groq service
    from services.groq_service import generate_health_insight
    
    try:
        # Generate insight using Groq
        insight_text = generate_health_insight(health_data)
        
        # Save the insight to the database
        new_insight = Insight(
            user_id=user_id,
            insight_text=insight_text,
            category="health",
            created_at=datetime.utcnow(),
            is_read=False
        )
        
        db.session.add(new_insight)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "insight": insight_text
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })


@app.route("/goals", methods=["GET", "POST"])
def goals():
    """Goals page route"""
    if "user_id" not in session:
        flash("Please log in to access your goals", "warning")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    
    if request.method == "POST":
        # Create a new goal
        new_goal = Goal(
            user_id=user_id,
            name=request.form.get("name"),
            description=request.form.get("description"),
            target_value=request.form.get("target_value", type=float),
            current_value=request.form.get("current_value", type=float, default=0),
            goal_type=request.form.get("goal_type"),
            start_date=datetime.utcnow()
        )
        
        target_date = request.form.get("target_date")
        if target_date:
            new_goal.target_date = datetime.strptime(target_date, "%Y-%m-%d")
        
        db.session.add(new_goal)
        db.session.commit()
        
        flash("New goal created successfully", "success")
        return redirect(url_for("goals"))
    
    # Get active and completed goals
    active_goals = Goal.query.filter_by(user_id=user_id, is_achieved=False).all()
    completed_goals = Goal.query.filter_by(user_id=user_id, is_achieved=True).all()
    
    return render_template(
        "goals.html",
        active_goals=active_goals,
        completed_goals=completed_goals
    )


@app.route("/update-goal/<int:goal_id>", methods=["POST"])
def update_goal(goal_id):
    """Update a goal"""
    if "user_id" not in session:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"success": False, "error": "Not logged in"})
        flash("Please log in to update goals", "warning")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    goal = Goal.query.filter_by(id=goal_id, user_id=user_id).first()
    
    if not goal:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"success": False, "error": "Goal not found"})
        flash("Goal not found", "danger")
        return redirect(url_for("goals"))
    
    # Update goal fields
    if "current_value" in request.form:
        goal.current_value = request.form.get("current_value", type=float)
    
    if "is_achieved" in request.form:
        goal.is_achieved = request.form.get("is_achieved") == "true"
    
    db.session.commit()
    
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"success": True})
    
    flash("Goal updated successfully", "success")
    return redirect(url_for("goals"))


@app.route("/delete-goal/<int:goal_id>", methods=["POST"])
def delete_goal(goal_id):
    """Delete a goal"""
    if "user_id" not in session:
        flash("Please log in to delete goals", "warning")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    goal = Goal.query.filter_by(id=goal_id, user_id=user_id).first()
    
    if not goal:
        flash("Goal not found", "danger")
    else:
        db.session.delete(goal)
        db.session.commit()
        flash("Goal deleted successfully", "success")
    
    return redirect(url_for("goals"))


@app.route("/achievements")
def achievements():
    """Achievements and streaks page"""
    if "user_id" not in session:
        flash("Please log in to view your achievements", "warning")
        return redirect(url_for("login"))
    
    user_id = session["user_id"]
    user = User.query.get(user_id)
    
    # Import achievements service
    from services.gamification_service import get_user_achievements, get_unearned_achievements, create_default_achievements
    
    # Make sure default achievements exist
    create_default_achievements()
    
    # Get user's earned and unearned achievements
    earned_achievements = get_user_achievements(user_id)
    unearned_achievements = get_unearned_achievements(user_id)
    
    # Group achievements by category
    earned_by_category = {}
    for achievement in earned_achievements:
        category = achievement["category"]
        if category not in earned_by_category:
            earned_by_category[category] = []
        earned_by_category[category].append(achievement)
    
    unearned_by_category = {}
    for achievement in unearned_achievements:
        category = achievement["category"]
        if category not in unearned_by_category:
            unearned_by_category[category] = []
        unearned_by_category[category].append(achievement)
    
    return render_template(
        "achievements.html",
        user=user,
        earned_achievements=earned_achievements,
        unearned_achievements=unearned_achievements,
        earned_by_category=earned_by_category,
        unearned_by_category=unearned_by_category
    )


@app.route("/update-streak", methods=["POST"])
def update_streak():
    """Update user streak and check for achievements"""
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Not logged in"})
    
    user_id = session["user_id"]
    
    # Import streak and achievements services
    from services.gamification_service import update_user_streak, check_achievements, get_new_achievement_notifications
    
    # Update streak
    streak_info = update_user_streak(user_id)
    
    # Check for new achievements
    new_achievements = check_achievements(user_id)
    
    # Get achievement notifications
    notifications = get_new_achievement_notifications(user_id)
    
    return jsonify({
        "success": True,
        "streak_info": streak_info,
        "new_achievements": new_achievements,
        "notifications": notifications
    })


# Register blueprints for meal planning, notifications, and chatbot
from routers.meal_planning_router import meal_planning
from routers.chatbot_router import chatbot

app.register_blueprint(meal_planning)
app.register_blueprint(chatbot)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)