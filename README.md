# 🌊 AI-Powered Flood Prediction System

> **An AI-powered web application that predicts flood risk using Machine Learning, historical rainfall data, and live weather information.**

![Python](https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-Web%20Framework-black?style=for-the-badge&logo=flask)
![Machine Learning](https://img.shields.io/badge/Machine-Learning-green?style=for-the-badge)
![SQLite](https://img.shields.io/badge/Database-SQLite-blue?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Completed-success?style=for-the-badge)

---

# 📖 Project Overview

The **AI-Powered Flood Prediction System** is a Flask-based web application that predicts flood risk using Machine Learning models, historical rainfall data, and live weather information.

The application allows users to:

- 🔐 Register and log in securely
- 🌍 Fetch live weather data
- 🌧️ Predict flood probability
- 📊 View flood prediction results
- 📜 Access prediction history
- 🤖 Compare multiple Machine Learning models
- 💾 Store prediction records in a SQLite database

The system follows the database architecture:

**Users → Weather_Data → Prediction_Result ← ML_Model**

---

# ✨ Features

- 🔐 Secure User Authentication
- 🌍 Live Weather Integration using Open-Meteo API
- 🌧️ AI-Based Flood Prediction
- 📊 Interactive Prediction Dashboard
- 📈 Flood Probability Estimation
- 📜 Prediction History
- 🤖 Multiple Machine Learning Models
- 💾 SQLite Database
- 🎨 Responsive User Interface

---

# 🛠️ Technology Stack

### Frontend
- HTML5
- CSS3
- JavaScript

### Backend
- Python
- Flask

### Machine Learning
- Scikit-Learn
- Random Forest
- Decision Tree
- K-Nearest Neighbors (KNN)
- XGBoost

### Database
- SQLite

---

# 📂 Project Structure

```text
AI-Powered-Flood-Prediction-System/
│
├── app.py
├── models.py
├── requirements.txt
├── README.md
│
├── ml/
│   ├── train_model.py
│   ├── best_model.pkl
│   ├── decision_tree.pkl
│   ├── knn.pkl
│   ├── xgboost.pkl
│   ├── model_meta.json
│   └── state_rainfall.json
│
├── static/
├── templates/
├── screenshots/
└── instance/
```

---

## 📸 Application Screenshots

### 🔐 Login Page

![Login](screenshots/login.png)

---

### 📝 Registration Page

![Registration](screenshots/register.png)

---

### 📊 Prediction Dashboard

![Dashboard](screenshots/dashboard.png)

---

### 🌊 Flood Prediction Result

![Flood Prediction](screenshots/flood_prediction.png)

---

### 📈 Prediction Result Summary

![Result](screenshots/result.png)

---

### 📜 Prediction History

![History](screenshots/history.png)

---

### 🗄️ Database - Users Table

![Users Table](screenshots/users_table.png)

---

### 🌦️ Database - Weather Data

![Weather Data](screenshots/weather_data.png)

---

# 🚀 Installation

### Clone the repository

```bash
git clone https://github.com/AP24110010419/AI-Powered-Flood-Prediction-System.git
```

### Navigate to the project folder

```bash
cd AI-Powered-Flood-Prediction-System
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the application

```bash
python app.py
```

Open your browser and visit:

```
http://127.0.0.1:5000
```

---

# 🌍 Live Weather Integration

The application uses the **Open-Meteo API** to retrieve live:

- 🌡️ Temperature
- 💧 Humidity
- ☁️ Cloud Cover

Users can enter any location (for example, **Kochi, Kerala**) to automatically fetch current weather information before running a flood prediction.

---

# 🤖 Machine Learning Models

The project evaluates multiple Machine Learning algorithms:

- Decision Tree
- Random Forest
- K-Nearest Neighbors (KNN)
- XGBoost

The best-performing model is automatically selected for live flood prediction.

---

# 📊 Dataset

This project uses:

- Flood Prediction Dataset
- Rainfall in India (1901–2015)

Prediction is based on:

- Annual Rainfall
- Monsoon Rainfall
- Temperature
- Humidity
- Cloud Cover

---

# 🗄️ Database

The application contains four primary tables:

- Users
- Weather_Data
- Prediction_Result
- ML_Model

These tables store user information, weather records, prediction history, and machine learning model details.

---

# 🔄 Workflow

```text
User Login/Register
        │
        ▼
Enter Location
        │
        ▼
Fetch Live Weather
        │
        ▼
Historical Rainfall Data
        │
        ▼
Feature Processing
        │
        ▼
Machine Learning Model
        │
        ▼
Flood Prediction
        │
        ▼
Save Prediction
        │
        ▼
Prediction History
```

---

# 🚀 Future Enhancements

- ☁️ Cloud Deployment
- 📱 Mobile Application
- 📍 Interactive Flood Risk Maps
- 📧 Email Notifications
- 📊 Advanced Analytics Dashboard
- 🌦️ Weather Forecast Integration

---

# 👨‍💻 Author

**Bhargav Parimi**

B.Tech – Computer Science Engineering

SRM University AP

📧 **bhargavparimi47@gmail.com**

🔗 **https://github.com/AP24110010419**

---

# ⭐ Support

If you found this project useful, please give it a ⭐ on GitHub.

---

<div align="center">

## 🌊 AI-Powered Flood Prediction System

**Built with ❤️ using Python, Flask, and Machine Learning**

</div>