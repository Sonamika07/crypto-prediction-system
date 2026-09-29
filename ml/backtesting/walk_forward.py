import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

from ml.preprocessing.feature_engineering import create_features


# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in .env")


# Database connection
engine = create_engine(DATABASE_URL)


# Load BTCUSDT data
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
print("WALK-FORWARD VALIDATION")
print("=" * 60)

print(f"Raw rows loaded: {len(df)}")


# Feature engineering
df = create_features(df)

print(f"Rows after feature engineering: {len(df)}")


# Model features
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


# Check features
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


# Walk-forward configuration
initial_train_size = 2500
test_size = 500

results = []

start = initial_train_size
fold = 1


while start + test_size <= len(df):

    train_df = df.iloc[:start].copy()

    test_df = df.iloc[
        start:start + test_size
    ].copy()

    X_train = train_df[features]
    y_train = train_df["target"]

    X_test = test_df[features]
    y_test = test_df["target"]


    # Create model
    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1
    )


    print()
    print("=" * 60)
    print(f"FOLD {fold}")
    print("=" * 60)

    print(
        f"Training rows: {len(train_df)}"
    )

    print(
        f"Testing rows: {len(test_df)}"
    )

    print(
        f"Test period: "
        f"{test_df['timestamp'].iloc[0]} "
        f"to "
        f"{test_df['timestamp'].iloc[-1]}"
    )


    # Train
    model.fit(
        X_train,
        y_train
    )


    # Predict
    predictions = model.predict(
        X_test
    )


    # Accuracy
    accuracy = accuracy_score(
        y_test,
        predictions
    )


    print(
        f"Fold {fold} accuracy: "
        f"{accuracy * 100:.2f}%"
    )


    results.append(
        {
            "fold": fold,
            "train_rows": len(train_df),
            "test_rows": len(test_df),
            "accuracy": accuracy
        }
    )


    # Move forward
    start += test_size
    fold += 1


# Results
results_df = pd.DataFrame(results)


print()
print("=" * 60)
print("WALK-FORWARD RESULTS")
print("=" * 60)

print(
    results_df.to_string(
        index=False
    )
)


# Average accuracy
average_accuracy = results_df[
    "accuracy"
].mean()


print()
print("=" * 60)
print("FINAL WALK-FORWARD RESULT")
print("=" * 60)

print(
    f"Number of folds: {len(results_df)}"
)

print(
    f"Average accuracy: "
    f"{average_accuracy * 100:.2f}%"
)


# Best and lowest fold
best_accuracy = results_df[
    "accuracy"
].max()

lowest_accuracy = results_df[
    "accuracy"
].min()


print(
    f"Highest fold accuracy: "
    f"{best_accuracy * 100:.2f}%"
)

print(
    f"Lowest fold accuracy: "
    f"{lowest_accuracy * 100:.2f}%"
)