# 🌊 AI-Powered Flood Prediction System

An AI-powered Flood Prediction System built using **Flask**, **Python**, and **Machine Learning** to predict flood risk based on rainfall and environmental data. The application provides an intuitive web interface for users to analyze flood predictions using multiple trained machine learning models.

---

## 📌 Features

- 🔐 User Authentication (Login & Registration)
- 📊 Interactive Dashboard
- 🎨 Responsive and Modern User Interface
- 📈 Rainfall Data Analysis


---

## 🛠️ Tech Stack

### Frontend
- HTML5
- CSS3
- JavaScript

### Backend
- Python
- Flask

### Machine Learning
- Scikit-learn
- XGBoost
- Joblib

### Database
- SQLite

---

## 📂 Project Structure

```
floodapp/
  app.py                  Flask routes, prediction logic
  models.py               SQLAlchemy models (Users, MLModel, WeatherData, PredictionResult)
  ml/
    train_model.py         Retrains all 4 models from the raw dataset
    best_model.pkl          Active model used for live predictions
    decision_tree.pkl, knn.pkl, xgboost.pkl   The other 3 trained models
    model_meta.json          Accuracy metadata, seeds the ML_Model table
    state_rainfall.json      Historical per-state rainfall averages (1901–2015)
  templates/               Jinja templates
  static/css/style.css     Shared styling
  requirements.txt
```

## Run it locally

```bash
cd floodapp
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# create the database tables and seed the model registry
flask --app app init-db

# start the dev server
python app.py
```

Open **http://127.0.0.1:5000**, register an account, and run your first prediction.

## Live weather by location

On the Predict page, type a place name (e.g. "Kochi, Kerala") and click **Use current
weather** — this calls Open-Meteo's free geocoding + forecast APIs (no API key required)
to pull the current temperature, humidity, and cloud cover for that place and drops them
straight into the form. Combine it with the historical rainfall autofill (state dropdown)
for annual/monsoon rainfall, then run the prediction. Requires internet access from the
machine running the Flask app — it makes an outbound HTTPS request, not just localhost.

## About the model

- Trained on `flood_dataset.xlsx` (115 samples, 16 flood events) using five features that
  map directly onto the `Weather_Data` table: **Temperature, Humidity, Cloud Cover,
  Annual Rainfall, Monsoon (Jun–Sep) Rainfall**.
- All four algorithms were evaluated with 5-fold stratified cross-validation (more reliable
  than a single split on this small a dataset); the best one is refit on the full dataset
  and used for live predictions. Currently that's **Random Forest** (~99% CV accuracy,
  95.7% on the held-out test split) — rerun `ml/train_model.py` any time you add more data,
  and it will re-pick whichever model performs best.
- `CloudVisibility` in the ER diagram is populated from the dataset's cloud cover reading
  (higher cover → more rain risk), and `SeasonalRainfall` uses the Jun–Sep monsoon total,
  since that's India's primary flood season.

## Note on the dataset

115 rows with only 16 positive (flood) cases is a small, imbalanced sample. The reported
accuracy numbers are honest results from this run, not guaranteed to match any specific
number you may have seen elsewhere — as you gather more historical records, retrain with
`train_model.py` for more robust numbers.

## Next steps you might want

- Swap SQLite for Postgres/Db2 for an IBM Cloud deployment (`SQLALCHEMY_DATABASE_URI`).
- Add an admin view to retrain/upload new datasets from the browser.
- Add email alerts when a prediction crosses the "High" risk threshold.
