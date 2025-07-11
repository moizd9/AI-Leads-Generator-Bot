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

# 🚀 Streamlit UI with new style
st.markdown("""
    <style>
    .stApp {
        background-color: #fff8e3;
    }
    .stButton>button {
        background-color: #F63366;
        color: white;
        border-radius: 8px;
        padding: 0.5em 1em;
    }
    .stButton>button:hover {
        background-color: #d42255;
    }
    .stDataFrame {
        border: 1px solid #eaeaea;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# 🔥 New header and intro
st.title("🚀 AI Lead Finder & Marketing Audit Tool")

st.markdown("""
<div style='color:#F63366; font-size:18px;'>
    Unlock local business growth in seconds.<br>
    This AI-powered agent finds businesses that need digital marketing help, then whips up tailored insights.
</div>

<br>

✅ Website speed & UX  
✅ SEO quick audits  
✅ Social media pulse  
✅ Outreach hooks & smart suggestions  

Perfect for marketers, consultants, or anyone curious about local opportunities.

✨ Get data-driven leads, boost strategy, and watch your pipeline grow — effortlessly.
""", unsafe_allow_html=True)


# Form inputs
query = st.text_input("📌 Enter type of business & location (ex: Dental Clinics in Boston):", placeholder="Write your query here...")

if st.button("Get Leads"):
    if query:
        with st.spinner(f"Searching for: {query} ..."):
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
        st.warning("Please enter a business & location to start.")
else:
    st.info("👉 Enter your query and click 'Get Leads' to start.")

# Footer
# Footer
st.markdown("""
---
<p style='text-align: center; font-size: 15px;'>
    Developed by <strong>Moiz Deshmukh</strong> | 
    <a href='https://www.moizdeshmukh.com' target='_blank'>www.moizdeshmukh.com</a>
</p>
<p style='text-align: center; font-size: 14px;'>
    Curious how this AI Agent was built? 
    <a href='https://www.moizdeshmukh.com/post/blueprint-how-i-built-the-ai-lead-finder-marketing-audit-agent' target='_blank'>
        Read the full blueprint here.
    </a>
</p>
""", unsafe_allow_html=True)

