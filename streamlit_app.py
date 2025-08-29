import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from dotenv import load_dotenv
import json
from markdown_it import MarkdownIt
import time
import datetime

# --- Gemini AI Setup ---
load_dotenv()
try:
    GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GOOGLE_API_KEY:
        st.error("Authentication Error: Missing GEMINI_API_KEY. Please make sure you have a .env file with your API key.")
        st.stop()
    else:
        genai.configure(api_key=GOOGLE_API_KEY)
except Exception as e:
    st.error(f"Error configuring Gemini AI: {e}")
    st.stop()

try:
    model = genai.GenerativeModel(model_name="gemini-2.0-flash")
except Exception as e:
    st.error(f"Error creating Gemini model: {e}")

# --- Custom CSS for a super-polished Dark Mode theme ---
st.markdown("""
<style>
    /* Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Orbitron:wght@500;700&display=swap');

    /* App background and global text */
    .stApp, body {
        background: radial-gradient(1200px 600px at 10% 10%, #0b1220 0%, rgba(11,18,32,0.9) 20%, #0f1724 60%, #111827 100%);
        color: #e6eef3;
        font-family: 'Outfit', system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        letter-spacing: 0.2px;
    }
    
    /* Global word and text styling */
    p, li, div {
        font-family: 'Outfit', sans-serif;
        color: #e6eef3;
        font-weight: 400;
        line-height: 1.6;
        letter-spacing: 0.1px;
    }
    
    strong {
        color: #e6f3ff;
        font-weight: 600;
    }

    /* Headings - neon gradient */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Orbitron', 'Outfit', sans-serif;
        color: #fff;
        margin-top: 0.2rem;
        margin-bottom: 0.8rem;
        line-height: 1.05;
        letter-spacing: 1px;
        text-shadow: 0 6px 20px rgba(0,0,0,0.6);
    }
    h1 {
        font-size: 2.8rem;
        background: linear-gradient(90deg, #ff6b6b, #ffb86b, #6be4ff, #7c4dff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 6px 24px rgba(124,77,255,0.12));
    }
    h2 { font-size: 2.1rem; }
    h3 { font-size: 1.5rem; }

    /* Home page title specific */
    .main-header {
        margin-bottom: 24px;
    }
    .home-title-gradient {
        font-size: 3.2rem;
        font-weight: 800;
        line-height: 0.95;
        margin-bottom: 4px;
    }

    .home-greeting-text {
        font-size: 1.15rem;
        color: #dbeafe;
        margin-bottom: 20px;
        opacity: 0.95;
    }

    /* Persona selection box */
    .persona-selection-box {
        background: linear-gradient(180deg, rgba(20,25,40,0.95), rgba(12,18,30,0.95));
        border: 1px solid rgba(120,120,170,0.06);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
    }
    .persona-selection-label {
        color: #9be7ff;
        font-weight: 700;
        margin-bottom: 10px;
        font-size: 1.1rem;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(20,25,40,0.95), rgba(12,18,30,0.95));
        border-right: 1px solid rgba(120,120,170,0.06);
        padding-top: 1.3rem;
        box-shadow: 6px 0 30px rgba(10,10,20,0.45);
        border-radius: 0 16px 16px 0;
    }
    section[data-testid="stSidebar"] .stButton > button {
        width: 95%; /* Increased width to prevent text overflow */
        margin: 8px auto;
        display: block;
        padding: 12px 20px; /* Adjusted padding to better fit text */
        font-weight: 700;
        border-radius: 14px;
        text-transform: none;
        white-space: nowrap; /* Prevents text from wrapping */
    }
    /* Active sidebar emphasised look */
    section[data-testid="stSidebar"] .stButton > button[aria-selected="true"] {
        box-shadow: inset 0 0 18px rgba(124,77,255,0.14);
        transform: translateY(-2px);
    }

    /* Buttons - global */
    .stButton > button {
        background: linear-gradient(135deg, #6a82fb, #fc5c7d);
        color: #fff !important;
        border: none;
        padding: 10px 22px;
        border-radius: 24px;
        font-weight: 700;
        transition: transform 0.18s ease, box-shadow 0.18s ease, opacity 0.18s ease;
        box-shadow: 0 6px 20px rgba(106,130,251,0.12);
    }
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.01);
        box-shadow: 0 10px 36px rgba(106,130,251,0.14);
        opacity: 0.98;
    }
    .stButton.clear-button > button {
        background: linear-gradient(135deg, #ff6b6b, #ee9b00);
        color: #111 !important;
        box-shadow: 0 6px 20px rgba(255,140,60,0.12);
    }

    /* Form labels & inputs - Fixed Label Text */
    .stTextInput > label, .stNumberInput > label, .stDateInput > label, .stForm > label {
        color: #cfeffd;
        font-weight: 600;
        margin-bottom: 6px;
        white-space: nowrap; /* Prevents labels from wrapping */
    }
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input {
        background: linear-gradient(180deg, #121422, #1e2232);
        border: 1px solid rgba(100,100,140,0.12);
        border-radius: 10px;
        padding: 12px 14px;
        color: #e6f3ff;
        font-size: 1.03rem;
        transition: box-shadow 0.18s ease, border-color 0.18s ease, transform 0.08s ease;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stNumberInput > div > div > input:focus {
        outline: none;
        border-color: rgba(124,77,255,0.85);
        box-shadow: 0 6px 30px rgba(124,77,255,0.06);
        transform: translateY(-1px);
    }

    /* ===== Chat Bubbles (Fixed width issue) ===== */
    .stChatMessage {
        display: inline-block;
        max-width: 95%; /* wider so text doesn’t break too early */
        width: fit-content;
        padding: 14px 20px;
        margin: 8px 0;
        border-radius: 20px;
        font-size: 16px;
        line-height: 1.5;
        word-wrap: break-word; /* ensures super long words still break */
        white-space: pre-wrap; /* preserves line breaks */
        box-shadow: 0 8px 28px rgba(3,6,23,0.45);
        border: 1px solid rgba(255,255,255,0.02);
    }
    .stChatMessage .st-emotion-cache-1wmy06w img {
        border-radius: 50%;
        border: 2px solid rgba(158, 216, 230, 0.18);
    }
    .stChatMessage.st-chat-message-user {
        background: linear-gradient(135deg, rgba(124,77,255,0.95), rgba(68,138,255,0.95));
        color: #f1fbff;
        text-align: right;
        margin-left: 18%;
        border-radius: 20px 20px 4px 20px;
        box-shadow: 0 12px 36px rgba(88,56,173,0.16);
    }
    .stChatMessage.st-chat-message-assistant {
        background: linear-gradient(135deg, rgba(14,62,148,0.96), rgba(12,74,110,0.95));
        color: #f1fbff;
        text-align: left;
        margin-right: 18%;
        border-radius: 20px 20px 20px 4px;
        box-shadow: 0 12px 36px rgba(6,60,140,0.14);
    }

    /* Chat input area (attempt to be resilient to classnames) */
    .st-emotion-cache-1g85z9l, .element-container .stTextInput {
        background: linear-gradient(180deg, #151622, #18202e);
        padding: 10px 14px;
        border-radius: 28px;
        border: 1px solid rgba(140,140,200,0.06);
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .st-emotion-cache-1g85z9l input {
        background: transparent;
        border: none;
        color: #eaf6ff;
        font-size: 1.05rem;
        outline: none;
    }
    .st-emotion-cache-1g85z9l button {
        border-radius: 20px;
        padding: 8px 14px;
        font-weight: 700;
        box-shadow: 0 6px 20px rgba(142,220,230,0.06);
    }

    /* Persona radio / segmented style - resilient selector */
    .stRadio > div[role="radiogroup"] {
        display: flex;
        gap: 12px;
        align-items: center;
        margin-bottom: 18px;
    }
    .stRadio [data-baseweb="radio"] label {
        background: linear-gradient(180deg, #2a2a3f, #212133);
        border-radius: 14px;
        padding: 10px 18px;
        color: #cbdff6;
        font-weight: 700;
        border: 1px solid rgba(120,120,160,0.06);
        cursor: pointer;
        transition: transform 0.12s ease, box-shadow 0.12s ease;
    }
    .stRadio [data-baseweb="radio"][aria-checked="true"] label {
        background: linear-gradient(135deg, rgba(161,140,209,0.95), rgba(252,92,125,0.95));
        color: #fff;
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(161,140,209,0.12);
    }
    .stRadio [data-baseweb="radio"] input[type="radio"] { opacity: 0; position: absolute; left: -9999px; }

    /* Progress bar: keep your custom class usage consistent */
    .progress-container {
        width: 100%;
        background-color: #16202b;
        border-radius: 999px;
        height: 32px;
        overflow: hidden;
        box-shadow: inset 0 3px 12px rgba(0,0,0,0.6);
        margin-top: 8px;
    }
    .progress-fill {
        height: 100%;
        border-radius: 999px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        letter-spacing: 0.6px;
        color: #08101a;
        background: linear-gradient(90deg, #9be7ff, #6a82fb);
        transition: width 0.6s cubic-bezier(.2,.9,.3,1);
    }

    /* Alerts */
    .stAlert {
        border-radius: 10px;
        padding: 14px 18px;
        font-weight: 700;
        background: linear-gradient(180deg, rgba(26,26,40,0.7), rgba(20,20,35,0.7));
        border: 1px solid rgba(120,120,180,0.05);
    }
    .stAlert.st-success { background: linear-gradient(90deg, rgba(72,187,120,0.95), rgba(58,204,136,0.95)); color: #071018; }
    .stAlert.st-error { background: linear-gradient(90deg, rgba(235,87,87,0.95), rgba(240,128,128,0.95)); color: #111; }
    .stAlert.st-info { background: linear-gradient(90deg, rgba(59,130,246,0.95), rgba(96,165,250,0.95)); color: #071018; }

    /* Table styles */
    table { width: 100%; border-collapse: collapse; margin-top: 16px; }
    th, td { padding: 12px 10px; border-bottom: 1px solid rgba(255,255,255,0.03); text-align: left; }
    th { text-transform: uppercase; font-size: 0.86rem; color: #06121a; background: linear-gradient(90deg, #a7f3d0, #bfdbfe); border-radius: 6px; }

    /* Plotly dark tune ups */
    .plotly-graph-div .main-svg {
        filter: drop-shadow(0 0 30px rgba(12,20,55,0.4));
    }

    /* Small devices responsiveness */
    @media (max-width: 640px) {
        h1 { font-size: 2rem; }
        .home-title-gradient { font-size: 2.2rem; }
        .stButton > button { width: 100%; }
        .stChatMessage.st-chat-message-user, .stChatMessage.st-chat-message-assistant { margin-left: 6%; margin-right: 6%; }
    }

    /* Subtle animated glows for important callouts - can be applied via <span class="glow">word</span> */
    .glow {
        background: linear-gradient(90deg,#ffb86b,#6be4ff,#7c4dff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: hueShift 6s linear infinite;
    }
    @keyframes hueShift {
        0% { filter: hue-rotate(0deg); }
        50% { filter: hue-rotate(45deg); }
        100% { filter: hue-rotate(0deg); }
    }

    /* Accessibility helpers - focus outlines */
    button:focus, input:focus, textarea:focus, select:focus {
        outline: 3px solid rgba(124,77,255,0.12);
        outline-offset: 2px;
    }
</style>
""", unsafe_allow_html=True)

