# 📈 Real-Time Crypto Market Prediction & Alert System

A real-time cryptocurrency market prediction and alert system built with **Python, Machine Learning, PostgreSQL, FastAPI, and Streamlit**.

The system collects BTCUSDT market data, performs feature engineering, predicts the next hourly price direction using a **Random Forest classifier**, stores predictions in PostgreSQL, exposes them through FastAPI, and visualizes the results through an interactive Streamlit dashboard.

> ⚠️ **Disclaimer:** This project is for educational and research purposes. Model predictions are probabilistic and do not guarantee future market movements, trading profits, or financial returns.

---

## 🚀 Project Overview

The system is designed to demonstrate an end-to-end machine learning pipeline for cryptocurrency market direction prediction.

### Workflow

```text
Binance Market Data
        ↓
Python Data Collector
        ↓
PostgreSQL Database
        ↓
Feature Engineering
        ↓
Random Forest Classifier
        ↓
UP / DOWN Prediction
        ↓
FastAPI
        ↓
Streamlit Dashboard
        ↓
Confidence-Based Alerts

✨ Key Features
📊 BTCUSDT historical market data collection
🔄 Automatic closed-candle data collection
🗄️ PostgreSQL data storage
🧮 Technical feature engineering
🤖 Random Forest classification model
🟢 UP / 🔴 DOWN direction prediction
🎯 Prediction confidence score
🔔 Confidence-based alert system
🔌 FastAPI REST API
📈 Interactive Streamlit dashboard
📊 Price history visualization
🔮 Prediction history
📉 Confidence history
🧪 Historical backtesting
🔄 Walk-forward validation
🩺 API health monitoring
📚 Swagger API documentation
🛠️ Tech Stack
Programming Language
Python
Data & Machine Learning
Pandas
NumPy
Scikit-learn
Joblib
Database
PostgreSQL
SQLAlchemy
Psycopg2
Backend
FastAPI
Uvicorn
Dashboard
Streamlit
Plotly
Data Source
Binance REST API
Development Tools
Visual Studio Code
Git
GitHub
Python Virtual Environment
🧠 Machine Learning

The project uses a Random Forest Classifier to predict whether the next hourly BTCUSDT closing price will move:

UP
or
DOWN
Target Definition

The target is created using the next closing price:

Target = 1 → Next close > Current close
Target = 0 → Next close <= Current close
📊 Features Used

The model currently uses the following features:

Feature	Description
return_1h	One-hour percentage return
ma_5	5-period moving average
ma_10	10-period moving average
ema_10	10-period exponential moving average
volatility_5	5-period return volatility
volume_change	Change in trading volume
momentum_5	5-period price momentum
price_range	High-low price range
rsi	Relative Strength Index
macd	Moving Average Convergence Divergence
bb_upper	Upper Bollinger Band
bb_lower	Lower Bollinger Band
🧪 Model Validation

The current model has been evaluated using historical BTCUSDT data.

Current Validation Results
Metric	Result
Test Accuracy	51.05%
Walk-Forward Average	52.50%
Highest Walk-Forward Fold	56.20%
Lowest Walk-Forward Fold	50.00%
Walk-Forward Folds	4

These are historical validation results for the current dataset and model configuration.

They should not be interpreted as guaranteed future prediction accuracy or trading performance.

🔄 Walk-Forward Validation

Walk-forward validation is used to evaluate the model across multiple chronological test periods.

The model is trained on historical observations and evaluated on later observations without randomly shuffling the time series.

This helps provide a more realistic evaluation for time-dependent market data.

🗄️ Database

The project uses PostgreSQL with two primary tables.

market_data

Stores cryptocurrency market information:

ID
Symbol
Timestamp
Open price
High price
Low price
Close price
Volume
Created timestamp
predictions

Stores model predictions:

ID
Symbol
Timestamp
Prediction
Confidence
Created timestamp
🔌 FastAPI Endpoints

The backend provides the following API endpoints:

Endpoint	Purpose
GET /	API status
GET /health	Health check
GET /prediction	Latest prediction
GET /market-data	Market data
GET /prediction-history	Prediction history
GET /model-metrics	Model validation metrics
Swagger Documentation

When running locally:

http://127.0.0.1:8000/docs
📈 Streamlit Dashboard

The dashboard provides:

Current BTCUSDT price
Latest UP/DOWN prediction
Prediction confidence
Confidence threshold
Alert status
BTCUSDT price chart
Prediction history
Confidence history
Model performance
System status

Run the dashboard with:

streamlit run dashboard/app.py
🔔 Alert System

The system currently uses a 60% confidence threshold.

Confidence >= 60%
        ↓
High-confidence alert

Example:

Prediction: DOWN
Confidence: 62.50%
Alert: ACTIVE

The alert indicates model confidence according to the configured threshold. It does not indicate guaranteed market movement.

🔄 Automatic Data Collector

The automatic collector checks Binance every few minutes for the latest closed hourly BTCUSDT candle.

It avoids inserting duplicate candles using the database uniqueness constraint.

When a new candle is stored, the system generates a new prediction.

Run it with:

python backend/app/services/data_collector.py
📂 Project Structure
crypto-prediction-system/
│
├── backend/
│   └── app/
│       ├── models/
│       │   ├── market_data.py
│       │   └── prediction.py
│       │
│       ├── services/
│       │   ├── market_data_service.py
│       │   ├── historical_data_service.py
│       │   ├── prediction_service.py
│       │   └── data_collector.py
│       │
│       ├── main.py
│       ├── database.py
│       ├── init_db.py
│       └── load_historical_data.py
│
├── dashboard/
│   └── app.py
│
├── data/
│   ├── raw/
│   └── processed/
│
├── ml/
│   ├── models/
│   ├── preprocessing/
│   │   └── feature_engineering.py
│   │
│   ├── training/
│   │   └── train.py
│   │
│   └── backtesting/
│       ├── backtest.py
│       └── walk_forward.py
│
├── database/
│
├── tests/
│
├── .env
├── .gitignore
├── README.md
└── requirements.txt
⚙️ Installation
1. Clone the repository
git clone https://github.com/Sonamika07/crypto-prediction-system.git
cd crypto-prediction-system
2. Create a virtual environment

Windows:

python -m venv venv
3. Activate the virtual environment
venv\Scripts\Activate.ps1
4. Install dependencies
pip install -r requirements.txt
🔐 Environment Variables

Create a .env file in the project root:

DATABASE_URL=postgresql://username:password@localhost:5432/crypto_prediction

Replace the username and password with your local PostgreSQL credentials.

.env is excluded from Git using .gitignore. Never commit database passwords, API keys, or other secrets.

🗄️ Initialize Database

Run:

python backend/app/init_db.py

This creates the required PostgreSQL tables.

📥 Load Historical Data

Run:

python backend/app/load_historical_data.py

The current project uses BTCUSDT hourly historical market data.

🤖 Train the Model

Run:

python ml/training/train.py

The trained model is saved locally as:

ml/models/btc_direction_model.joblib

The model directory is excluded from Git in the current project configuration.

🧪 Run Backtesting

Run:

python ml/backtesting/backtest.py
🔄 Run Walk-Forward Validation

Run:

python ml/backtesting/walk_forward.py
🚀 Run FastAPI

Start the backend:

uvicorn backend.app.main:app --reload

API:

http://127.0.0.1:8000

Swagger:

http://127.0.0.1:8000/docs
📊 Run Streamlit

Open another terminal and run:

streamlit run dashboard/app.py

Dashboard:

http://localhost:8501
🔄 Run Automatic Collector

In another terminal:

python backend/app/services/data_collector.py

The collector checks for newly closed hourly candles and generates predictions when new market data is stored.

🔒 Security

The following files and directories are intentionally excluded from Git:

.env
venv/
__pycache__/
*.pyc
data/raw/*
data/processed/*
ml/models/*

This helps prevent sensitive credentials, virtual environments, generated datasets, and trained model artifacts from being committed accidentally.

⚠️ Disclaimer

This project is an educational machine-learning application for cryptocurrency market analysis.

It does not provide financial advice.

Predictions are based on historical market data and technical features. Cryptocurrency markets are highly volatile, and historical model performance does not guarantee future results.

Do not use the predictions as the sole basis for financial or trading decisions.

👩‍💻 Author

Sonamika Anand Samrat

B.Tech Computer Science Engineering

Interests:
Data Analytics
Machine Learning
Artificial Intelligence
Python


GitHub: https://github.com/Sonamika07

Project Repository: https://github.com/Sonamika07/crypto-prediction-system