import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from dotenv import load_dotenv
import json # You need to import the json library
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
        border-radius: 20px 
    }
    .stChatMessage.st-chat-message-assistant {
        background: linear-gradient(135deg, rgba(40,50,70,0.9), rgba(25,30,45,0.9));
        color: #e6eef3;
        text-align: left;
        margin-right: 18%;
        border-radius: 20px 
    }
    /* Scrollbar */
    .st-emotion-cache-1kyx52r {
        scrollbar-width: thin;
        scrollbar-color: #4b6cb7 #1f274a;
    }
    .st-emotion-cache-1kyx52r::-webkit-scrollbar {
        width: 10px;
    }
    .st-emotion-cache-1kyx52r::-webkit-scrollbar-track {
        background: #1f274a;
        border-radius: 10px;
    }
    .st-emotion-cache-1kyx52r::-webkit-scrollbar-thumb {
        background-color: #4b6cb7;
        border-radius: 10px;
        border: 3px solid #1f274a;
    }
    .st-emotion-cache-1kyx52r::-webkit-scrollbar-thumb:hover {
        background-color: #5d7ac5;
    }

    /* Make sure Plotly charts fit the container */
    .stPlotlyChart {
        width: 100% !important;
        height: auto !important;
    }

    /* Specific styles for goals and transactions pages */
    .goals-container, .transactions-container {
        padding: 24px;
        background: linear-gradient(180deg, rgba(20,25,40,0.95), rgba(12,18,30,0.95));
        border: 1px solid rgba(120,120,170,0.06);
        border-radius: 16px;
        margin-bottom: 24px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.1);
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, rgba(30,40,60,0.8), rgba(15,20,30,0.8));
        border: 1px solid rgba(124,77,255,0.1);
        padding: 20px 24px;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 30px rgba(124,77,255,0.08);
    }
    [data-testid="stMetric-label"] > div {
        color: #9be7ff;
        font-weight: 700;
        font-size: 1.05rem;
    }
    [data-testid="stMetric-value"] {
        font-size: 2.2rem;
        font-weight: 700;
        color: #e6f3ff;
        text-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    [data-testid="stMetric-delta"] {
        font-size: 1rem;
        font-weight: 600;
        padding-top: 8px;
    }

    /* Expander style */
    .st-emotion-cache-x5yr5g {
        background: linear-gradient(135deg, rgba(40,50,70,0.9), rgba(25,30,45,0.9));
        border: 1px solid rgba(124,77,255,0.1);
        border-radius: 14px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        color: #e6eef3;
    }
    .st-emotion-cache-x5yr5g .st-emotion-cache-1ft4jcp {
        color: #9be7ff;
        font-weight: 600;
        padding: 1rem 1.2rem;
    }

    /* General containers */
    .st-emotion-cache-6q9sum {
        background: transparent;
    }

</style>
""", unsafe_allow_html=True)


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

def add_message(role, content):
    st.session_state.messages.append({"role": role, "content": content})

def get_response_from_gemini(prompt):
    full_prompt = f"""
    You are the brain of a budgeting chatbot named Penny. Your persona is a friendly, calm, and supportive peer who is good with money. Your tone should be encouraging, non-judgmental, and relatable. Use casual language and a few relevant emojis to make the conversation feel natural. You are assisting students (mid-secondary to tertiary school) with managing their finances for the semester. Ensure all text in your responses is formatted to display in a standard, default font (like Arial or sans-serif) to maintain visual consistency.

    Your main job is to help students manage their finances. Your process is as follows:

    1.  **New Rule: Initial State:** If the user says "hi" or initiates a conversation without providing any data, start by greeting them and politely asking for their monthly income. Do not provide a long list of things to do.
    2.  Collect Data: Ask users for their monthly income, expenses, and financial goals. If information is missing, politely and directly ask for it (e.g., "Thanks! To get started, I also need to know your monthly income. What's that looking like?").
    3.  Evaluate: Based on the data, analyze how the user's spending, income, and savings goal align. Do not use verbose, long paragraphs. Instead, provide short, specific feedback.
    4.  Provide a Summary: After the initial data is collected, give a concise, high-level summary of the budget’s health. This summary should be brief—just a few sentences. The goal is to avoid overwhelming the user with long text.
    5.  Give Advice: Offer specific, actionable suggestions. You can also answer general financial questions (e.g., "How do I save more?"). As this is a test system, do not say you can't provide advice.
    6.  **Response Length:** All responses in the "response" key should be between 25 and 150 words. The initial greeting should be no more than 15 words.

    To keep responses concise and non-judgmental, use these codes to summarize the budget's status. The code should be the first thing you mention in the summary.

    - code lambda (λ): Your budget is mostly on track. This means your income comfortably covers your expenses, and you are on a clear path to your financial goal.
    - code epsilon (ε): Your budget needs some adjustments. Your income covers expenses, but the monthly savings target may be a challenge. Small changes are needed to reach your goal.
    - code gamma (γ): Your budget is risky. Your spending is likely exceeding your income, or your financial goal is currently unrealistic with your budget. Significant changes are needed.

    All your replies must be in a JSON object with the following five keys. Do not use any Markdown or special formatting (like bolding, italics, or code blocks) that would alter the font of the text.

    - "response": Your actual reply to the user.
    - "quit": true or false. Set to true only if the user uses an explicit exit phrase like "quit," "bye," or "exit."
    - "name": The user's name. Default to "user" if not provided.
    - "predictiveText1": A likely follow-up question. (Max 25 words, with a line break after 7 words)
    - "predictiveText2": Another likely follow-up question. (Max 25 words, with a line break after 7 words)
    
    Current chat history for context (keep responses brief):
    {st.session_state.messages}
    
    User's current input: {prompt}
    """
    
    try:
        response = model.generate_content(full_prompt)
        
        # --- NEW LOGIC FOR ENFORCING RESPONSE LENGTH ---
        json_response = json.loads(response.text)
        
        # Define a character limit (e.g., 500 characters, roughly 100-125 words)
        char_limit = 500
        
        # Truncate the response if it's too long
        if len(json_response["response"]) > char_limit:
            # Find the last full sentence before the limit
            truncated_text = json_response["response"][:char_limit]
            last_period_index = truncated_text.rfind('.')
            if last_period_index != -1:
                truncated_text = truncated_text[:last_period_index + 1]
            else:
                # If no period is found, just truncate and add an ellipsis
                truncated_text = truncated_text.strip() + '...'
            
            json_response["response"] = truncated_text
            
        return json_response

    except Exception as e:
        st.error(f"Error getting response from Gemini: {e}")
        return {
            "response": "Oops! I ran into an issue. Please try again in a moment.",
            "quit": False,
            "name": st.session_state.user_name,
            "predictiveText1": "",
            "predictiveText2": ""
        }


# --- UI and Pages ---
def set_page(page_name):
    st.session_state.current_page = page_name

def show_home_page():
    st.markdown("<div class='main-header'>", unsafe_allow_html=True)
    st.markdown("<h1 class='home-title-gradient'>Hi, I'm Penny.</h1>", unsafe_allow_html=True)
    
    # Updated greeting to use the user's name
    if st.session_state.name_set:
        st.markdown(f"<p class='home-greeting-text'>Hello there, <strong>{st.session_state.user_name}</strong>! How can I help you today?</p>", unsafe_allow_html=True)
    else:
        st.markdown(f"<p class='home-greeting-text'>Hello there! How can I help you today?</p>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

    with st.container():
        st.markdown("<div class='persona-selection-box'>", unsafe_allow_html=True)
        st.markdown("<p class='persona-selection-label'>I can be a...</p>", unsafe_allow_html=True)
        st.session_state.persona = st.radio(
            "Select my persona:",
            ["Friendly and supportive peer", "Knowledgeable financial advisor", "Straight-to-the-point coach"],
            key="persona_radio",
            index=0,
            label_visibility="hidden"
        )
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat input logic
    if prompt := st.chat_input("Ask Penny a question..."):
        add_message("user", prompt)
        
        # Get AI response
        ai_response_json = get_response_from_gemini(prompt)

        # Check for user's name in the response
        if 'name' in ai_response_json and ai_response_json['name'] != "user":
            st.session_state.user_name = ai_response_json['name']
            st.session_state.name_set = True

        # Check for quit command
        if ai_response_json.get("quit", False):
            st.session_state.messages.append({"role": "assistant", "content": "Goodbye! It was great helping you."})
            st.rerun()

        # Add the AI's response to messages
        ai_response_content = ai_response_json.get("response", "I'm sorry, I couldn't generate a response.")
        add_message("assistant", ai_response_content)

        # Rerun to display messages
        st.rerun()

def show_budget_page():
    st.header("Your Budget 💰")
    st.markdown("<p>Let's track your income and expenses to get a clear picture of your cash flow.</p>", unsafe_allow_html=True)

    with st.form("income_expenses_form", clear_on_submit=False):
        st.subheader("Monthly Income")
        income = st.number_input(
            "Total Monthly Income",
            min_value=0.0,
            step=1.0,
            key='income_input',
            value=st.session_state.financial_data['income']
        )
        
        st.subheader("Monthly Expenses")
        expense_categories = list(st.session_state.financial_data['expenses'].keys())
        
        if not expense_categories:
            st.info("Add your first expense below!")
        
        for category in expense_categories:
            value = st.number_input(
                f"{category}",
                min_value=0.0,
                step=1.0,
                key=f'expense_{category}',
                value=st.session_state.financial_data['expenses'][category]
            )
            st.session_state.financial_data['expenses'][category] = value
        
        new_expense_col, add_button_col = st.columns([0.7, 0.3])
        with new_expense_col:
            new_expense_name = st.text_input("New Expense Category", key='new_expense_name')
        with add_button_col:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Add Expense", key='add_expense_btn'):
                if new_expense_name:
                    st.session_state.financial_data['expenses'][new_expense_name] = 0.0
                    st.rerun()

        st.markdown("---")
        submit_button = st.form_submit_button("Save Budget")

    if submit_button:
        st.session_state.financial_data['income'] = income
        
        # Update session state with expenses from the form
        for category in expense_categories:
            st.session_state.financial_data['expenses'][category] = st.session_state[f'expense_{category}']

        st.success("Budget saved successfully! ✅")

    total_expenses = sum(st.session_state.financial_data['expenses'].values())
    net_income = st.session_state.financial_data['income'] - total_expenses

    st.markdown("---")
    st.subheader("Your Financial Snapshot")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Income", f"${st.session_state.financial_data['income']:,.2f}")
    with col2:
        st.metric("Total Expenses", f"${total_expenses:,.2f}")
    with col3:
        st.metric("Net Income", f"${net_income:,.2f}", delta=f"You have ${net_income:,.2f} left over.")

    if st.session_state.financial_data['income'] > 0:
        fig = make_subplots(
            rows=1, cols=2,
            specs=[[{'type':'domain'}, {'type':'domain'}]],
            subplot_titles=['Income Distribution', 'Expense Breakdown']
        )
        
        # Income chart (Pie with Net Income)
        income_labels = ['Total Expenses', 'Net Income']
        income_values = [total_expenses, net_income]
        
        fig.add_trace(go.Pie(
            labels=income_labels,
            values=income_values,
            name="Income",
            marker_colors=['#ffb86b', '#6be4ff']
        ), 1, 1)

        # Expenses chart (Pie of expenses)
        expense_labels = list(st.session_state.financial_data['expenses'].keys())
        expense_values = list(st.session_state.financial_data['expenses'].values())
        
        fig.add_trace(go.Pie(
            labels=expense_labels,
            values=expense_values,
            name="Expenses",
            marker_colors=px.colors.sequential.Sunset[:len(expense_labels)]
        ), 1, 2)
        
        fig.update_traces(hole=.4, hoverinfo="label+percent+value")
        fig.update_layout(
            title_text="Your Financial Overview",
            title_x=0.5,
            font=dict(color="#e6eef3", family='Outfit'),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            )
        )
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("Tips for Budgeting"):
        st.markdown("""
        - **Track Everything:** For one month, write down every single expense. This helps you find small things that add up.
        - **Start Small:** Don't try to cut everything at once. Pick one or two categories to reduce, like eating out.
        - **Automate Savings:** Set up a direct transfer from your checking to your savings account on payday.
        - **Use the 50/30/20 Rule:** Try to allocate 50% of your income to needs, 30% to wants, and 20% to savings.
        """)
        
def show_goals_page():
    st.header("Your Financial Goals 🎯")
    st.markdown("<p>Setting goals makes managing money more exciting! What are you saving for?</p>", unsafe_allow_html=True)
    
    with st.form("new_goal_form", clear_on_submit=True):
        st.subheader("Add a New Goal")
        goal_name = st.text_input("What are you saving for? (e.g., New Laptop)")
        goal_amount = st.number_input("Goal Amount ($)", min_value=1.0, step=1.0)
        target_date = st.date_input("Target Completion Date")
        
        if st.form_submit_button("Add Goal"):
            if goal_name and goal_amount > 0:
                st.session_state.financial_data['goals'].append({
                    'name': goal_name,
                    'amount': goal_amount,
                    'target_date': str(target_date),
                    'current_savings': 0,
                    'progress': 0
                })
                st.success(f"Goal '{goal_name}' added! 🎉")
            else:
                st.error("Please enter a valid goal name and amount.")
                
    st.markdown("---")
    st.subheader("Your Current Goals")
    
    if not st.session_state.financial_data['goals']:
        st.info("You haven't added any goals yet. Add one above to get started!")
    
    for i, goal in enumerate(st.session_state.financial_data['goals']):
        with st.container():
            col1, col2, col3 = st.columns([0.4, 0.4, 0.2])
            
            with col1:
                st.markdown(f"**{goal['name']}**")
                st.markdown(f"Target: ${goal['amount']:,.2f}")
                
            with col2:
                st.markdown(f"**Progress**")
                progress_percentage = (goal['current_savings'] / goal['amount']) if goal['amount'] > 0 else 0
                st.progress(progress_percentage)
                st.markdown(f"${goal['current_savings']:,.2f} of ${goal['amount']:,.2f}")
                
            with col3:
                st.markdown("<br>", unsafe_allow_html=True)
                # Buttons for logging savings and deleting
                if st.button("Log Savings", key=f'log_{i}'):
                    # This will open a sub-form to log savings
                    with st.form(f"log_savings_form_{i}", clear_on_submit=True):
                        amount_to_log = st.number_input("Amount to save", min_value=1.0, step=1.0)
                        if st.form_submit_button("Add to Goal"):
                            st.session_state.financial_data['goals'][i]['current_savings'] += amount_to_log
                            st.success(f"${amount_to_log:,.2f} added to '{goal['name']}'!")
                            st.rerun()

                if st.button("Delete", key=f'del_{i}'):
                    st.session_state.financial_data['goals'].pop(i)
                    st.rerun()

    st.markdown("---")
    with st.expander("Pro-Tips for Goals"):
        st.markdown("""
        - **Make it Specific:** Instead of "save money," set a goal like "save $500 for a concert ticket."
        - **Break It Down:** If you have a big goal, figure out how much you need to save each month to hit your target date.
        - **Celebrate Wins:** Every time you hit a savings milestone, celebrate! It keeps you motivated.
        """)

# --- Main App Logic ---
def main():
    init_session_state()

    # Sidebar for navigation
    with st.sidebar:
        st.title("Penny's Pages")
        st.markdown("---")
        if st.button("Home 🏠", key="nav_home"):
            set_page("Home")
        if st.button("Budget 📈", key="nav_budget"):
            set_page("Budget")
        if st.button("Goals 🎯", key="nav_goals"):
            set_page("Goals")
            
        st.markdown("---")
        if st.button("Clear Chat", key="clear_chat_button", help="Start a new conversation."):
            st.session_state.messages = []
            st.rerun()
        if st.button("Reset All Data", key="reset_data_button", help="This will delete your income, expenses, and goals."):
            init_session_state()
            st.session_state.messages.append({"role": "assistant", "content": "All data has been reset."})
            st.rerun()

    if st.session_state.current_page == "Home":
        show_home_page()
    elif st.session_state.current_page == "Budget":
        show_budget_page()
    elif st.session_state.current_page == "Goals":
        show_goals_page()

if __name__ == "__main__":
    main()