# --- Initialize Markdown parser
md = MarkdownIt()

# --- State Management and Data Functions ---
def init_session_state():
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Home"
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'user_name' not in st.session_state:
        st.session_state.user_name = "user"
    if 'financial_data' not in st.session_state:
        st.session_state.financial_data = {
            'income': 0,
            'expenses': {},
            'goals': []
        }
    if 'persona' not in st.session_state:
        st.session_state.persona = "Friendly and supportive peer"
    if 'name_set' not in st.session_state:
        st.session_state.name_set = False


# --- New get_response_from_gemini function with JSON validation and Persona ---
def get_response_from_gemini(prompt, persona):
    
    # Conditionally set the prompt persona based on the user's selection
    persona_prompt = ""
    if persona == "Friendly":
        persona_prompt = """
        -   **Friendly**: A supportive, non-judgmental peer. Use casual language and emojis.
        """
    elif persona == "Professional":
        persona_prompt = """
        -   **Professional**: Formal, concise, and informative. Use clear and professional language without emojis.
        """

    full_prompt = f"""
    ### **Directive: Generate ONLY a JSON Object** ###
    
    You are a financial chatbot named Penny. Your task is to respond to the user by providing a **single JSON object**. Do not include any text or dialogue outside of this JSON.
    
    The JSON object must contain the following keys:
    -   "response": Your reply to the user. Max 150 words.
    -   "quit": `true` or `false`. `true` only if the user says "quit," "bye," or "exit."
    -   "name": The user's name. Default to "user."
    -   "predictiveText1": A short, likely follow-up question.
    -   "predictiveText2": A second short, likely follow-up question.

    ### **Persona** ###
    {persona_prompt}
    
    ### **Your Logic** ###
    -   **Initial Greeting**: If the user's input is a greeting (e.g., "hi", "hello"), your response should be a friendly greeting that asks for their monthly income to get started.
    -   **Data Collection**: If the user's prompt is missing income, expenses, or goals, politely ask for the missing information.
    -   **Budget Summary**: If all financial data is provided, evaluate the budget and provide a concise summary. Start the summary with a simple emoji to indicate status:
        -   ✅: Your budget is on track.
        -   ⚠️: Your budget needs adjustments.
        -   🚨: Your budget is risky.
    -   **Actionable Advice**: After the summary, provide a specific piece of actionable advice.

    ### **Example Input/Output** ###
    User Input: "Hi"
    Expected JSON Output:
    {{"response": "Hi there! 👋 I'm Penny, your budgeting peer. To get started, what's your monthly income?", "quit": false, "name": "user", "predictiveText1": "What if I don't have a steady income?", "predictiveText2": "What kind of expenses should I list?"}}
    
    User's current input: {prompt}
    """
    
    try:
        response = model.generate_content(full_prompt)
        raw_text = response.text.strip()
        
        # New robust JSON parsing logic
        start_index = raw_text.find('{')
        end_index = raw_text.rfind('}')
        
        if start_index == -1 or end_index == -1:
            raise json.JSONDecodeError("JSON object not found in response.", raw_text, 0)
        
        json_string = raw_text[start_index:end_index + 1]
        json_response = json.loads(json_string)
        
        return json_response
    
    except json.JSONDecodeError as e:
        st.warning(f"Error parsing JSON. Raw response: {raw_text}")
        st.warning(f"Error details: {e}")
        # Fallback for when the AI messes up
        return {
            "response": "Oops! I ran into an issue. Please try again.",
            "quit": False,
            "name": st.session_state.user_name,
            "predictiveText1": "",
            "predictiveText2": ""
        }
    except Exception as e:
        st.error(f"Error getting response from Gemini: {e}")
        return {
            "response": "Oops! I ran into an issue. Please try again in a moment.",
            "quit": False,
            "name": st.session_state.user_name,
            "predictiveText1": "",
            "predictiveText2": ""
        }


