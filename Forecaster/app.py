import streamlit as st
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from prophet import Prophet
from dotenv import load_dotenv
from groq import Groq

# Load API key securely
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("🚨 API Key is missing! Set it in Streamlit Secrets or a .env file.")
    st.stop()

# Streamlit UI
st.set_page_config(page_title="AI Forecasting Agent", page_icon="📈", layout="wide")
st.title("📊 AI Forecasting with Prophet")

# File uploader
uploaded_file = st.file_uploader("Upload an Excel file with Date and Revenue columns", type=["xlsx", "xls"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("### Preview of Uploaded Data")
    st.dataframe(df.head())
    
    # Ensure proper column names
    if "Date" not in df.columns or "Revenue" not in df.columns:
        st.error("The file must contain 'Date' and 'Revenue' columns.")
        st.stop()
    
    # Prepare data for Prophet
    df = df.rename(columns={"Date": "ds", "Revenue": "y"})
    df["ds"] = pd.to_datetime(df["ds"])  # Ensure Date column is in datetime format
    
    # Fit Prophet model
    model = Prophet()
    model.fit(df)
    
    # Forecast future data
    future = model.make_future_dataframe(periods=30)  # Predict for next 30 days
    forecast = model.predict(future)
    
    # Display forecast
    st.write("### Forecasted Data")
    st.dataframe(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail())
    
    # Plot forecast
    fig, ax = plt.subplots(figsize=(10, 6))
    model.plot(forecast, ax=ax)
    st.pyplot(fig)
    
    # Generate AI Commentary
    st.subheader("🤖 AI-Generated Forecast Analysis")
    client = Groq(api_key=GROQ_API_KEY)
    prompt = f"""
    You are a Financial Analyst. Analyze the revenue forecast trends and provide:
    - Key insights from the forecast.
    - Potential risks and opportunities.
    - Strategic recommendations based on the trend.
    
    Here is the forecast data:
    {forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].to_json()}
    """
    
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are an expert in financial forecasting."},
            {"role": "user", "content": prompt}
        ],
        model="llama-3.3-70b-versatile",
    )
    
    ai_analysis = response.choices[0].message.content
    st.write(ai_analysis)
