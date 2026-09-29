import os

import joblib
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

from ml.preprocessing.feature_engineering import create_features


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

query = """
SELECT
    symbol,
    timestamp,
    open_price,
    high_price,
    low_price,
    close_price,
    volume
FROM market_data
WHERE symbol = 'BTCUSDT'
ORDER BY timestamp ASC
"""

df = pd.read_sql(query, engine)

print("Rows loaded:", len(df))

df = create_features(df)

print("Rows after feature engineering:", len(df))

features = [
    "return_1h",
    "ma_5",
    "ma_10",
    "volatility_5",
    "volume_change"
]

X = df[features]
y = df["target"]

split_index = int(len(df) * 0.8)

X_train = X.iloc[:split_index]
X_test = X.iloc[split_index:]

y_train = y.iloc[:split_index]
y_test = y.iloc[split_index:]

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)

predictions = model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)

print("\nMODEL RESULTS")
print("Accuracy:", accuracy)

print("\nClassification Report:")
print(
    classification_report(
        y_test,
        predictions,
        zero_division=0
    )
)

os.makedirs("ml/models", exist_ok=True)

model_path = "ml/models/btc_direction_model.joblib"

joblib.dump(model, model_path)

print("\nMODEL SAVED SUCCESSFULLY")
print("Path:", model_path)