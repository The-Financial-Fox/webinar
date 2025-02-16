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
st.set_page_config(page_title="Finance GPT", page_icon="💰", layout="wide")

st.markdown("""
    <style>
        .title { text-align: center; font-size: 36px; font-weight: bold; color: #004D99; }
        .subtitle { text-align: center; font-size: 20px; color: #007ACC; }
        .stButton>button { width: 100%; background-color: #004D99; color: white; font-size: 16px; font-weight: bold; }
        .chat-container { padding: 15px; border-radius: 10px; margin: 10px 0; background-color: #F0F8FF; }
    </style>
""", unsafe_allow_html=True)

# **📢 Title & Description**
st.markdown('<h1 class="title">💰 Finance GPT</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Your AI-powered financial assistant for all things finance, FP&A, and investing.</p>', unsafe_allow_html=True)

# **📂 File Uploads (PDF & Excel)**
st.subheader("📥 Upload Financial Documents (PDF or Excel)")
uploaded_files = st.file_uploader("Upload PDF or Excel documents for analysis.", type=["pdf", "xlsx"], accept_multiple_files=True)

combined_text = ""
excel_sheets = {}

for uploaded_file in uploaded_files:
    if uploaded_file.type == "application/pdf":
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            combined_text += page.extract_text() or ""
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        excel_data = pd.ExcelFile(uploaded_file)
        for sheet_name in excel_data.sheet_names:
            excel_sheets[sheet_name] = excel_data.parse(sheet_name)

st.success("✅ Files Uploaded & Processed Successfully!") if uploaded_files else None

# **Model Selection Dropdown**
st.subheader("🤖 Select AI Model")
model_options = ["gemma2-9b-it", "llama-3.3-70b-versatile", "mixtral-8x7b-32768", "whisper-large-v3-turbo", "llama3-8b-8192"]
selected_model = st.selectbox("Choose the model to process your query:", model_options)

# **Chat Input**
st.subheader("💬 Ask a Finance Question")
user_input = st.text_area("🔍 Type your finance-related question here...")

if st.button("🚀 Get Answer"):
    client = Groq(api_key=GROQ_API_KEY)

    excel_summary = "\n\n".join([f"Sheet: {name}\n{df.head().to_string()}" for name, df in excel_sheets.items()])
    
    prompt = f"""
    You are Finance GPT, an AI assistant specializing in financial topics.
    User's Question:
    {user_input}

    Relevant Information from Uploaded Documents:
    {combined_text}
    {excel_summary}
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
    st.subheader("💡 Finance GPT Answer")
    st.write(ai_response)
