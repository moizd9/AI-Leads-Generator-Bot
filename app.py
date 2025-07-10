import streamlit as st
import pandas as pd
import requests
import json
import time
from openai import OpenAI

# 🚀 Load API keys from Streamlit secrets
openai_key = st.secrets["api_keys"]["openai_key"]
serpapi_key = st.secrets["api_keys"]["serpapi_key"]

client = OpenAI(api_key=openai_key)

# Helper functions
def classify_brand_image(rating):
    if rating < 4:
        return "Average"
    elif 4 <= rating <= 4.6:
        return "Need to Improve"
    else:
        return "Too Good"

def get_businesses_from_google_maps(query):
    url = "https://serpapi.com/search"
    params = {
        "engine": "google_maps",
        "type": "search",
        "q": query,
        "api_key": serpapi_key
    }
    response = requests.get(url, params=params)
    data = response.json()

    businesses = []
    for res in data.get("local_results", []):
        businesses.append({
            "Company Name": res.get("title", ""),
            "Website": res.get("website", ""),
            "Type": res.get("type", ""),
            "Rating": res.get("rating", 0)
        })
    return pd.DataFrame(businesses)

def get_full_gpt_analysis(company_name, website, company_type):
    prompt = f"""
You are a digital marketing consultant.

Return ONLY a JSON object like this:
{{
"insight": "...",
"hook": "...",
"speed": "...",
"theme": "...",
"seo": "...",
"social": "..."
}}

Business:
- Name: {company_name}
- Website: {website}
- Type: {company_type}
"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    text = response.choices[0].message.content.strip()
    try:
        data = json.loads(text)
        return (
            data.get("insight", ""),
            data.get("hook", ""),
            data.get("speed", ""),
            data.get("theme", ""),
            data.get("seo", ""),
            data.get("social", "")
        )
    except json.JSONDecodeError:
        return "", "", "", "", "", ""

# 🚀 Streamlit UI
st.markdown("""
    <style>
    .stApp {
        background-color: #fff8e3;
        font-family: 'Helvetica', sans-serif;
    }
    .stButton>button {
        background-color: #F63366;
        color: white;
        border-radius: 8px;
        padding: 0.6em 1.2em;
        font-size: 1rem;
    }
    .stButton>button:hover {
        background-color: #d42255;
        color: white;
    }
    .stDataFrame {
        border: 1px solid #eaeaea;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# Main heading
st.markdown("<h1 style='text-align: center;'>🚀 AI Lead Finder & Marketing Audit Tool</h1>", unsafe_allow_html=True)

# Intro paragraph
st.markdown("""
<div style='font-size: 1.1rem; line-height: 1.6; margin-top: 20px;'>
This <strong>AI-Powered Lead Finder & Marketing Audit Tool</strong> helps you discover local businesses that need digital marketing support and provides instant, tailored insights to grow their online presence.

From analyzing website speed and user experience to offering SEO quick audits and social media presence guesses, this smart agent does the heavy lifting for you.

Whether you're a marketer, consultant, or simply curious about local businesses, this tool delivers actionable recommendations and outreach hooks — all in seconds. Elevate your strategy and unlock new opportunities with data-driven intelligence at your fingertips.
</div>
""", unsafe_allow_html=True)

# Input field
query = st.text_input("📌 Enter type of business & location (like 'Dental Clinics Boston'):")

# Main action button
if st.button("Get Leads"):
    if query:
        with st.spinner(f"🔎 Searching for: {query} ..."):
            df = get_businesses_from_google_maps(query)
            results = []
            for i, row in df.iterrows():
                company = row["Company Name"]
                website = row.get("Website", "")
                ctype = row.get("Type", "")
                rating = row.get("Rating", 0)
                brand_image = classify_brand_image(rating)

                insight, hook, speed, theme, seo, social = get_full_gpt_analysis(company, website, ctype)
                time.sleep(1)

                if insight:
                    results.append({
                        "Company Name": company,
                        "Website": website,
                        "Type": ctype,
                        "Rating": rating,
                        "Brand Image": brand_image,
                        "GPT Insight": insight,
                        "Outreach Hook": hook,
                        "Website Speed Insight": speed,
                        "Theme Suggestion": theme,
                        "SEO Quick Audit": seo,
                        "Social Presence Guess": social
                    })
            
            out_df = pd.DataFrame(results)
            st.success("✅ Done! See your leads below.")
            st.dataframe(out_df)
            csv = out_df.to_csv(index=False)
            st.download_button("📥 Download CSV", csv, "leads.csv", "text/csv")
    else:
        st.warning("⚠️ Please enter a business & location to start.")
else:
    st.info("👉 Enter your query and click 'Get Leads' to start.")

# Footer
st.markdown("""
<hr style='border: 1px solid #ccc;'>
<p style='text-align: center; font-size: 0.9rem;'>
    Developed By - <strong>Moiz Deshmukh</strong>
</p>
""", unsafe_allow_html=True)
