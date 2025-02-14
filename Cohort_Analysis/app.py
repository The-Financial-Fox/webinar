import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from groq import Groq
from dotenv import load_dotenv
from operator import attrgetter
from pptx import Presentation
from pptx.util import Inches

# Load API key securely
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("🚨 API Key is missing! Set it in Streamlit Secrets or a .env file.")
    st.stop()

# Streamlit App UI
st.title("🤖 FP&A AI Agent - SaaS Cohort Analysis")
st.write("Upload an Excel file, analyze retention rates, and get AI-generated FP&A insights!")

# File uploader
uploaded_file = st.file_uploader("📂 Upload your cohort data (Excel format)", type=["xlsx"])

if uploaded_file:
    # Read the Excel file
    sales_data = pd.read_excel(uploaded_file)
    sales_data['Date'] = pd.to_datetime(sales_data['Date'])
    sales_data['CohortMonth'] = sales_data.groupby('Customer_ID')['Date'].transform('min').dt.to_period('M')
    sales_data['PurchaseMonth'] = sales_data['Date'].dt.to_period('M')
    sales_data['CohortIndex'] = (sales_data['PurchaseMonth'] - sales_data['CohortMonth']).apply(attrgetter('n'))
    
    # Create a pivot table for cohort analysis
    cohort_counts = sales_data.pivot_table(index='CohortMonth', columns='CohortIndex', values='Customer_ID', aggfunc='nunique')
    cohort_sizes = cohort_counts.iloc[:, 0]
    retention_rate = cohort_counts.divide(cohort_sizes, axis=0)
    
    # Identify outliers (clients who left all in one month)
    extreme_churn = sales_data.groupby(['PurchaseMonth'])['Customer_ID'].nunique()
    churn_outliers = extreme_churn[extreme_churn > (extreme_churn.mean() + 2 * extreme_churn.std())]
    
    # Plot retention rate heatmap
    st.subheader("🔥 Retention Rate Heatmap")
    plt.figure(figsize=(16, 9))
    sns.heatmap(retention_rate, annot=True, fmt=".0%", cmap="YlGnBu", linewidths=0.5)
    plt.title('Cohort Analysis - Retention Rate', fontsize=16)
    plt.xlabel('Months Since First Purchase', fontsize=12)
    plt.ylabel('Cohort Month', fontsize=12)
    plt.tight_layout()
    st.pyplot(plt)
    
    # AI Insights
    cohort_summary = f"""
    **Cohort Analysis Summary**:
    - Number of Cohorts: {len(cohort_counts)}
    - Retention Rate Breakdown:
    {retention_rate.to_string()}
    - Churn Outliers: {churn_outliers.to_string() if not churn_outliers.empty else 'No extreme churn detected.'}
    """
    
    st.subheader("🤖 AI Agent - FP&A Commentary")
    if st.button("🚀 Generate AI Commentary"):
        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an AI-powered FP&A analyst providing financial insights."},
                {"role": "user", "content": f"""
                    **Insight 1: Analysis Period:** Identify the cohort period being analyzed.
                    **Insight 2: Product Retention:** Identify which product has the highest and lowest retention.
                    **Insight 3: Outlier Analysis:** Detect extreme churn patterns.
                    {cohort_summary}
                """}
            ],
            model="llama3-8b-8192",
        )
        ai_commentary = response.choices[0].message.content
        
        # Display AI insights
        st.subheader("💡 AI-Generated FP&A Insights")
        st.write(ai_commentary)

        # Draft Email to CFO
        email_body = f"""
        Subject: SaaS Cohort Retention Analysis - Key Findings
        
        Dear CFO,
        
        Please find below key insights from our latest cohort retention analysis:
        
        1️⃣ **Analysis Period**: {len(cohort_counts)} cohorts analyzed from {sales_data['CohortMonth'].min()} to {sales_data['CohortMonth'].max()}.
        2️⃣ **Product Retention**: Highest retention observed in {retention_rate.max().idxmax()} months, lowest in {retention_rate.min().idxmin()} months.
        3️⃣ **Outlier Alert**: {churn_outliers.to_string() if not churn_outliers.empty else 'No significant churn spikes detected.'}
        
        Let me know if you'd like further details or a meeting to discuss next steps.
        
        Best,  
        FP&A Team
        """
        
        st.subheader("📩 Email Draft to CFO")
        st.code(email_body)
        
        # Generate PowerPoint Report
        if st.button("📊 Generate PowerPoint Report"):
            prs = Presentation()
            slide_layout = prs.slide_layouts[5]
            slide = prs.slides.add_slide(slide_layout)
            title = slide.shapes.title
            title.text = "SaaS Cohort Retention Analysis"
            
            for insight in ai_commentary.split('\n'):
                slide = prs.slides.add_slide(slide_layout)
                slide.shapes.title.text = insight.strip()
            
            ppt_filename = "Cohort_Analysis_Report.pptx"
            prs.save(ppt_filename)
            
            with open(ppt_filename, "rb") as f:
                st.download_button("📥 Download PowerPoint Report", f, file_name=ppt_filename)
