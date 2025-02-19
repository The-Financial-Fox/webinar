import streamlit as st
import os
import pandas as pd
from groq import Groq
from dotenv import load_dotenv
import PyPDF2
import warnings

# Suppress unnecessary warnings
warnings.filterwarnings("ignore")

# Load API key securely
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("🚨 API Key is missing! Set it in Streamlit Secrets or a .env file.")
    st.stop()

# Ensure 'openpyxl' is installed for reading Excel files
try:
    import openpyxl
except ImportError:
    st.error("🚨 Missing optional dependency 'openpyxl'. Install it using: pip install openpyxl")
    st.stop()

# **🎨 Streamlit UI Styling**
st.set_page_config(page_title="Finance GPT", page_icon="💰", layout="wide")

# **📂 File Uploads (PDF & Excel)**
st.subheader("📥 Upload Financial Documents (PDF or Excel)")
uploaded_files = st.file_uploader(
    "Upload PDF or Excel documents for analysis.", 
    type=["pdf", "xlsx"], 
    accept_multiple_files=True
)

combined_text = ""
excel_sheets = {}

for uploaded_file in uploaded_files:
    if uploaded_file.type == "application/pdf":
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            combined_text += page.extract_text() or ""
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        excel_data = pd.ExcelFile(uploaded_file, engine='openpyxl')
        for sheet_name in excel_data.sheet_names:
            excel_sheets[sheet_name] = excel_data.parse(sheet_name)

if uploaded_files:
    st.success("✅ Files Uploaded & Processed Successfully!")

# **Model Selection (Multi-Select for 3 models)**
st.subheader("🤖 Select AI Models")
model_options = [
    "llama3-70b-8192", 
    "llama-3.3-70b-versatile", 
    "mixtral-8x7b-32768", 
    "whisper-large-v3-turbo", 
    "llama3-8b-8192"
]
selected_models = st.multiselect(
    "Choose exactly 3 models to process your query:", 
    model_options, 
    default=model_options[:3]
)

if len(selected_models) != 3:
    st.warning("Please select exactly 3 models to compare.")
    st.stop()

# **Chat Input**
st.subheader("💬 Ask a Finance Question")
user_input = st.text_area("🔍 Type your finance-related question here...")

if st.button("🚀 Get Answer"):
    client = Groq(api_key=GROQ_API_KEY)
    
    # Summarize Excel sheets (showing first few rows per sheet)
    excel_summary = "\n\n".join(
        [f"Sheet: {name}\n{df.head().to_string()}" for name, df in excel_sheets.items()]
    )
    
    prompt = f"""
    You are Finance GPT, an AI assistant specializing in financial topics.
    User's Question:
    {user_input}

    Relevant Information from Uploaded Documents:
    {combined_text}
    {excel_summary}
    """
    
    responses = {}
    for model in selected_models:
        try:
            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an AI expert in finance and financial planning & analysis (FP&A)."},
                    {"role": "user", "content": prompt}
                ],
                model=model,
            )
            responses[model] = response.choices[0].message.content
        except Exception as e:
            responses[model] = f"Error: {e}"
    
    # **Display Responses Side by Side**
    st.subheader("💡 Finance GPT Answers")
    cols = st.columns(len(selected_models))
    for col, model in zip(cols, selected_models):
        with col:
            st.markdown(f"### {model}")
            st.write(responses[model])
