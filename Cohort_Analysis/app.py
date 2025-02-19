import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from groq import Groq
from dotenv import load_dotenv
from operator import attrgetter
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from io import BytesIO

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
    
    # Plot retention rate heatmap and save to a buffer
    st.subheader("🔥 Retention Rate Heatmap")
    fig, ax = plt.subplots(figsize=(16, 9))
    sns.heatmap(retention_rate, annot=True, fmt=".0%", cmap="YlGnBu", linewidths=0.5, ax=ax)
    ax.set_title('Cohort Analysis - Retention Rate', fontsize=16)
    plt.tight_layout()
    st.pyplot(fig)
    
    # Save the figure to a buffer
    heatmap_buffer = BytesIO()
    fig.savefig(heatmap_buffer, format='png', dpi=300)
    heatmap_buffer.seek(0)

    # AI Insights
    st.subheader("🤖 AI Agent - FP&A Commentary")
    if st.button("🚀 Generate AI Commentary"):
        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an AI-powered FP&A analyst providing concise financial insights."},
                {"role": "user", "content": "Analyze retention trends, product impact, churn outliers, and revenue implications."}
            ],
            model="llama3-8b-8192",
        )
        ai_commentary = response.choices[0].message.content
        insights = ai_commentary.split("**Insight")

        def generate_graph():
            fig, ax = plt.subplots(figsize=(6, 3))
            sns.lineplot(data=retention_rate.T, dashes=False, ax=ax)
            ax.set_title("Retention Trends Over Time", fontsize=10)
            plt.xticks(fontsize=8)
            plt.yticks(fontsize=8)
            plt.tight_layout()
            buffer = BytesIO()
            fig.savefig(buffer, format='png', dpi=150)
            buffer.seek(0)
            return buffer

        def create_pptx(heatmap_img, insights_list):
            prs = Presentation()
            slide = prs.slides.add_slide(prs.slide_layouts[0])
            slide.shapes.title.text = "SaaS Cohort Retention Analysis"
            slide.placeholders[1].text = "Generated by FP&A AI Agent"
            slide = prs.slides.add_slide(prs.slide_layouts[5])
            slide.shapes.title.text = "Retention Rate Heatmap"
            image_stream = BytesIO(heatmap_img.getvalue())
            slide.shapes.add_picture(image_stream, Inches(1), Inches(1.5), Inches(8))

            for idx, insight in enumerate(insights_list, start=1):
                if not insight.strip():
                    continue
                slide = prs.slides.add_slide(prs.slide_layouts[5])
                slide.shapes.title.text = f"AI Insight {idx}"
                insight_lines = insight.strip().split("\n")
                insight_title = insight_lines[0][:50]
                insight_body = "\n".join(insight_lines[1:])
                text_box = slide.shapes.add_textbox(Inches(0.5), Inches(1), Inches(5), Inches(5))
                text_frame = text_box.text_frame
                text_frame.word_wrap = True
                text_frame.text = insight_title
                text_frame.paragraphs[0].font.bold = True
                text_frame.paragraphs[0].font.size = Pt(16)
                p = text_frame.add_paragraph()
                p.text = insight_body
                p.space_after = Pt(3)
                p.font.size = Pt(14)
                p.alignment = PP_ALIGN.LEFT
                graph_img = generate_graph()
                graph_stream = BytesIO(graph_img.getvalue())
                slide.shapes.add_picture(graph_stream, Inches(5.5), Inches(1), Inches(3))
            
            ppt_buffer = BytesIO()
            prs.save(ppt_buffer)
            ppt_buffer.seek(0)
            return ppt_buffer

        ppt_buffer = create_pptx(heatmap_buffer, insights)
        email_body = f"""
        **Subject: SaaS Cohort Retention Analysis - Key Insights**
        
        Dear CFO,

        Please find below key insights from our latest cohort retention analysis:

        {ai_commentary}

        Let me know if you’d like to discuss this further or require additional details.

        Best,  
        FP&A Team
        """
        
        st.subheader("📩 Email Draft to CFO")
        st.code(email_body)
        
        st.subheader("📤 Export Results")
        st.download_button(
            label="📊 Download PowerPoint Report",
            data=ppt_buffer,
            file_name="Cohort_Analysis_Report.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )
