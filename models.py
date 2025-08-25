"""
Database models for the Health Tracker application
"""
import json
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash

from app import db

# Define a custom JSON type for SQLite
class JSONEncodedDict(db.TypeDecorator):
    """Represents a JSON structure as Text for SQLite"""
    impl = Text

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class User(db.Model):
    """User model for authentication and profile information"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(256), nullable=False)
    full_name = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Gamification fields
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_activity_date = Column(DateTime)
    total_points = Column(Integer, default=0)
    level = Column(Integer, default=1)

    # Relationships
    health_data = relationship("HealthData", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    insights = relationship("Insight", back_populates="user", cascade="all, delete-orphan")
    achievements = relationship("UserAchievement", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password):
        """Set password hash"""
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.hashed_password, password)

    def __repr__(self):
        return f"<User {self.username}>"


class HealthData(db.Model):
    """Health data model for storing user health metrics"""
    __tablename__ = "health_data"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    weight = Column(Float)  # in kg
    height = Column(Float)  # in cm
    steps = Column(Integer)
    sleep_hours = Column(Float)
    water_intake = Column(Float)  # in liters
    calories_consumed = Column(Integer)
    calories_burned = Column(Integer)
    heart_rate = Column(Integer)  # BPM
    blood_pressure_systolic = Column(Integer)
    blood_pressure_diastolic = Column(Integer)
    notes = Column(Text)

    # Relationships
    user = relationship("User", back_populates="health_data")
    nutrition_entries = relationship("NutritionEntry", back_populates="health_data", cascade="all, delete-orphan")
    activity_entries = relationship("ActivityEntry", back_populates="health_data", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<HealthData for user_id={self.user_id} on {self.date}>"


class NutritionEntry(db.Model):
    """Nutrition entry model for storing meal information"""
    __tablename__ = "nutrition_entries"

    id = Column(Integer, primary_key=True, index=True)
    health_data_id = Column(Integer, ForeignKey("health_data.id"), nullable=False)
    meal_type = Column(String(50))  # breakfast, lunch, dinner, snack
    food_name = Column(String(100))
    calories = Column(Integer)
    protein = Column(Float)  # in grams
    carbs = Column(Float)  # in grams
    fat = Column(Float)  # in grams
    time = Column(DateTime, default=datetime.utcnow)

    # Relationships
    health_data = relationship("HealthData", back_populates="nutrition_entries")

    def __repr__(self):
        return f"<NutritionEntry {self.food_name} for health_data_id={self.health_data_id}>"


class ActivityEntry(db.Model):
    """Activity entry model for storing exercise information"""
    __tablename__ = "activity_entries"

    id = Column(Integer, primary_key=True, index=True)
    health_data_id = Column(Integer, ForeignKey("health_data.id"), nullable=False)
    activity_type = Column(String(50))
    duration = Column(Integer)  # in minutes
    calories_burned = Column(Integer)
    time = Column(DateTime, default=datetime.utcnow)

    # Relationships
    health_data = relationship("HealthData", back_populates="activity_entries")

    def __repr__(self):
        return f"<ActivityEntry {self.activity_type} for health_data_id={self.health_data_id}>"


class Goal(db.Model):
    """Goal model for tracking user health objectives"""
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100))
    description = Column(Text)
    target_value = Column(Float)
    current_value = Column(Float)
    goal_type = Column(String(50))  # weight, steps, activity, nutrition
    start_date = Column(DateTime, default=datetime.utcnow)
    target_date = Column(DateTime)
    is_achieved = Column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="goals")

    def __repr__(self):
        return f"<Goal {self.name} for user_id={self.user_id}>"


class Insight(db.Model):
    """Insight model for storing AI-generated health insights"""
    __tablename__ = "insights"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    insight_text = Column(Text)
    category = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="insights")

    def __repr__(self):
        return f"<Insight for user_id={self.user_id} created at {self.created_at}>"


class Achievement(db.Model):
    """Achievement model for storing available badges and achievements"""
    __tablename__ = "achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    badge_image = Column(String(200))  # Path or URL to the badge image
    category = Column(String(50))  # Category of achievement (e.g., exercise, nutrition, etc.)
    points = Column(Integer, default=10)  # Points awarded for this achievement
    requirement_type = Column(String(50))  # What triggers this achievement (e.g., streak, total_steps, etc.)
    requirement_value = Column(Integer, default=1)  # Value needed to earn the achievement
    
    # Relationships
    user_achievements = relationship("UserAchievement", back_populates="achievement")
    
    def __repr__(self):
        return f"<Achievement {self.name}>"


class UserAchievement(db.Model):
    """User achievement model for storing earned badges"""
    __tablename__ = "user_achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    achievement_id = Column(Integer, ForeignKey("achievements.id"), nullable=False)
    earned_at = Column(DateTime, default=datetime.utcnow)
    displayed = Column(Boolean, default=False)  # Whether user has seen the achievement notification
    
    # Relationships
    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="user_achievements")
    
    def __repr__(self):
        return f"<UserAchievement {self.achievement_id} for user_id={self.user_id}>"


class Notification(db.Model):
    """Notification model for storing user alerts and reminders"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), default="general")  # general, streak, health, meal, etc.
    link = Column(String(255))  # Optional URL to direct user when clicking the notification
    created_at = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime)
    expires_at = Column(DateTime)  # When the notification should no longer be shown
    
    # Relationships
    user = relationship("User", backref="notifications")
    
    def __repr__(self):
        return f"<Notification {self.id} for user_id={self.user_id}>"


class MealPlan(db.Model):
    """Meal plan model for storing generated meal plans"""
    __tablename__ = "meal_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime)
    daily_calories = Column(Integer)
    is_active = Column(Boolean, default=True)
    preferences = Column(Text)  # JSON string of preferred foods/cuisines
    restrictions = Column(Text)  # JSON string of dietary restrictions or allergies
    plan_data = Column(JSONEncodedDict)  # Stores the full meal plan as JSON
    
    # Relationships
    user = relationship("User", backref="meal_plans")
    
    def __repr__(self):
        return f"<MealPlan {self.id} for user_id={self.user_id}>"


class GroceryList(db.Model):
    """Grocery list model for storing shopping lists based on meal plans"""
    __tablename__ = "grocery_lists"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    meal_plan_id = Column(Integer, ForeignKey("meal_plans.id"), nullable=True)
    name = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_completed = Column(Boolean, default=False)
    list_data = Column(JSONEncodedDict)  # Stores the categorized grocery items as JSON
    
    # Relationships
    user = relationship("User", backref="grocery_lists")
    meal_plan = relationship("MealPlan", backref="grocery_lists")
    
    def __repr__(self):
        return f"<GroceryList {self.id} for user_id={self.user_id}>"