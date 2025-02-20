import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
import os
from groq import Groq

# Load environment variables (for Groq API key)
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("🚨 Please set your Groq API key in a .env file as GROQ_API_KEY.")
    st.stop()

# Dummy data for demonstration
data = pd.DataFrame({
    ' Month ': pd.date_range(start='2023-01-01', periods=12, freq='M'),
    'Revenue ($M)': [5.2, 5.5, 6.0, 5.8, 6.2, 6.5, 6.8, 7.0, 7.2, 7.5, 7.8, 8.0],
    'Expenses ($M)': [1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6]
})

# Streamlit app configuration
st.set_page_config(page_title="The Financial Fox FP&A Tool", layout="wide")

# Custom CSS for branding (gold: #FFD700, navy blue: #1E3A8A)
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
page = st.sidebar.radio("Go to", ["Dashboard", "Ask a Question", "Generate Graph"])

# Dashboard Page
if page == "Dashboard":
    st.title("📊 The Financial Fox FP&A Tool")
    st.write("Your assistant for financial planning and analysis.")

    # Display KPIs
    total_revenue = data['Revenue ($M)'].sum()
    total_expenses = data['Expenses ($M)'].sum()
    profit = total_revenue - total_expenses
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Revenue", f"${total_revenue:.2f}M")
    col2.metric("Total Expenses", f"${total_expenses:.2f}M")
    col3.metric("Profit", f"${profit:.2f}M")

    # Default Revenue Line Chart
    fig = px.line(data, x=' Month ', y='Revenue ($M)', title='Revenue Over Time')
    fig.update_layout(template="plotly_white")
    st.plotly_chart(fig)

# Ask a Question Page
elif page == "Ask a Question":
    st.header("💬 Ask a Financial Question")
    st.write("Ask anything about your financial data, and get an AI-powered answer!")

    # Text input for user question
    user_question = st.text_input("Type your question here (e.g., 'What’s our revenue growth rate?')")
    if st.button("Get Answer"):
        if user_question:
            with st.spinner("Thinking..."):
                # Initialize Groq client
                client = Groq(api_key=GROQ_API_KEY)
                # Send question to Groq API
                response = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are a financial planning expert."},
                        {"role": "user", "content": user_question}
                    ],
                    model="llama3-8b-8192",  # Example model; adjust as needed
                )
                answer = response.choices[0].message.content
                st.write("**Answer:**")
                st.write(answer)
        else:
            st.warning("Please enter a question.")

# Generate Graph Page
elif page == "Generate Graph":
    st.header("📈 Generate a Graph")
    st.write("Create custom visualizations with advanced graph types.")

    # Data source selection
    data_source = st.radio("Data source", ["Dummy Data", "Upload CSV"])
    if data_source == "Dummy Data":
        df = data
    else:
        uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
        else:
            st.warning("Please upload a CSV file.")
            st.stop()

    # Graph type selection
    graph_type = st.selectbox("Select graph type", ["Line", "Bar", "Pie", "Scatter", "Area", "Heatmap"])

    # Graph generation logic
    if graph_type in ["Line", "Bar", "Scatter", "Area"]:
        x_col = st.selectbox("Select X-axis column", df.columns)
        y_col = st.selectbox("Select Y-axis column", [col for col in df.columns if col != x_col and pd.api.types.is_numeric_dtype(df[col])])

        if graph_type == "Line":
            fig = px.line(df, x=x_col, y=y_col, title=f'{y_col} over {x_col}')
        elif graph_type == "Bar":
            fig = px.bar(df, x=x_col, y=y_col, title=f'{y_col} by {x_col}')
        elif graph_type == "Scatter":
            fig = px.scatter(df, x=x_col, y=y_col, title=f'{y_col} vs {x_col}')
        elif graph_type == "Area":
            fig = px.area(df, x=x_col, y=y_col, title=f'{y_col} over {x_col}')

    elif graph_type == "Pie":
        pie_col = st.selectbox("Select column for pie chart", df.columns)
        if pd.api.types.is_numeric_dtype(df[pie_col]):
            values = df[pie_col].value_counts().values
            labels = df[pie_col].value_counts().index
        else:
            values = df[pie_col].value_counts().values
            labels = df[pie_col].value_counts().index
        fig = px.pie(values=values, names=labels, title=f'Distribution of {pie_col}')

    elif graph_type == "Heatmap":
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        if len(numeric_cols) < 2:
            st.error("Heatmap requires at least two numeric columns.")
            st.stop()
        corr_matrix = df[numeric_cols].corr()
        fig = px.imshow(corr_matrix, text_auto=True, title="Correlation Heatmap")

    # Display the graph
    fig.update_layout(template="plotly_white")
    st.plotly_chart(fig)
