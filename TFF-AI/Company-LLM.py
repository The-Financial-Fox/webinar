import streamlit as st
import pandas as pd
import plotly.express as px
from groq import Groq
import os
from dotenv import load_dotenv
from statsmodels.tsa.arima.model import ARIMA

# Load API key securely from .env file
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("🚨 API Key is missing! Set it in Streamlit Secrets or a .env file.")
    st.stop()

# Dummy data for demonstration
revenue_data = pd.DataFrame({
    'Month': pd.date_range(start='2023-01-01', periods=6, freq='M'),
    'Revenue ($M)': [5.2, 5.5, 6.0, 5.8, 6.2, 6.5]
})

budget_data = pd.DataFrame({
    'Category': ['Marketing', 'Operations', 'R&D'],
    'Budget ($M)': [1.5, 2.0, 1.0],
    'Actual ($M)': [1.7, 1.9, 1.2]
})

# Streamlit app configuration
st.set_page_config(page_title="The Financial Fox FP&A Tool", layout="wide")

# Custom CSS for The Financial Fox branding (gold: #FFD700, navy blue: #1E3A8A)
st.markdown("""
    <style>
    .stApp {
        background-color: #1E3A8A;
        color: #FFFFFF;
    }
    .stButton>button {
        background-color: #FFD700;
        color: #1E3A8A;
    }
    .stTextInput>div>input {
        background-color: #FFFFFF;
        color: #1E3A8A;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Ask a Question", "Generate Graph", "Forecasting", "Budgeting"])

# Dashboard Page
if page == "Dashboard":
    st.title("📊 The Financial Fox FP&A Tool")
    st.write("Welcome to your AI-powered financial planning and analysis assistant!")
    st.image("https://via.placeholder.com/150x50.png?text=The+Financial+Fox+Logo", use_column_width=True)
    st.write("Use the sidebar to navigate to different features.")

# Ask a Question Page (Chat Interface)
elif page == "Ask a Question":
    st.header("💬 Ask a Financial Question")
    user_question = st.text_input("Type your question here:")
    if st.button("Get Answer"):
        with st.spinner("Thinking..."):
            client = Groq(api_key=GROQ_API_KEY)
            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an FP&A expert for The Financial Fox."},
                    {"role": "user", "content": user_question}
                ],
                model="llama3-8b-8192",
            )
            answer = response.choices[0].message.content
            st.write(answer)

# Generate Graph Page
elif page == "Generate Graph":
    st.header("📈 Generate a Graph")
    chart_type = st.selectbox("Select chart type", ["Line", "Bar", "Pie"])
    data_source = st.radio("Data source", ["Dummy Data", "Upload File"])

    if data_source == "Dummy Data":
        df = revenue_data
    else:
        uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
        else:
            st.warning("Please upload a file.")
            st.stop()

    if chart_type == "Line":
        fig = px.line(df, x='Month', y='Revenue ($M)', title='Revenue Over Time')
    elif chart_type == "Bar":
        fig = px.bar(df, x='Month', y='Revenue ($M)', title='Monthly Revenue')
    elif chart_type == "Pie":
        fig = px.pie(df, values='Revenue ($M)', names='Month', title='Revenue Distribution')

    st.plotly_chart(fig)

# Forecasting Page
elif page == "Forecasting":
    st.header("🔮 Forecasting")
    st.write("Generate a forecast based on historical revenue data.")

    # Simple ARIMA forecast
    model = ARIMA(revenue_data['Revenue ($M)'], order=(1,1,1))
    fitted_model = model.fit()
    forecast = fitted_model.forecast(steps=3)
    forecast_dates = pd.date_range(start=revenue_data['Month'].iloc[-1] + pd.DateOffset(months=1), periods=3, freq='M')
    forecast_df = pd.DataFrame({'Month': forecast_dates, 'Forecast ($M)': forecast})

    fig = px.line(revenue_data, x='Month', y='Revenue ($M)', title='Revenue Forecast')
    fig.add_scatter(x=forecast_df['Month'], y=forecast_df['Forecast ($M)'], mode='lines', name='Forecast')
    st.plotly_chart(fig)

# Budgeting Page
elif page == "Budgeting":
    st.header("💰 Budgeting")
    st.write("Manage your budgets and compare with actuals.")

    edited_df = st.data_editor(budget_data, num_rows="dynamic")
    if st.button("Save Budget"):
        st.success("Budget saved successfully!")

    # Calculate variance
    edited_df['Variance ($M)'] = edited_df['Budget ($M)'] - edited_df['Actual ($M)']
    st.write("Budget vs Actuals with Variance:")
    st.dataframe(edited_df)

# Placeholder for additional features in the sidebar
st.sidebar.markdown("---")
st.sidebar.write("Coming Soon: Scenario Analysis, Report Generation, and AI Insights")