# --- Page Functions ---
def show_welcome_page():
    st.title("Penny's Budgeting Assistant")
    st.subheader("Your AI-powered peer for smart financial planning.")
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login", key="welcome_login"):
            st.session_state.page = 'login'
            st.rerun()
    with col2:
        if st.button("Sign Up", key="welcome_signup"):
            st.session_state.page = 'signup'
            st.rerun()

def show_login_page():
    st.title("Login to Your Account")
    st.info("This is a simplified prototype. Just enter a name and email to 'log in'.")
    st.markdown("---")
    with st.form("login_form"):
        user_name = st.text_input("First Name:")
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Enter")

        if submitted:
            if email and user_name:
                st.session_state.logged_in = True
                st.session_state.user_id = email
                st.session_state.user_name = user_name # Store user's first name
                st.session_state.page = 'home'
                st.rerun()
            else:
                st.error("Please enter a name and email to log in.")

def show_signup_page():
    st.title("Create Your Account")
    st.info("This feature is currently disabled. Please use the login page to proceed.")
    st.markdown("---")
    if st.button("Go to Login", key="signup_to_login"):
        st.session_state.page = 'login'
        st.rerun()
        
def show_home_page():
    user_name = st.session_state.get('user_name', 'User')
    
    st.markdown(f"""
        <div class="main-header">
            <h1 class='home-title-gradient'>Hi, I'm Penny.</h1>
            <p class='home-greeting-text'>Hello there, **{user_name}**! How can I help you today?</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
        <div class="persona-selection-box">
            <p class='persona-selection-label'>Choose Penny's persona:</p>
    """, unsafe_allow_html=True)

    # Validate and set the persona to prevent the ValueError
    current_persona = st.session_state.get('persona', 'Friendly')
    persona_options = ("Friendly", "Professional")
    if current_persona not in persona_options:
        current_persona = "Friendly"
        st.session_state.persona = "Friendly"
        
    persona = st.radio(
        "Choose Penny's persona:",
        persona_options,
        index=persona_options.index(current_persona),
        horizontal=True,
        label_visibility="collapsed",
        key='persona_selector'
    )
    st.session_state.persona = persona
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    # Add a button to clear the chat messages
    if st.button("Clear Chat", key="clear_chat_button", help="Clear all chat messages", type="secondary"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True) # Add some spacing

    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"], unsafe_allow_html=True)
            
    # Input area for chat
    prompt = st.chat_input("Ask Penny a question...")
    
    if prompt:
        # Add the user's message to the chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display the user's message immediately
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Display a thinking message while waiting for the response
        with st.chat_message("assistant"):
            with st.spinner('Penny is thinking...'):
                # Call the new function that handles the AI response and JSON validation
                ai_response_json = get_response_from_gemini(prompt, st.session_state.persona)

                if 'name' in ai_response_json and ai_response_json['name'] != "user":
                    st.session_state.user_name = ai_response_json['name']
                    st.session_state.name_set = True
                
                if ai_response_json.get("quit", False):
                    st.session_state.messages.append({"role": "assistant", "content": "Goodbye! It was great helping you."})
                    st.rerun()

                ai_response_content = ai_response_json.get("response", "I'm sorry, I couldn't generate a response.")
                st.markdown(ai_response_content)
        
        st.session_state.messages.append({"role": "assistant", "content": ai_response_content})
        st.rerun()

