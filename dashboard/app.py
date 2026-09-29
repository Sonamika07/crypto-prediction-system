import time

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Crypto Prediction Dashboard",
    page_icon="📈",
    layout="wide"
)


# ==================================================
# CONFIGURATION
# ==================================================

API_URL = "https://crypto-prediction-system.onrender.com"
REFRESH_SECONDS = 60


# ==================================================
# HEADER
# ==================================================

st.title("📈 Real-Time Crypto Prediction Dashboard")

st.subheader("BTC / USDT")

st.caption(
    f"🔄 Dashboard automatically refreshes every "
    f"{REFRESH_SECONDS} seconds."
)


# ==================================================
# LATEST PREDICTION
# ==================================================

prediction = None

try:
    prediction_response = requests.get(
        f"{API_URL}/prediction",
        timeout=30
    )

    prediction_response.raise_for_status()
    prediction = prediction_response.json()

except Exception as error:
    st.error("Prediction API is not available.")
    st.write(str(error))


# ==================================================
# MARKET DATA
# ==================================================

market_df = pd.DataFrame()

try:
    market_response = requests.get(
        f"{API_URL}/market-data",
        params={"limit": 100},
        timeout=30
    )

    market_response.raise_for_status()

    market_data = market_response.json()

    market_df = pd.DataFrame(market_data)

except Exception as error:
    st.error("Unable to load market data.")
    st.write(str(error))


# ==================================================
# PREPARE MARKET DATA
# ==================================================

current_price = None

if not market_df.empty:

    market_df["timestamp"] = pd.to_datetime(
        market_df["timestamp"],
        format="mixed",
        utc=True
    )

    market_df["close_price"] = pd.to_numeric(
        market_df["close_price"],
        errors="coerce"
    )

    market_df = market_df.sort_values("timestamp")

    current_price = float(
        market_df["close_price"].iloc[-1]
    )


# ==================================================
# ALERT
# ==================================================

if prediction:

    if prediction.get("alert"):

        st.warning(
            f"🔔 ALERT: {prediction.get('alert_message', 'Market alert detected.')}"
        )

    else:

        st.info(
            f"ℹ️ {prediction.get('alert_message', 'No active alert.')}"
        )


# ==================================================
# KPI CARDS
# ==================================================

if prediction:

    card1, card2, card3, card4 = st.columns(4)

    # ----------------------------------------------
    # CURRENT PRICE
    # ----------------------------------------------

    with card1:

        if current_price is not None:

            st.metric(
                "💰 Current BTC Price",
                f"${current_price:,.2f}"
            )

        else:

            st.metric(
                "💰 Current BTC Price",
                "N/A"
            )

    # ----------------------------------------------
    # PREDICTION
    # ----------------------------------------------

    with card2:

        direction = prediction.get(
            "prediction",
            "N/A"
        )

        if direction == "UP":

            direction_display = "🟢 UP"

        elif direction == "DOWN":

            direction_display = "🔴 DOWN"

        else:

            direction_display = direction

        st.metric(
            "🤖 Prediction",
            direction_display
        )

    # ----------------------------------------------
    # CONFIDENCE
    # ----------------------------------------------

    with card3:

        try:

            confidence = float(
                prediction.get(
                    "confidence",
                    0
                )
            )

        except (TypeError, ValueError):

            confidence = 0

        confidence_percent = confidence * 100

        st.metric(
            "🎯 Confidence",
            f"{confidence_percent:.2f}%"
        )

    # ----------------------------------------------
    # ALERT STATUS
    # ----------------------------------------------

    with card4:

        alert_status = (
            "ACTIVE"
            if prediction.get("alert")
            else "NORMAL"
        )

        st.metric(
            "🔔 Alert Status",
            alert_status
        )


    # ==================================================
    # CONFIDENCE BAR
    # ==================================================

    st.write("### 🎯 Prediction Confidence")

    st.progress(
        min(max(confidence, 0), 1)
    )

    try:

        threshold = float(
            prediction.get(
                "threshold",
                0.60
            )
        )

    except (TypeError, ValueError):

        threshold = 0.60

    st.caption(
        f"Model confidence: "
        f"{confidence_percent:.2f}% | "
        f"Alert threshold: "
        f"{threshold * 100:.0f}%"
    )


# ==================================================
# MARKET PRICE CHART
# ==================================================

st.divider()

st.subheader("📊 BTC Price Chart")

if not market_df.empty:

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=market_df["timestamp"],
            y=market_df["close_price"],
            mode="lines",
            name="BTC Close Price"
        )
    )

    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="BTC Price (USDT)",
        hovermode="x unified",
        height=450
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

else:

    st.warning(
        "No market data available."
    )


# ==================================================
# MARKET DATA TABLE
# ==================================================

st.subheader("📋 Latest Market Data")

if not market_df.empty:

    display_columns = [
        "timestamp",
        "open_price",
        "high_price",
        "low_price",
        "close_price",
        "volume"
    ]

    available_columns = [
        column
        for column in display_columns
        if column in market_df.columns
    ]

    st.dataframe(
        market_df[available_columns]
        .sort_values(
            "timestamp",
            ascending=False
        )
        .head(20),
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        "Market data is currently unavailable."
    )


# ==================================================
# SYSTEM STATUS
# ==================================================

st.divider()

st.subheader("⚙️ System Status")

status1, status2, status3 = st.columns(3)


with status1:

    st.success(
        "🟢 Prediction API Connected"
    )


with status2:

    if prediction:

        st.success(
            "🟢 Prediction Data Available"
        )

    else:

        st.error(
            "🔴 Prediction Data Unavailable"
        )


with status3:

    if not market_df.empty:

        st.success(
            "🟢 Market Data Available"
        )

    else:

        st.error(
            "🔴 Market Data Unavailable"
        )


# ==================================================
# FOOTER
# ==================================================

st.divider()

st.caption(
    "⚠️ This dashboard provides model-based predictions "
    "and does not guarantee trading profits."
)

st.caption(
    "🔄 Dashboard will automatically refresh."
)


# ==================================================
# AUTO REFRESH
# ==================================================

time.sleep(
    REFRESH_SECONDS
)

st.rerun()