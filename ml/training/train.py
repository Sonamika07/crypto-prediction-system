import os

import joblib
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

from ml.preprocessing.feature_engineering import create_features


# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in .env")


# Database connection
engine = create_engine(DATABASE_URL)


# Load BTCUSDT market data
query = """
SELECT
    timestamp,
    open_price,
    high_price,
    low_price,
    close_price,
    volume
FROM market_data
WHERE symbol = 'BTCUSDT'
  AND volume > 0
ORDER BY timestamp ASC
"""

df = pd.read_sql(query, engine)

print("=" * 60)
print("BTCUSDT ML MODEL TRAINING")
print("=" * 60)

print(f"Raw rows loaded: {len(df)}")


# Feature engineering
df = create_features(df)

print(f"Rows after feature engineering: {len(df)}")


# Features used by the model
features = [
    "return_1h",
    "ma_5",
    "ma_10",
    "ema_10",
    "volatility_5",
    "volume_change",
    "momentum_5",
    "price_range",
    "rsi",
    "macd",
    "bb_upper",
    "bb_lower"
]


# Check missing features
missing_features = [
    feature
    for feature in features
    if feature not in df.columns
]

if missing_features:
    raise ValueError(
        f"Missing features: {missing_features}"
    )


# Remove invalid rows
df = df.dropna(
    subset=features + ["target"]
).reset_index(drop=True)

print(f"Usable rows: {len(df)}")


# Time-based train/test split
split_index = int(len(df) * 0.80)

train_df = df.iloc[:split_index].copy()
test_df = df.iloc[split_index:].copy()


print()
print("DATA SPLIT")
print("-" * 40)
print(f"Training rows: {len(train_df)}")
print(f"Testing rows: {len(test_df)}")


# Training data
X_train = train_df[features]
y_train = train_df["target"]


# Testing data
X_test = test_df[features]
y_test = test_df["target"]


# Random Forest model
model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced",
    n_jobs=-1
)


print()
print("Training Random Forest model...")

model.fit(
    X_train,
    y_train
)


# Predictions
predictions = model.predict(X_test)


# Accuracy
accuracy = accuracy_score(
    y_test,
    predictions
)


print()
print("MODEL RESULTS")
print("=" * 40)

print(
    f"Test accuracy: {accuracy:.4f}"
)

print(
    f"Test accuracy (%): {accuracy * 100:.2f}%"
)


# Classification report
print()
print("CLASSIFICATION REPORT")
print("=" * 40)

print(
    classification_report(
        y_test,
        predictions,
        zero_division=0
    )
)


# Confusion matrix
print()
print("CONFUSION MATRIX")
print("=" * 40)

print(
    confusion_matrix(
        y_test,
        predictions
    )
)


# Save model
model_directory = "ml/models"

os.makedirs(
    model_directory,
    exist_ok=True
)

model_path = os.path.join(
    model_directory,
    "btc_direction_model.joblib"
)

joblib.dump(
    model,
    model_path
)


print()
print("=" * 60)
print("MODEL TRAINING COMPLETED")
print("=" * 60)

print(
    f"Model saved at: {model_path}"
)