def show_budget_page():
    st.title("📝 Budget Details")
    st.markdown("Please provide your financial information below.")
    st.markdown("---")

    # Initialize budget data if it doesn't exist
    if 'budget' not in st.session_state:
        st.session_state.budget = {}

    with st.form("budget_form"):
        st.markdown("##### Income & Overall Budget")
        income = st.text_input("Monthly Income:", value=str(st.session_state.budget.get('income', '')), placeholder="e.g., 1500 XCD", key='budget_income')
        monthly_budget = st.text_input("Overall Monthly Budget:", value=str(st.session_state.budget.get('monthly_budget', '')), placeholder="e.g., 1000 XCD", key='budget_monthly_budget')

        st.markdown("##### Expenses & Liabilities")
        rent = st.text_input("Rent:", value=str(st.session_state.budget.get('rent', '')), placeholder="e.g., 500 XCD", key='budget_rent')
        food = st.text_input("Food:", value=str(st.session_state.budget.get('food', '')), placeholder="e.g., 300 XCD", key='budget_food')
        transport = st.text_input("Transport:", value=str(st.session_state.budget.get('transport', '')), placeholder="e.g., 100 XCD", key='budget_transport')
        liabilities = st.text_input("Other Liabilities:", value=str(st.session_state.budget.get('liabilities', '')), placeholder="e.g., 50 XCD", key='budget_liabilities')
        
        submitted = st.form_submit_button("Save Budget Details")
        
        if submitted:
            try:
                st.session_state.budget = {
                    'income': float(income or 0),
                    'monthly_budget': float(monthly_budget or 0),
                    'rent': float(rent or 0),
                    'food': float(food or 0),
                    'transport': float(transport or 0),
                    'liabilities': float(liabilities or 0)
                }
                st.success("Budget details saved! Navigate to the 'Graphs' page to see your breakdown.")
                st.rerun()
            except ValueError:
                st.error("Please ensure all financial inputs are valid numbers.")

