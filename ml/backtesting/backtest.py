import os

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


# --------------------------------------------------
# LOAD ENVIRONMENT
# --------------------------------------------------

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)


# --------------------------------------------------
# LOAD MARKET DATA
# --------------------------------------------------

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

print("Rows loaded:", len(df))


# --------------------------------------------------
# FEATURE ENGINEERING
# --------------------------------------------------

df = create_features(df)

print(
    "Rows after feature engineering:",
    len(df)
)


# --------------------------------------------------
# FEATURES
# --------------------------------------------------

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


# --------------------------------------------------
# CHECK FEATURES
# --------------------------------------------------

missing_features = [
    feature
    for feature in features
    if feature not in df.columns
]

if missing_features:

    raise ValueError(
        f"Missing features: {missing_features}"
    )


# --------------------------------------------------
# REMOVE INVALID VALUES
# --------------------------------------------------

df = df.dropna(
    subset=features + ["target"]
).reset_index(drop=True)


# --------------------------------------------------
# TIME-SERIES SPLIT
# --------------------------------------------------

split_index = int(
    len(df) * 0.80
)

train_df = df.iloc[
    :split_index
].copy()

test_df = df.iloc[
    split_index:
].copy()


print("\nDATA SPLIT")
print("------------------------")
print("Training rows:", len(train_df))
print("Testing rows:", len(test_df))


# --------------------------------------------------
# TRAIN MODEL ONLY ON PAST DATA
# --------------------------------------------------

X_train = train_df[features]

y_train = train_df["target"]


X_test = test_df[features]

y_test = test_df["target"]


model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    class_weight="balanced"
)


model.fit(
    X_train,
    y_train
)


# --------------------------------------------------
# FUTURE / UNSEEN DATA PREDICTION
# --------------------------------------------------

predictions = model.predict(
    X_test
)


# --------------------------------------------------
# ACCURACY
# --------------------------------------------------

accuracy = accuracy_score(
    y_test,
    predictions
)


# --------------------------------------------------
# RESULTS
# --------------------------------------------------

print("\nBACKTEST RESULTS")
print("========================")

print(
    "Test rows:",
    len(test_df)
)

print(
    "Correct predictions:",
    int(
        (predictions == y_test).sum()
    )
)

print(
    "Incorrect predictions:",
    int(
        (predictions != y_test).sum()
    )
)

print(
    "Backtest accuracy:",
    round(
        accuracy,
        4
    )
)

print(
    "Backtest accuracy (%):",
    round(
        accuracy * 100,
        2
    ),
    "%"
)


# --------------------------------------------------
# CLASSIFICATION REPORT
# --------------------------------------------------

print("\nCLASSIFICATION REPORT")
print("========================")

print(
    classification_report(
        y_test,
        predictions,
        zero_division=0
    )
)


# --------------------------------------------------
# CONFUSION MATRIX
# --------------------------------------------------

print("\nCONFUSION MATRIX")
print("========================")

print(
    confusion_matrix(
        y_test,
        predictions
    )
)