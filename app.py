import asyncio
import streamlit as st
import os
from dotenv import load_dotenv
from tourist_agent import TouristQuery, run_tourist_agent
import nest_asyncio
import google.generativeai as genai

nest_asyncio.apply()
load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    st.error("Gemini API key not found. Please set GEMINI_API_KEY in your .env file.")
    st.stop()

genai.configure(api_key=gemini_api_key)
gemini_client = genai.GenerativeModel("gemini-1.5-flash")

# ---------- UI Design ----------
st.markdown("""
    <style>
    .main {
        background: linear-gradient(to bottom, #e6f3ff, #ffffff);
        padding: 20px;
        border-radius: 10px;
    }
    h1 {
        color: #1a73e8;
        font-family: 'Arial', sans-serif;
        text-align: center;
        font-size: 2.5em;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select {
        border: 2px solid #1a73e8;
        border-radius: 8px;
        padding: 10px;
        font-size: 1em;
    }
    .stButton > button {
        background-color: #1a73e8;
        color: white;
        border-radius: 8px;
        padding: 12px 24px;
        font-size: 1.1em;
        font-weight: bold;
        border: none;
        margin: 10px;
    }
    .stButton > button:hover {
        background-color: #1557b0;
    }
    .trip-plan {
        background-color: #f9f9f9;
        border-left: 5px solid #1a73e8;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------- Main Header ----------
st.title("🌍 AI Tourist Agent")
st.markdown("Plan your dream trip or picnic with personalized recommendations!")

# ---------- Sidebar ----------
with st.sidebar:
    st.header("✨ Travel Tips")
    st.markdown("""
    - **Book Early**: Secure flights and hotels for better deals.
    - **Pack Light**: Bring versatile clothing for changing weather.
    - **Local Cuisine**: Try street food for authentic flavors.
    - **Stay Safe**: Keep digital copies of important documents.
    """)
    st.image("https://img.icons8.com/color/48/000000/passport.png", caption="Ready to Explore!")
    st.header("📅 Book Your Trip")
    st.markdown("""
    - [✈️ Book Flight](https://www.duksaa.com/)
    - [🏨 Book Hotel](https://www.duksaa.com/)
    - [🚗 Book Car](https://www.duksaa.com/)
    """, unsafe_allow_html=True)

# ---------- Form ----------
st.subheader("Tell Us About Your Trip")
with st.form("tourist_form"):
    col1, col2 = st.columns(2)
    with col1:
        destination = st.text_input("Destination", placeholder="e.g., Pakistan, Paris")
    with col2:
        budget = st.selectbox("Budget", ["Not specified", "Low", "Medium", "High"])
    col3, col4 = st.columns(2)
    with col3:
        start_date = st.text_input("Start Date (optional)", placeholder="YYYY-MM-DD")
    with col4:
        end_date = st.text_input("End Date (optional)", placeholder="YYYY-MM-DD")
    interests = st.text_input("Interests (optional)", placeholder="e.g., history, food, nature, picnic")
    submit_button = st.form_submit_button("🚀 Plan My Trip")

# ...existing code...

# ---------- Handle Submission ----------
if submit_button:
    # Validate required fields
    if not destination:
        st.error("Please enter a destination.")
    elif not start_date:
        st.error("Please enter a start date.")
    elif not end_date:
        st.error("Please enter an end date.")
    elif budget == "Not specified":
        st.error("Please select a budget.")
    else:
        try:
            interests_list = [i.strip() for i in interests.split(",")] if interests else None
            query = TouristQuery(
                destination=destination,
                start_date=start_date or None,
                end_date=end_date or None,
                interests=interests_list,
                budget=budget if budget != "Not specified" else None
            )
            with st.spinner("Crafting your perfect trip..."):
                response = asyncio.run(run_tourist_agent(query, gemini_client))
                st.markdown(f"<div class='trip-plan'>{response}</div>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"An error occurred: {e}")