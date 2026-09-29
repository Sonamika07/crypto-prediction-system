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

API_URL = "http://127.0.0.1:8000"
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
        timeout=10
    )

    prediction_response.raise_for_status()

    prediction = prediction_response.json()

except Exception as error:

    st.error(
        "Prediction API is not available."
    )

    st.write(str(error))


# ==================================================
# MARKET DATA
# ==================================================

market_df = pd.DataFrame()

try:

    market_response = requests.get(
        f"{API_URL}/market-data",
        params={"limit": 100},
        timeout=10
    )

    market_response.raise_for_status()

    market_data = market_response.json()

    market_df = pd.DataFrame(
        market_data
    )

except Exception as error:

    st.error(
        "Unable to load market data."
    )

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
        market_df["close_price"]
    )

    current_price = float(
        market_df["close_price"].iloc[-1]
    )


# ==================================================
# ALERT
# ==================================================

if prediction:

    if prediction.get("alert"):

        st.warning(
            f"🔔 ALERT: {prediction['alert_message']}"
        )

    else:

        st.info(
            f"ℹ️ {prediction['alert_message']}"
        )


# ==================================================
# KPI CARDS
# ==================================================

if prediction:

    card1, card2, card3, card4 = st.columns(4)


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


    with card2:

        direction = prediction["prediction"]

        direction_display = (
            "🟢 UP"
            if direction == "UP"
            else "🔴 DOWN"
        )

        st.metric(
            "🤖 Prediction",
            direction_display
        )


    with card3:

        confidence = float(
            prediction["confidence"]
        )

        confidence_percent = (
            confidence * 100
        )

        st.metric(
            "🎯 Confidence",
            f"{confidence_percent:.2f}%"
        )


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


    # ----------------------------------------------
    # CONFIDENCE BAR
    # ----------------------------------------------

    st.write("### 🎯 Prediction Confidence")

    st.progress(
        min(confidence, 1.0)
    )

    threshold = float(
        prediction.get(
            "threshold",
            0.60
        )
    )

    st.caption(
        f"Model confidence: "
        f"{confidence_percent:.2f}% | "
        f"Alert threshold: "
        f"{threshold * 100:.0f}%"
    )

    st.caption(
        f"🕐 Last processed: "
        f"{prediction['timestamp']}"
    )


st.divider()


# ==================================================
# BTC PRICE HISTORY
# ==================================================

st.subheader("📊 BTCUSDT Price History")


if not market_df.empty:

    price_fig = go.Figure()


    price_fig.add_trace(
        go.Scatter(
            x=market_df["timestamp"],
            y=market_df["close_price"],
            mode="lines",
            name="BTCUSDT Price"
        )
    )


    price_fig.update_layout(
        title="BTCUSDT Closing Price",
        xaxis_title="Time",
        yaxis_title="Price (USDT)",
        height=500,
        hovermode="x unified"
    )


    st.plotly_chart(
        price_fig,
        use_container_width=True
    )

else:

    st.warning(
        "No market data available."
    )


st.divider()


# ==================================================
# PREDICTION HISTORY
# ==================================================

st.subheader("🔮 Prediction History")


try:

    history_response = requests.get(
        f"{API_URL}/prediction-history",
        params={"limit": 50},
        timeout=10
    )

    history_response.raise_for_status()

    history_data = history_response.json()

    history_df = pd.DataFrame(
        history_data
    )


    if not history_df.empty:

        history_df["timestamp"] = pd.to_datetime(
            history_df["timestamp"],
            format="mixed",
            utc=True
        )

        history_df["confidence"] = pd.to_numeric(
            history_df["confidence"]
        )

        history_df["confidence_percent"] = (
            history_df["confidence"] * 100
        ).round(2)


        # Direction

        history_df["direction"] = (
            history_df["prediction"]
            .map(
                {
                    "UP": "🟢 UP",
                    "DOWN": "🔴 DOWN"
                }
            )
        )


        # Signal

        history_df["signal"] = history_df[
            "confidence"
        ].apply(
            lambda value:
                "🔔 ALERT"
                if value >= threshold
                else "Normal"
        )


        display_df = history_df[
            [
                "timestamp",
                "symbol",
                "direction",
                "confidence_percent",
                "signal"
            ]
        ].copy()


        display_df.columns = [
            "Time",
            "Symbol",
            "Direction",
            "Confidence (%)",
            "Signal"
        ]


        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )


        # ------------------------------------------
        # CONFIDENCE CHART
        # ------------------------------------------

        st.subheader(
            "📈 Prediction Confidence History"
        )


        chart_df = history_df.sort_values(
            "timestamp"
        )


        confidence_fig = go.Figure()


        confidence_fig.add_trace(
            go.Scatter(
                x=chart_df["timestamp"],
                y=chart_df["confidence_percent"],
                mode="lines+markers",
                name="Confidence"
            )
        )


        confidence_fig.add_hline(
            y=threshold * 100,
            line_dash="dash",
            annotation_text=(
                f"Alert Threshold: "
                f"{threshold * 100:.0f}%"
            )
        )


        confidence_fig.update_layout(
            title="Prediction Confidence Over Time",
            xaxis_title="Time",
            yaxis_title="Confidence (%)",
            height=400,
            hovermode="x unified"
        )


        st.plotly_chart(
            confidence_fig,
            use_container_width=True
        )


    else:

        st.info(
            "No prediction history available yet."
        )


except Exception as error:

    st.error(
        "Unable to load prediction history."
    )

    st.write(str(error))


st.divider()


# ==================================================
# MODEL PERFORMANCE
# ==================================================

st.subheader("🧠 Model Performance")


try:

    metrics_response = requests.get(
        f"{API_URL}/model-metrics",
        timeout=10
    )

    metrics_response.raise_for_status()

    metrics = metrics_response.json()


    metric1, metric2, metric3, metric4 = st.columns(4)


    # ----------------------------------------------
    # TEST ACCURACY
    # ----------------------------------------------

    with metric1:

        st.metric(
            "Test Accuracy",
            f"{metrics['test_accuracy_percent']:.2f}%"
        )


    # ----------------------------------------------
    # WALK-FORWARD AVERAGE
    # ----------------------------------------------

    with metric2:

        st.metric(
            "Walk-Forward Avg.",
            f"{metrics['walk_forward_average_percent']:.2f}%"
        )


    # ----------------------------------------------
    # HIGHEST FOLD
    # ----------------------------------------------

    with metric3:

        st.metric(
            "Highest Fold",
            f"{metrics['highest_walk_forward_fold_percent']:.2f}%"
        )


    # ----------------------------------------------
    # LOWEST FOLD
    # ----------------------------------------------

    with metric4:

        st.metric(
            "Lowest Fold",
            f"{metrics['lowest_walk_forward_fold_percent']:.2f}%"
        )


    st.write(
        f"**Model:** {metrics['model']}"
    )

    st.write(
        f"**Validation folds:** "
        f"{metrics['walk_forward_folds']}"
    )

    st.info(
        f"ℹ️ {metrics['note']}"
    )


except Exception as error:

    st.error(
        "Unable to load model performance metrics."
    )

    st.write(str(error))


st.divider()


# ==================================================
# SYSTEM STATUS
# ==================================================

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
# AUTO REFRESH
# ==================================================

st.divider()

st.caption(
    "🔄 Dashboard will refresh automatically."
)


time.sleep(
    REFRESH_SECONDS
)

st.rerun()