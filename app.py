import os, json, pickle
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import (
    LoginManager, login_user, login_required, logout_user, current_user
)
import pandas as pd
import requests

from models import db, Users, MLModel, WeatherData, PredictionResult

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ML_DIR = os.path.join(BASE_DIR, "ml")

app = Flask(__name__, instance_relative_config=True)

os.makedirs(app.instance_path, exist_ok=True)

app.config["SECRET_KEY"] = "flood-watch-dev-secret-change-me"
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///" + os.path.join(app.instance_path, "floodwatch.db")
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


# ---------- load ML assets once at startup ----------
with open(os.path.join(ML_DIR, "best_model.pkl"), "rb") as f:
    _bundle = pickle.load(f)
ACTIVE_MODEL = _bundle["model"]
ACTIVE_FEATURES = _bundle["features"]  # ["Temp", "Humidity", "Cloud Cover", "ANNUAL", "Jun-Sep"]

with open(os.path.join(ML_DIR, "state_rainfall.json")) as f:
    STATE_RAINFALL = json.load(f)


def seed_models():
    """Populate ML_Model table from ml/model_meta.json if empty."""
    if MLModel.query.count() > 0:
        return
    with open(os.path.join(ML_DIR, "model_meta.json")) as f:
        meta = json.load(f)
    for m in meta:
        db.session.add(MLModel(
            ModelName=m["ModelName"],
            AlgorithmType=m["AlgorithmType"],
            Accuracy=m["Accuracy"],
            ModelFile=m["ModelFile"],
            IsActive=m["IsActive"],
        ))
    db.session.commit()


def get_active_model_row():
    return MLModel.query.filter_by(IsActive=True).first()


def classify(prob):
    if prob < 0.30:
        return "Low"
    elif prob < 0.55:
        return "Moderate"
    elif prob < 0.80:
        return "High"
    return "Severe"


