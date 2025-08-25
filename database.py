"""
Database configuration for the Health Tracker application
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Initialize SQLAlchemy with a declarative base
class Base(DeclarativeBase):
    pass

# Create database instance
db = SQLAlchemy(model_class=Base)