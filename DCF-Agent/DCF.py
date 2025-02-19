import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv
from groq import Groq  # Make sure the groq package is installed and configured

# Load API key securely
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("🚨 API Key is missing! Set it in Streamlit Secrets or a .env file.")
    st.stop()

st.title("💰 DCF Modelling & AI Commentary")
st.write("Enter your assumptions to build a Discounted Cash Flow (DCF) model and get AI-powered insights!")

# User inputs for DCF assumptions
initial_fcf = st.number_input("Initial Free Cash Flow (in millions)", value=100.0, min_value=0.0, step=1.0)
growth_rate_pct = st.number_input("Annual Growth Rate (%)", value=5.0, min_value=0.0, step=0.1)
discount_rate_pct = st.number_input("Discount Rate (%)", value=10.0, min_value=0.0, step=0.1)
terminal_growth_rate_pct = st.number_input("Terminal Growth Rate (%)", value=2.0, min_value=0.0, step=0.1)
forecast_years = st.slider("Forecast Period (years)", 1, 20, 5)

# Convert percentages to decimals
growth_rate = growth_rate_pct / 100.0
discount_rate = discount_rate_pct / 100.0
terminal_growth_rate = terminal_growth_rate_pct / 100.0

# Calculate forecasted Free Cash Flows (FCF) and their present values
years = list(range(1, forecast_years + 1))
forecasted_fcf = [initial_fcf * ((1 + growth_rate) ** year) for year in years]
discounted_fcf = [fcf / ((1 + discount_rate) ** year) for year, fcf in zip(years, forecasted_fcf)]

# Calculate Terminal Value and discount it back to present value
terminal_value = (forecasted_fcf[-1] * (1 + terminal_growth_rate)) / (discount_rate - terminal_growth_rate)
discounted_terminal_value = terminal_value / ((1 + discount_rate) ** forecast_years)

# Total DCF valuation
dcf_valuation = sum(discounted_fcf) + discounted_terminal_value

# Create a DataFrame for display
df = pd.DataFrame({
    "Year": years,
    "Forecasted FCF (M)": forecasted_fcf,
    "Discounted FCF (M)": discounted_fcf
})
st.subheader("📊 DCF Model Details")
st.dataframe(df)

# Plot the forecasted and discounted free cash flows
plt.figure(figsize=(10, 6))
plt.plot(years, forecasted_fcf, marker="o", label="Forecasted FCF")
plt.plot(years, discounted_fcf, marker="o", label="Discounted FCF")
plt.xlabel("Year")
plt.ylabel("Free Cash Flow (in millions)")
plt.title("Forecasted vs Discounted FCF")
plt.legend()
st.pyplot(plt)

# Display the summary of the DCF calculation
dcf_summary = f"""
**DCF Valuation Summary:**

- **Forecast Period:** {forecast_years} years
- **Initial FCF:** {initial_fcf:.2f} million
- **Annual Growth Rate:** {growth_rate_pct:.2f}%
- **Discount Rate:** {discount_rate_pct:.2f}%
- **Terminal Growth Rate:** {terminal_growth_rate_pct:.2f}%
- **Sum of Discounted FCFs:** {sum(discounted_fcf):.2f} million
- **Discounted Terminal Value:** {discounted_terminal_value:.2f} million
- **Total DCF Valuation:** {dcf_valuation:.2f} million
"""
st.markdown(dcf_summary)

# AI Agent Commentary Section
st.subheader("🤖 AI Commentary on the DCF Valuation")
user_prompt = st.text_area("Ask AI for insights on the DCF valuation:", 
                           "Please provide an analysis of the DCF assumptions, valuation, and any potential risks or improvements.")

if st.button("Generate AI Commentary"):
    # Prepare the AI prompt combining the DCF summary and user question
    ai_input = f"Here is the DCF valuation summary:\n{dcf_summary}\n\nUser Query:\n{user_prompt}"
    
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a financial analyst expert providing insights on DCF valuations."},
            {"role": "user", "content": ai_input}
        ],
        model="llama3-8b-8192",
    )
    ai_commentary = response.choices[0].message.content
    st.markdown("### AI-Generated Commentary")
    st.write(ai_commentary)