# ---------------- Auth ----------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        role = request.form.get("role", "Meteorologist")
        password = request.form["password"]

        if Users.query.filter_by(Email=email).first():
            flash("An account with that email already exists.", "error")
            return redirect(url_for("register"))

        user = Users(Name=name, Email=email, Role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for("dashboard"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        user = Users.query.filter_by(Email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("dashboard"))
        flash("Incorrect email or password.", "error")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# ---------------- Core app ----------------

@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    result = None

    if request.method == "POST":
        region = request.form.get("region", "").strip()
        annual_rainfall = float(request.form["annual_rainfall"])
        cloud_visibility = float(request.form["cloud_visibility"])
        temperature = float(request.form["temperature"])
        humidity = float(request.form["humidity"])
        seasonal_rainfall = float(request.form["seasonal_rainfall"])

        reading = WeatherData(
            UserID=current_user.UserID,
            Region=region or None,
            AnnualRainfall=annual_rainfall,
            CloudVisibility=cloud_visibility,
            Temperature=temperature,
            Humidity=humidity,
            SeasonalRainfall=seasonal_rainfall,
        )
        db.session.add(reading)
        db.session.commit()

        # feature order must match training: Temp, Humidity, Cloud Cover, ANNUAL, Jun-Sep
        row = pd.DataFrame([{
            "Temp": temperature,
            "Humidity": humidity,
            "Cloud Cover": cloud_visibility,
            "ANNUAL": annual_rainfall,
            "Jun-Sep": seasonal_rainfall,
        }])[ACTIVE_FEATURES]

        proba = ACTIVE_MODEL.predict_proba(row)[0][1]
        flood_result = "Flood" if proba >= 0.5 else "No Flood"
        level = classify(proba)

        active_model_row = get_active_model_row()
        prediction = PredictionResult(
            DataID=reading.DataID,
            ModelID=active_model_row.ModelID,
            FloodResult=flood_result,
            FloodProbability=round(float(proba) * 100, 2),
            PredictionDate=datetime.utcnow(),
        )
        db.session.add(prediction)
        db.session.commit()

        result = {
            "region": region or "Unnamed district",
            "probability": prediction.FloodProbability,
            "level": level,
            "flood_result": flood_result,
            "model_name": active_model_row.ModelName,
        }

    recent = (
        db.session.query(WeatherData, PredictionResult)
        .join(PredictionResult, PredictionResult.DataID == WeatherData.DataID)
        .filter(WeatherData.UserID == current_user.UserID)
        .order_by(PredictionResult.PredictionDate.desc())
        .limit(8)
        .all()
    )

    return render_template(
        "dashboard.html",
        result=result,
        recent=recent,
        states=sorted(STATE_RAINFALL.keys()),
    )


@app.route("/api/state-rainfall/<state>")
@login_required
def state_rainfall(state):
    data = STATE_RAINFALL.get(state.upper())
    if not data:
        return jsonify({"error": "not found"}), 404
    return jsonify(data)


@app.route("/api/live-weather")
@login_required
def live_weather():
    """Fetch current temperature, humidity, cloud cover and rain probability for a
    place name using Open-Meteo's free geocoding + forecast APIs (no API key needed)."""
    location = request.args.get("location", "").strip()
    if not location:
        return jsonify({"error": "location is required"}), 400

    # Try the full string first, then progressively simpler variants
    # (geocoding often fails on "City, State" but succeeds on "City").
    candidates = [location]
    if "," in location:
        parts = [p.strip() for p in location.split(",") if p.strip()]
        if parts and parts[0] not in candidates:
            candidates.append(parts[0])

    try:
        place = None
        for candidate in candidates:
            geo = requests.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={"name": candidate, "count": 1, "language": "en", "format": "json"},
                timeout=8,
            ).json()
            results = geo.get("results")
            if results:
                place = results[0]
                break

        if not place:
            return jsonify({"error": f"couldn't find a place named '{location}' — try just the city name"}), 404

        lat, lon = place["latitude"], place["longitude"]
        resolved_name = ", ".join(
            filter(None, [place.get("name"), place.get("admin1"), place.get("country")])
        )

        weather = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,cloud_cover,precipitation",
                "hourly": "precipitation_probability",
                "forecast_days": 1,
            },
            timeout=8,
        ).json()
        current = weather.get("current")
        if not current:
            return jsonify({"error": "weather service returned no current data"}), 502

        # match the current hour to its precipitation probability from the hourly series
        rain_probability = None
        hourly = weather.get("hourly", {})
        times = hourly.get("time", [])
        probs = hourly.get("precipitation_probability", [])
        current_time = current.get("time")
        if current_time and times:
            current_hour = current_time[:13]  # "YYYY-MM-DDTHH"
            for t, p in zip(times, probs):
                if t[:13] == current_hour:
                    rain_probability = p
                    break
        if rain_probability is None and probs:
            rain_probability = probs[0]

        return jsonify({
            "resolved_name": resolved_name,
            "latitude": lat,
            "longitude": lon,
            "temperature": current["temperature_2m"],
            "humidity": current["relative_humidity_2m"],
            "cloud_cover": current["cloud_cover"],
            "current_precipitation_mm": current.get("precipitation"),
            "rain_probability": rain_probability,
            "observed_at": current.get("time"),
        })
    except requests.RequestException:
        return jsonify({"error": "couldn't reach the weather service — check your internet connection"}), 502


@app.route("/history")
@login_required
def history():
    rows = (
        db.session.query(WeatherData, PredictionResult, MLModel)
        .join(PredictionResult, PredictionResult.DataID == WeatherData.DataID)
        .join(MLModel, MLModel.ModelID == PredictionResult.ModelID)
        .filter(WeatherData.UserID == current_user.UserID)
        .order_by(PredictionResult.PredictionDate.desc())
        .all()
    )
    return render_template("history.html", rows=rows)


@app.route("/models")
@login_required
def models_page():
    all_models = MLModel.query.order_by(MLModel.Accuracy.desc()).all()
    return render_template("models.html", models=all_models)


@app.cli.command("init-db")
def init_db():
    db.create_all()
    seed_models()
    print("Database initialised and models seeded.")


with app.app_context():
    db.create_all()
    seed_models()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)