from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Users(db.Model, UserMixin):
    __tablename__ = "users"
    UserID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(120), nullable=False)
    Email = db.Column(db.String(120), unique=True, nullable=False)
    Password = db.Column(db.String(255), nullable=False)
    Role = db.Column(db.String(40), nullable=False, default="Meteorologist")

    weather_readings = db.relationship("WeatherData", backref="user", lazy=True)

    def get_id(self):
        return str(self.UserID)

    def set_password(self, raw_password):
        self.Password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.Password, raw_password)


class MLModel(db.Model):
    __tablename__ = "ml_model"
    ModelID = db.Column(db.Integer, primary_key=True)
    ModelName = db.Column(db.String(120), nullable=False)
    AlgorithmType = db.Column(db.String(60), nullable=False)
    Accuracy = db.Column(db.Float, nullable=False)
    ModelFile = db.Column(db.String(120), nullable=False)
    IsActive = db.Column(db.Boolean, default=False)

    predictions = db.relationship("PredictionResult", backref="model", lazy=True)


class WeatherData(db.Model):
    __tablename__ = "weather_data"
    DataID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey("users.UserID"), nullable=False)
    Region = db.Column(db.String(120))
    AnnualRainfall = db.Column(db.Float, nullable=False)
    CloudVisibility = db.Column(db.Float, nullable=False)
    Temperature = db.Column(db.Float, nullable=False)
    Humidity = db.Column(db.Float, nullable=False)
    SeasonalRainfall = db.Column(db.Float, nullable=False)
    RecordedAt = db.Column(db.DateTime, default=datetime.utcnow)

    predictions = db.relationship("PredictionResult", backref="reading", lazy=True)


class PredictionResult(db.Model):
    __tablename__ = "prediction_result"
    PredictionID = db.Column(db.Integer, primary_key=True)
    DataID = db.Column(db.Integer, db.ForeignKey("weather_data.DataID"), nullable=False)
    ModelID = db.Column(db.Integer, db.ForeignKey("ml_model.ModelID"), nullable=False)
    FloodResult = db.Column(db.String(20), nullable=False)
    FloodProbability = db.Column(db.Float, nullable=False)
    PredictionDate = db.Column(db.DateTime, default=datetime.utcnow)