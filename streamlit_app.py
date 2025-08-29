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

# --- Custom CSS for a Dark Mode theme with rounded, gradient elements ---
st.markdown("""
<style>
    /* Import a modern font - using Google Fonts for 'Outfit' */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

    /* General styling for the main app container and body */
    .stApp {
        background-color: #1a1a2e; /* Dark navy background */
        color: #e0e0e0; /* Light gray for general text */
        font-family: 'Outfit', sans-serif;
        font-weight: 400;
    }

    /* Styling for headers */
    h1, h2, h3, h4, h5, h6 {
        color: #8edce6; /* A soft, light blue accent for headers - will be overridden by .home-title-gradient for H1 on home */
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.3);
        border-bottom: 1px solid #2e2e42; /* Subtler separator */
        padding-bottom: 15px;
        margin-bottom: 25px;
    }
    h1 { font-size: 2.5em; font-weight: 700; }
    h2 { font-size: 2em; font-weight: 600; }
    h3 { font-size: 1.7em; font-weight: 500; }

    /* Styling for various input labels */
    .stRadio > label,
    .stTextInput > label,
    .stNumberInput > label,
    .stDateInput > label,
    .stForm > label {
        color: #e0e0e0;
        font-weight: 500;
        margin-bottom: 8px; /* Add some space below labels */
    }
    
    /* Styling for buttons */
    .stButton > button {
        background: linear-gradient(135deg, #6a82fb, #fc5c7d); /* Gradient for buttons */
        color: white !important;
        border: none;
        border-radius: 25px; /* More rounded, oval-like */
        padding: 12px 30px;
        font-weight: 600;
        font-size: 1em;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        cursor: pointer;
    }
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
        opacity: 0.9;
    }
    .stButton.clear-button > button {
        background: linear-gradient(135deg, #ff6b6b, #ee9b00); /* Different gradient for clear button */
        color: white !important;
    }
    .stButton.clear-button > button:hover {
        opacity: 0.9;
    }


    /* Styling for the sidebar */
    .css-1d391kg { /* This is the main sidebar container */
        background-color: #2a2a4a; /* Slightly lighter dark for sidebar */
        border-right: 1px solid #3e3e5e;
        padding-top: 2rem;
        box-shadow: 2px 0 10px rgba(0, 0, 0, 0.4);
        border-radius: 0 15px 15px 0; /* Rounded right side for a modern touch */
    }
    .css-1d391kg .stButton > button { /* Sidebar buttons */
        background: linear-gradient(135deg, #a18cd1, #fbc2eb); /* Pastel gradient for sidebar buttons */
        color: #1a1a2e !important; /* Dark text on light button */
        border-color: transparent;
        width: 90%; /* Adjust width for spacing */
        margin: 5px auto; /* Center buttons with auto margin */
        display: block; /* Ensures margin auto works */
        border-radius: 20px; /* More rounded */
        font-weight: 500;
    }
    .css-1d391kg .stButton > button:hover {
        background: linear-gradient(135deg, #b09ee0, #fcd8f2); /* Slightly brighter hover */
        transform: translateY(-1px);
    }
    /* Active sidebar button styling */
    .css-1d391kg .stButton > button[aria-selected="true"] {
        background: linear-gradient(135deg, #fc5c7d, #6a82fb); /* Stronger accent for active */
        color: white !important;
    }


    /* Styling for chat messages */
    .stChatMessage {
        background: #2e2e42; /* Darker background for chat bubbles */
        border-radius: 20px; /* Very rounded, oval-like */
        padding: 18px 22px; /* More padding */
        margin-bottom: 15px; /* More space between messages */
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.25);
        border: none; /* Remove default border */
        color: #e0e0e0;
        font-size: 1.05em;
    }
    .stChatMessage.st-chat-message-user {
        background: linear-gradient(135deg, #7c4dff, #448aff); /* Gradient for user messages */
        color: white;
        text-align: right; /* Align user messages to the right */
        margin-left: auto; /* Push user message to the right */
        border-radius: 20px 20px 5px 20px; /* Slightly different corner for tail */
    }
    .stChatMessage.st-chat-message-assistant {
        background: linear-gradient(135deg, #1e3a8a, #0c4a6e); /* Gradient for assistant messages */
        color: #e0e0e0;
        text-align: left; /* Align assistant messages to the left */
        margin-right: auto; /* Push assistant message to the left */
        border-radius: 20px 20px 20px 5px; /* Slightly different corner for tail */
    }


    /* Styling for the main content block, including chat input and forms */
    .st-emotion-cache-1c7v05w, .stForm {
        background-color: #1a1a2e; /* Match app background */
        border-radius: 15px;
        padding: 30px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        border: 1px solid #2e2e42;
        margin-bottom: 30px; /* Add space below forms/blocks */
    }
    
    /* Text input fields */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea, .stNumberInput > div > div > input {
        background-color: #2e2e42; /* Darker input fields */
        color: #e0e0e0;
        border: 1px solid #3e3e5e;
        border-radius: 10px; /* Rounded corners */
        padding: 12px 15px;
        transition: border-color 0.3s ease, box-shadow 0.3s ease;
        font-size: 1.05em;
    }
    .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus, .stNumberInput > div > div > input:focus {
        border-color: #8edce6; /* Accent color on focus */
        box-shadow: 0 0 0 0.15rem rgba(142, 220, 230, 0.4); /* Subtle glow */
        outline: none; /* Remove default outline */
    }
    
    /* Chat input container styling - for the main chat input at the bottom */
    .st-emotion-cache-1g85z9l { /* This targets the overall chat input container */
        background-color: #2e2e42; /* Match content blocks */
        border-radius: 30px; /* Very rounded */
        padding: 10px 15px;
        border: 1px solid #3e3e5e;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
        display: flex;
        align-items: center;
        gap: 10px;
        margin-top: 30px; /* Space above chat input */
    }
    .st-emotion-cache-1g85z9l input { /* This targets the actual text input within the chat input container */
        background-color: transparent; /* Transparent background */
        color: #e0e0e0;
        border: none; /* Remove border */
        padding: 10px 15px;
        flex-grow: 1;
        font-size: 1.1em;
        outline: none; /* Remove outline */
    }
    .st-emotion-cache-1g85z9l button { /* Send button within chat input */
        background: linear-gradient(45deg, #8edce6, #a18cd1); /* Soft gradient for send button */
        color: #1a1a2e !important;
        border-radius: 25px; /* Oval shape */
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .st-emotion-cache-1g85z9l button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 10px rgba(142, 220, 230, 0.3);
    }
    
    /* Info and Error messages */
    .stAlert {
        border-radius: 10px;
        padding: 15px 20px;
        margin-bottom: 20px;
        border: none; /* Remove default border */
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        font-size: 1em;
    }
    .stAlert.st-success {
        background-color: #4CAF50; /* Green */
        color: white;
    }
    .stAlert.st-error {
        background-color: #f44336; /* Red */
        color: white;
    }
    .stAlert.st-info {
        background-color: #2196F3; /* Blue */
        color: white;
    }

    /* Icon adjustments for better visibility */
    .stChatMessage .st-emotion-cache-1wmy06w img {
        border: 2px solid #8edce6; /* Accent border for assistant icon */
        border-radius: 50%; /* Make icons circular */
    }
    .stChatMessage.st-chat-message-user .st-emotion-cache-1wmy06w img {
        border: 2px solid #fc5c7d; /* Different accent for user icon */
    }

    /* Persona selection as segmented control */
    .stRadio > div[role="radiogroup"] {
        display: flex;
        justify-content: flex-start;
        margin-bottom: 25px;
        gap: 15px; /* Space between radio options */
    }
    .stRadio [data-baseweb="radio"] {
        margin-right: 0px; /* Remove default margin */
    }
    .stRadio [data-baseweb="radio"] label {
        background: linear-gradient(135deg, #3e3e5e, #2e2e42); /* Subtle dark gradient */
        border: 1px solid #5e5e7e;
        border-radius: 20px; /* Very rounded */
        padding: 10px 20px;
        color: #c0c0c0;
        font-weight: 500;
        transition: all 0.3s ease;
        cursor: pointer;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .stRadio [data-baseweb="radio"][aria-checked="true"] label {
        background: linear-gradient(135deg, #a18cd1, #fc5c7d); /* Vibrant gradient when selected */
        border-color: #fc5c7d;
        color: white; /* White text on vibrant background */
        box-shadow: 0 4px 10px rgba(161, 140, 209, 0.4);
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
        gap: 20px;
        margin-bottom: 30px;
        padding-top: 15px;
        border-bottom: none; /* Remove double border */
    }

    /* Custom progress bar container */
    .progress-container {
        width: 100%;
        background-color: #2e2e42;
        border-radius: 15px; /* Rounded progress bar */
        height: 30px; /* Taller progress bar */
        overflow: hidden;
        box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.2);
        margin-top: 10px;
    }
    /* Custom progress bar fill */
    .progress-fill {
        height: 100%;
        background-image: linear-gradient(90deg, #8edce6, #6a82fb); /* Gradient fill */
        border-radius: 15px;
        transition: width 0.5s ease-in-out;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #1a1a2e; /* Dark text on light gradient */
        font-weight: 600;
        text-shadow: 1px 1px 2px rgba(255,255,255,0.2);
        font-size: 0.95em;
        white-space: nowrap; /* Prevent text wrapping */
        padding: 0 10px; /* Padding for text inside bar */
    }
    .progress-fill span {
        text-align: center;
        width: 100%;
    }

    /* --- Specific Styling for Home Page Text --- */
    .home-title-gradient {
        font-size: 3.5em; /* Larger, more prominent */
        font-weight: 700;
        background: linear-gradient(90deg, #fc5c7d, #6a82fb); /* Gradient matching sidebar buttons */
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 15px; /* Adjust spacing */
        text-shadow: 2px 2px 5px rgba(0,0,0,0.4); /* More pronounced shadow */
    }

    .home-greeting-text {
        font-size: 1.6em; /* Slightly larger for emphasis */
        font-weight: 500; /* Medium weight */
        color: #e0e0e0; /* Light text for readability */
        margin-bottom: 40px; /* More space below greeting */
        line-height: 1.4; /* Better line spacing */
    }

    .persona-selection-label {
        color: #8edce6; /* Use a bright accent color for this label */
        font-weight: 600; /* Bolder */
        font-size: 1.15em; /* Slightly larger */
        margin-bottom: 20px; /* Space above radio buttons */
    }

</style>
""", unsafe_allow_html=True)

# --- Initialize Markdown parser
md = MarkdownIt()

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
        </div>
        <p class='home-greeting-text'>Hello there, **{user_name}**! How can I help you today?</p>
    """, unsafe_allow_html=True)
    
    st.markdown("<p class='persona-selection-label'>Choose Penny's persona:</p>", unsafe_allow_html=True)
    persona = st.radio(
        "Choose Penny's persona:",
        ("Friendly", "Professional"),
        index=("Friendly", "Professional").index(st.session_state.get('persona', 'Friendly')),
        horizontal=True,
        label_visibility="collapsed",
        key='persona_selector'
    )
    st.session_state.persona = persona
    
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
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display the user's message immediately
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Display a thinking message while waiting for the response
        with st.chat_message("assistant"):
            with st.spinner('Penny is thinking...'):
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
        fig.update_traces(textinfo='percent+label', marker=dict(line=dict(color='#1a1a2e', width=1)))
        
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
        st.markdown("<h2 style='text-align:center; color:#e0e0e0; border-bottom: none;'>Penny</h2>", unsafe_allow_html=True)
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
