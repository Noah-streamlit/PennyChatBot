import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from dotenv import load_dotenv
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

# --- Custom CSS for a Dark Mode theme (App-Store Level) ---
st.markdown("""
<style>
    /* General styling for the main app container and body */
    .stApp {
        background-color: #0A192F; /* Deep navy background, modern and sleek */
        color: #F0F0F0; /* Off-white for general text */
        font-family: 'Segoe UI', Arial, sans-serif;
    }

    /* Styling for headers */
    h1, h2, h3, h4, h5, h6 {
        color: #64FFDA; /* Mint green for headers, a modern accent */
        font-family: 'Segoe UI', Arial, sans-serif;
        font-weight: 700;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
        border-bottom: 2px solid #1A314A; /* Subtle separator */
        padding-bottom: 10px;
        margin-bottom: 20px;
    }

    /* Styling for various input labels */
    .stRadio > label,
    .stTextInput > label,
    .stNumberInput > label,
    .stDateInput > label,
    .stForm > label {
        color: #F0F0F0;
        font-weight: bold;
    }
    
    /* Styling for buttons */
    .stButton > button {
        background-color: #263353; /* A soft, dark purple for buttons */
        color: #F0F0F0 !important;
        border: 2px solid #304169;
        border-radius: 12px;
        padding: 10px 25px;
        font-weight: 600;
        transition: background-color 0.3s ease, border-color 0.3s ease, transform 0.2s ease;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
    }
    .stButton > button:hover {
        background-color: #304169; /* Lighter shade on hover */
        border-color: #64FFDA; /* Mint green border on hover */
        color: white !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(100, 255, 218, 0.15); /* Subtle glow */
    }

    /* Styling for the sidebar */
    .css-1d391kg {
        background-color: #0B213A; /* Slightly darker shade for sidebar */
        border-right: 1px solid #1A314A;
        padding-top: 2rem;
        box-shadow: 2px 0 5px rgba(0, 0, 0, 0.3);
    }
    .css-1d391kg .stButton > button {
        background-color: #64FFDA; /* Accent color for sidebar buttons */
        color: #0A192F !important;
        border-color: #64FFDA;
        width: 100%;
        margin-bottom: 10px;
    }
    .css-1d391kg .stButton > button:hover {
        background-color: #79FDD4;
        border-color: #79FDD4;
    }

    /* Styling for chat messages */
    .stChatMessage {
        background: #12243D; /* Subtle background for depth */
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 12px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        border-left: 3px solid #64FFDA; /* Accent border */
    }
    .stChatMessage.st-chat-message-user {
        background: #1A314A; /* Slightly different background for user messages */
        border-left: 3px solid #FF7F9F; /* Different accent for user */
    }

    /* Styling for the main content block, including chat input and forms */
    .st-emotion-cache-1c7v05w, .stForm {
        background-color: #12243D;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        border: 1px solid #1A314A;
    }
    
    /* Text input fields */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        background-color: #0B213A; /* Darker input fields */
        color: #F0F0F0;
        border: 1px solid #1A314A;
        border-radius: 8px;
        padding: 10px;
        transition: border-color 0.3s ease;
    }
    .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
        border-color: #64FFDA;
        box-shadow: 0 0 0 0.1rem rgba(100, 255, 218, 0.5);
    }
    
    /* Chat input container styling - for the main chat input at the bottom */
    .st-emotion-cache-1g85z9l { /* This targets the overall chat input container */
        background-color: #12243D; /* Match main content block */
        border-radius: 12px;
        padding: 8px;
        border: 1px solid #1A314A;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        display: flex; /* Enable flexbox for alignment of input and button */
        align-items: center;
        gap: 10px; /* Space between input and button */
    }
    .st-emotion-cache-1g85z9l input { /* This targets the actual text input within the chat input container */
        background-color: #0B213A; /* Darker input field */
        color: #F0F0F0;
        border: 1px solid #1A314A;
        border-radius: 8px;
        padding: 10px;
        flex-grow: 1; /* Allow input to take available space */
    }
    .st-emotion-cache-1g85z9l input:focus {
        border-color: #64FFDA;
        box-shadow: 0 0 0 0.1rem rgba(100, 255, 218, 0.5);
    }
    /* Style for the send button within the chat input */
    .st-emotion-cache-1g85z9l button {
        background-color: #64FFDA; /* Mint green send button */
        color: #0A192F !important;
        border-radius: 8px;
        padding: 8px 15px;
        font-weight: 600;
        transition: background-color 0.3s ease, transform 0.2s ease;
    }
    .st-emotion-cache-1g85z9l button:hover {
        background-color: #79FDD4;
        transform: translateY(-1px);
    }
    
    /* Info and Error messages */
    .stAlert {
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        border: 1px solid transparent;
    }
    .stAlert.st-success {
        background-color: #D4EDDA;
        color: #155724;
        border-color: #C3E6CB;
    }
    .stAlert.st-error {
        background-color: #F8D7DA;
        color: #721C24;
        border-color: #F5C6CB;
    }
    .stAlert.st-info {
        background-color: #D1ECF1;
        color: #0C5460;
        border-color: #BEE5EB;
    }

    /* Icon adjustments for better visibility */
    .stChatMessage .st-emotion-cache-1wmy06w img {
        border: 2px solid #64FFDA;
    }
    .stChatMessage.st-chat-message-user .st-emotion-cache-1wmy06w img {
        border: 2px solid #FF7F9F;
    }

    /* Persona selection as segmented control */
    .stRadio > div[role="radiogroup"] {
        display: flex;
        justify-content: flex-start; /* Align to start */
        margin-bottom: 20px;
    }
    .stRadio [data-baseweb="radio"] {
        margin-right: 10px; /* Space between buttons */
    }
    .stRadio [data-baseweb="radio"] label {
        background-color: #1A314A; /* Darker background for segments */
        border: 1px solid #304169;
        border-radius: 8px;
        padding: 8px 15px;
        color: #F0F0F0;
        font-weight: 500;
        transition: background-color 0.3s ease, border-color 0.3s ease;
        cursor: pointer;
    }
    .stRadio [data-baseweb="radio"][aria-checked="true"] label {
        background-color: #64FFDA; /* Accent color when selected */
        border-color: #64FFDA;
        color: #0A192F; /* Dark text on accent */
    }
    
    /* Hide the default radio button dot for a cleaner segmented look */
    .stRadio [data-baseweb="radio"] input[type="radio"] {
        position: absolute;
        opacity: 0;
        width: 0;
        height: 0;
    }

    /* Style for the main page header */
    .main-header {
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 20px;
        padding-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- Initialize Markdown parser
md = MarkdownIt()

# --- Page Functions ---

def show_welcome_page():
    st.title("Penny's Budgeting Assistant")
    st.subheader("Your AI-powered peer for smart financial planning.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login"):
            st.session_state.page = 'login'
            st.rerun()
    with col2:
        if st.button("Sign Up"):
            st.session_state.page = 'signup'
            st.rerun()

def show_login_page():
    st.title("Login to Your Account")
    st.info("This is a simplified prototype. Just enter a name and email to 'log in'.")
    with st.form("login_form"):
        user_name = st.text_input("First Name:")
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Enter")

        if submitted:
            if email and user_name:
                st.session_state.logged_in = True
                st.session_state.user_id = email
                st.session_state.user_name = user_name
                st.session_state.page = 'home'
                st.rerun()
            else:
                st.error("Please enter a name and email to log in.")

def show_signup_page():
    st.title("Create Your Account")
    st.info("This feature is currently disabled. Please use the login page to proceed.")
    if st.button("Go to Login"):
        st.session_state.page = 'login'
        st.rerun()
        
def show_home_page():
    user_name = st.session_state.get('user_name', 'User')
    # Header without the logo
    st.markdown(f"""
        <div class="main-header">
            <h1>Chat with Penny</h1>
        </div>
        <p style="color: #A0AABA; margin-bottom: 30px;">Hello there, **{user_name}**! I'm Penny, your budgeting assistant. How can I help you today?</p>
    """, unsafe_allow_html=True)
    
    # Persona selection as a segmented control (custom CSS handles appearance)
    st.markdown("<p style='color: #F0F0F0; font-weight: bold;'>Choose Penny's persona:</p>", unsafe_allow_html=True)
    persona = st.radio(
        "Choose Penny's persona:",
        ("Friendly", "Professional"),
        index=("Friendly", "Professional").index(st.session_state.get('persona', 'Friendly')),
        horizontal=True,
        label_visibility="collapsed",
        key='persona_selector'
    )
    st.session_state.persona = persona

    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"], unsafe_allow_html=True)
            
    # Input area for chat
    prompt = st.chat_input("Ask Penny a question...")
    
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display the user's message immediately
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Display a thinking message while waiting for the response
        with st.chat_message("assistant"):
            with st.spinner('Thinking...'):
                persona_prompt = ""
                if st.session_state.persona == "Friendly":
                    persona_prompt = "You are a friendly, calm, and supportive financial assistant for teens. Keep your language simple and encouraging. Address the user by their name."
                elif st.session_state.persona == "Professional":
                    persona_prompt = "You are a professional financial advisor for adults. Use technical but clear language, focusing on practical advice. Address the user by their name."
                
                budget_data = st.session_state.get('budget', {})
                budget_info = f"""
                Here is the user's current budget information:
                - Monthly Income: {budget_data.get('income', 'N/A')}
                - Monthly Budget: {budget_data.get('monthly_budget', 'N/A')}
                - Rent: {budget_data.get('rent', 'N/A')}
                - Food: {budget_data.get('food', 'N/A')}
                - Transport: {budget_data.get('transport', 'N/A')}
                - Other Liabilities: {budget_data.get('liabilities', 'N/A')}
                - Extra Info: {budget_data.get('extra_info', 'None provided')}
                
                Analyze this information to provide a helpful response.
                """
                full_prompt = f"{persona_prompt}\n\nUser's Name: {user_name}\n\n{budget_info}\n\nUser's Question: {prompt}"
                
                response = genai.GenerativeModel(model_name="gemini-2.0-flash").generate_content(full_prompt)
                assistant_response_raw = response.text
                assistant_response_plain = md.render(assistant_response_raw)
                
                st.markdown(assistant_response_plain, unsafe_allow_html=True)
        
        st.session_state.messages.append({"role": "assistant", "content": assistant_response_plain})
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
            remaining_amount = max(0, goal_amount - total_saved)
            
            st.markdown(f"**Total Saved:** ${total_saved:.2f}")
            st.markdown(f"**Remaining:** ${remaining_amount:.2f}")
            st.progress(progress)
            st.markdown(f"**Progress:** {progress * 100:.1f}%")

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
        
        if income > total_expenses:
            expenses['Remaining Balance'] = income - total_expenses
        
        df = pd.DataFrame(list(expenses.items()), columns=['Category', 'Amount'])
        
        fig = px.pie(df, values='Amount', names='Category', title='Distribution of Monthly Finances')
        st.plotly_chart(fig)
    else:
        st.info("Please fill out the Budget page to see your graphs.")

def show_log_out_page():
    st.title("Log Out")
    st.markdown("Are you sure you want to log out?")
    if st.button("Log Out"):
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
        st.markdown("---")
        if st.button("Home"):
            st.session_state.page = 'home'
            st.rerun()
        if st.button("Budget"):
            st.session_state.page = 'budget'
            st.rerun()
        if st.button("Financial Goals"):
            st.session_state.page = 'goals'
            st.rerun()
        if st.button("Graphs"):
            st.session_state.page = 'graphs'
            st.rerun()
        if st.button("Log Out"):
            st.session_state.page = 'logout'

if st.session_state.page == 'welcome':
    show_welcome_page()
elif st.session_state.page == 'login':
    show_login_page()
elif st.session_state.page == 'signup':
    show_signup_page()
elif st.session_state.logged_in and st.session_state.page == 'home':
    show_home_page()
elif st.session_state.logged_in and st.session_state.page == 'budget':
    show_budget_page()
elif st.session_state.logged_in and st.session_state.page == 'goals':
    show_financial_goals_page()
elif st.session_state.logged_in and st.session_state.page == 'graphs':
    show_graphs_page()
elif st.session_state.logged_in and st.session_state.page == 'logout':
    show_log_out_page()
else:
    st.session_state.page = 'welcome'
    st.rerun()
