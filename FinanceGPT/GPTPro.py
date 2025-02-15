import streamlit as st
import os
import pandas as pd
from groq import Groq
from dotenv import load_dotenv
import PyPDF2

# Load API key securely
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("🚨 API Key is missing! Set it in Streamlit Secrets or a .env file.")
    st.stop()

# **🎨 Streamlit UI Styling**
st.set_page_config(page_title="Finance GPT Pro by Christian Martinez", page_icon="💰", layout="wide")

st.markdown("""
    <style>
        .title { text-align: center; font-size: 36px; font-weight: bold; color: #004D99; }
        .subtitle { text-align: center; font-size: 20px; color: #007ACC; }
        .stButton>button { width: 100%; background-color: #004D99; color: white; font-size: 16px; font-weight: bold; }
        .chat-container { padding: 15px; border-radius: 10px; margin: 10px 0; background-color: #F0F8FF; }
        .chat-title { font-size: 20px; font-weight: bold; color: #004D99; }
        .chat-response { font-size: 16px; color: #002E4D; }
    </style>
""", unsafe_allow_html=True)

# **📢 Title & Description**
st.markdown('<h1 class="title">💰 Finance GPT Pro by Christian Martinez</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Your AI-powered financial assistant for all things finance, FP&A, and investing.</p>', unsafe_allow_html=True)

# **📂 PDF Upload**
st.subheader("📥 Upload PDF Documents (Optional)")
uploaded_file = st.file_uploader("Upload a financial report, earnings call transcript, or any finance-related document.", type=["pdf"])

pdf_text = ""

if uploaded_file:
    # Extract text from PDF
    with st.spinner("📖 Reading PDF..."):
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            pdf_text += page.extract_text()
    
    st.success("✅ PDF Uploaded & Processed Successfully!")

# **Model Selection Dropdown**
st.subheader("🤖 Select AI Model")
model_options = [
    "gemma2-9b-it",
    "llama-3.3-70b-versatile",
    "mixtral-8x7b-32768",
    "llama-3.1-8b-instant",
    "llama3-8b-8192"
]
selected_model = st.selectbox("Choose the model to process your query:", model_options)

# **Chat Input**
st.subheader("💬 Ask a Finance Question")
user_input = st.text_area("🔍 Type your finance-related question here...")

if st.button("🚀 Get Answer"):
    client = Groq(api_key=GROQ_API_KEY)

    prompt = f"""
    You are Finance GPT, an AI assistant specializing in financial topics, including:
    - Corporate Finance, FP&A, and Budgeting
    - Stock Market Analysis and Investment Strategies
    - Financial Modeling, DCF Valuation, and Forecasting
    - Python and AI Applications in Finance
    - Risk Management, Accounting, and Business Strategy

    Answer the user's question clearly, concisely, and professionally.

    User's Question:
    {user_input}

    { "Relevant Information from Uploaded PDF:\n" + pdf_text if pdf_text else ""}
    """

    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are an AI expert in finance and financial planning & analysis (FP&A)."},
            {"role": "user", "content": prompt}
        ],
        model=selected_model,
    )

    ai_response = response.choices[0].message.content

    # **Display AI Response**
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    st.subheader("💡 Finance GPT Answer")
    st.write(ai_response)
    st.markdown('</div>', unsafe_allow_html=True)
