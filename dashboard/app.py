import requests
import streamlit as st


st.set_page_config(
    page_title="Crypto Prediction Dashboard",
    page_icon="📈",
    layout="wide"
)


st.title("📈 Real-Time Crypto Prediction Dashboard")

st.subheader("BTC/USDT")

try:

    response = requests.get(
        "http://127.0.0.1:8000/prediction",
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Symbol",
            data["symbol"]
        )

    with col2:
        st.metric(
            "Prediction",
            data["prediction"]
        )

    with col3:
        st.metric(
            "Confidence",
            f"{data['confidence'] * 100:.2f}%"
        )

    st.write("Last processed timestamp:")
    st.write(data["timestamp"])

except Exception as e:

    st.error(
        "Could not connect to Prediction API."
    )

    st.write(str(e))