def show_financial_goals_page():
    st.title("🎯 Financial Goals")
    st.markdown("Set your goals and see if they are achievable.")
    st.markdown("---")
    
    # Initialize goals data
    if 'goals' not in st.session_state:
        st.session_state.goals = []

    st.subheader("Add a New Goal")
    with st.form("goal_form"):
        goal_name = st.text_input("What is your goal?", placeholder="e.g., New Laptop")
        goal_amount = st.text_input("What is the cost?", placeholder="e.g., 1200 XCD")
        time_span = st.text_input("How many months do you want to save for?", placeholder="e.g., 6")
        submitted = st.form_submit_button("Check Achievability & Save")

        if submitted:
            try:
                goal_amount_val = float(goal_amount or 0)
                time_span_val = int(time_span or 1)
                
                # Check achievability using Gemini
                budget_data = st.session_state.get('budget', {})
                monthly_saving_capacity = (budget_data.get('income', 0) or 0) - (budget_data.get('monthly_budget', 0) or 0)
                monthly_saving_needed = goal_amount_val / time_span_val
                
                prompt = f"Goal: {goal_name} for {goal_amount_val} over {time_span_val} months. Monthly saving needed: {monthly_saving_needed:.2f}. User's estimated monthly saving capacity: {monthly_saving_capacity:.2f}. Is this goal achievable? Provide a friendly, detailed explanation."
                
                with st.spinner('Checking your goal...'):
                    response = genai.GenerativeModel(model_name="gemini-2.0-flash").generate_content(prompt)
                    st.subheader("Penny's Achievability Analysis")
                    
                    rendered_text = md.render(response.text)
                    st.markdown(rendered_text, unsafe_allow_html=True)
                
                # Save goal to session state with savings history
                st.session_state.goals.append({
                    'goal_name': goal_name,
                    'goal_amount': goal_amount_val,
                    'time_span': time_span_val,
                    'savings_history': [],
                })
                st.success("Goal saved! You can now track your progress below.")
                st.rerun()
            except ValueError:
                st.error("Please enter valid numbers for amount and time span.")

    st.markdown("---")
    st.subheader("Your Saved Goals")
    if st.session_state.goals:
        for i, goal in enumerate(st.session_state.goals):
            st.markdown(f"### {goal['goal_name']}")
            
            # Form to add a new savings contribution
            with st.form(key=f"savings_form_{i}", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    # Changed to text_input to remove - and + buttons
                    savings_amount_str = st.text_input("Amount Saved:", value="", placeholder="e.g., 50.00", key=f"amount_str_{i}")
                with col2:
                    savings_date = st.date_input("Date:", datetime.date.today(), key=f"date_{i}")
                
                submit_savings = st.form_submit_button("Log Savings")
                
                if submit_savings:
                    try:
                        savings_amount = float(savings_amount_str)
                        if savings_amount > 0:
                            st.session_state.goals[i]['savings_history'].append({
                                'date': savings_date,
                                'amount': savings_amount
                            })
                            st.success(f"Saved ${savings_amount:.2f} logged for {goal['goal_name']}!")
                            st.rerun()
                        else:
                            st.warning("Please enter a positive amount to log.")
                    except ValueError:
                        st.error("Please enter a valid number for the amount.")

            # Calculate and display progress
            total_saved = sum(item['amount'] for item in goal['savings_history'])
            goal_amount = goal['goal_amount']
            progress = min(total_saved / goal_amount, 1.0) if goal_amount > 0 else 0.0
            
            st.markdown(f"**Progress:** {total_saved:.2f} / {goal_amount:.2f}")

            # Custom, styled progress bar
            progress_percentage = progress * 100
            st.markdown(f"""
                <div class="progress-container">
                    <div class="progress-fill" style="width: {progress_percentage:.1f}%;">
                        <span>{progress_percentage:.1f}%</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
    else:
        st.info("You haven't set any goals yet.")

def show_graphs_page():
    st.title("📈 Financial Graphs")
    st.markdown("Visualize your budget and financial progress.")
    st.markdown("---")

    budget_data = st.session_state.get('budget', {})
    if budget_data and budget_data.get('income', 0) > 0:
        expenses = {
            'Rent': budget_data.get('rent', 0),
            'Food': budget_data.get('food', 0),
            'Transport': budget_data.get('transport', 0),
            'Liabilities': budget_data.get('liabilities', 0)
        }

        total_expenses = sum(expenses.values())
        income = budget_data.get('income', 0)

        # Calculate remaining balance
        remaining_balance = income - total_expenses
        if remaining_balance > 0:
            expenses['Remaining Balance'] = remaining_balance
        else:
            expenses['Over budget'] = abs(remaining_balance) # Show negative balance as "Over budget"


        df = pd.DataFrame(list(expenses.items()), columns=['Category', 'Amount'])
        
        # Define a custom color sequence that matches the app's theme
        # More vibrant, soft pastel gradients
        custom_colors = ['#FC5C7D', '#6A82FB', '#FFCDD2', '#8EDCE6', '#FBC2EB', '#A18CD1', '#FF7F9F', '#7C4DFF']


        # Create the pie chart with a dark theme and custom colors
        fig = px.pie(
            df, 
            values='Amount', 
            names='Category', 
            title='Distribution of Monthly Finances',
            color_discrete_sequence=custom_colors,
            template="plotly_dark"  # Apply the dark theme
        )
        
        # Center the title for better aesthetics on the dark theme
        fig.update_layout(
            title_x=0.5,
            title_font_size=24,
            title_font_color='#e0e0e0',
            legend_title_font_color='#e0e0e0',
            legend_font_color='#e0e0e0',
            paper_bgcolor='rgba(0,0,0,0)', # Transparent background for the plot area
            plot_bgcolor='rgba(0,0,0,0)', # Transparent background for the chart itself
            margin=dict(l=20, r=20, t=60, b=20) # Adjust margins
        )
        
        # Update trace for text color on slices for better contrast
        fig.update_traces(textinfo='percent+label', marker=dict(line=dict(color='#0b1020', width=1)))
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Please fill out the Budget page to see your graphs.")

def show_log_out_page():
    st.title("Log Out")
    st.markdown("Are you sure you want to log out?")
    st.markdown("---")
    if st.button("Log Out", key="logout_button"):
        st.session_state.clear()
        st.success("You have been logged out successfully.")
        st.info("Redirecting to the welcome page...")
        time.sleep(1)
        st.rerun()

# --- Main App Logic ---
if 'page' not in st.session_state:
    st.session_state.page = 'welcome'

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    with st.sidebar:
        st.markdown("<h2 style='text-align:center; color:#e6eef3; border-bottom: none;'>Penny</h2>", unsafe_allow_html=True)
        st.markdown("---")
        if st.button("Home", key="sidebar_home"):
            st.session_state.page = 'home'
            st.rerun()
        if st.button("Budget", key="sidebar_budget"):
            st.session_state.page = 'budget'
            st.rerun()
        if st.button("Financial Goals", key="sidebar_goals"):
            st.session_state.page = 'goals'
            st.rerun()
        if st.button("Graphs", key="sidebar_graphs"):
            st.session_state.page = 'graphs'
            st.rerun()
        st.markdown("---")
        if st.button("Log Out", key="sidebar_logout"):
            st.session_state.page = 'logout'
            st.rerun()
    
    init_session_state()

    if st.session_state.page == 'home':
        show_home_page()
    elif st.session_state.page == 'budget':
        show_budget_page()
    elif st.session_state.page == 'goals':
        show_financial_goals_page()
    elif st.session_state.page == 'graphs':
        show_graphs_page()
    elif st.session_state.page == 'logout':
        show_log_out_page()

else:
    init_session_state()
    if st.session_state.page == 'login':
        show_login_page()
    elif st.session_state.page == 'signup':
        show_signup_page()
    else:
        show_welcome_page()
