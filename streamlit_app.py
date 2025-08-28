import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import time
import os
import json
from dotenv import load_dotenv
from markdown_it import MarkdownIt

# --- Firebase Initialization and Globals ---
firebase_config = {}
try:
    # This global variable is provided by the Canvas environment.
    firebase_config = json.loads(__firebase_config)
except NameError:
    # If not running in Canvas, check for a local file.
    if os.path.exists('firebase_creds.json'):
        with open('firebase_creeds.json', 'r') as f:
            firebase_config = json.load(f)
    else:
        st.error("Firebase configuration not found. Please provide a `firebase_creds.json` file or run this app in the Canvas environment.")
        st.stop()
except Exception as e:
    st.error(f"Error loading Firebase configuration: {e}")
    st.stop()

app_id = 'default-app-id'
try:
    app_id = __app_id
except NameError:
    warnMessage = ""
    # st.warning("Running outside Canvas environment. Using default app ID.")
except Exception as e:
    st.error(f"An unexpected error occurred with the app_id: {e}")
    st.stop()

if "type" not in firebase_config:
    firebase_config["type"] = "service_account"

if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(firebase_config)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Error initializing Firebase Admin SDK: {e}")
        st.stop()

# --- Connect to the 'pennydata' database using database_id ---
db = firestore.client(database_id="pennydata")

# --- Gemini AI Setup ---
load_dotenv()
try:
    GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GOOGLE_API_KEY:
        st.error("Missing GEMINI_API_KEY. Please set it in your .env file.")
        # Raise an exception to stop the app if the key is missing
        raise ValueError("GEMINI_API_KEY is not set.")
    else:
        genai.configure(api_key=GOOGLE_API_KEY)
except Exception as e:
    st.error(f"Error configuring Gemini AI: {e}")
    st.stop()

try:
    model = genai.GenerativeModel(model_name="gemini-2.0-flash")
except Exception as e:
    st.error(f"Error creating Gemini model: {e}")

# --- Custom CSS for a Dark Mode theme ---
st.markdown("""
<style>
    /* General styling for the main app container and body */
    .stApp {
        background-color: #1a1a2e; /* Dark blue-purple background */
        color: #e0e0e0; /* Light gray for general text */
        font-family: 'Segoe UI', Arial, sans-serif;
    }

    /* Styling for headers */
    h1, h2, h3, h4, h5, h6 {
        color: #e94560; /* A vibrant red-pink for headers */
        font-family: 'Segoe UI', Arial, sans-serif;
        font-weight: 700; /* Bolder headers */
    }

    /* Styling for various input labels */
    .stRadio > label,
    .stTextInput > label,
    .stNumberInput > label,
    .stDateInput > label,
    .stForm > label {
        color: #e0e0e0;
        font-weight: bold;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    
    /* Styling for buttons */
    .stButton > button {
        background-color: #537d88; /* A muted teal-blue */
        color: white !important;
        border: 2px solid #537d88;
        border-radius: 8px; /* Slightly less rounded for professional look */
        padding: 10px 25px;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-weight: 600;
        transition: background-color 0.3s ease, border-color 0.3s ease, transform 0.2s ease;
    }
    .stButton > button:hover {
        background-color: #72a0a8; /* Lighter teal-blue on hover */
        border-color: #72a0a8;
        color: white !important;
        transform: translateY(-2px); /* Slight lift effect */
    }

    /* Styling for the sidebar */
    .css-1d391kg { /* This is the class for the sidebar container */
        background-color: #0f3460; /* Darker blue for sidebar */
        border-right: 1px solid #16213e;
        font-family: 'Segoe UI', Arial, sans-serif;
        padding-top: 2rem;
        box-shadow: 2px 0 5px rgba(0, 0, 0, 0.3); /* Subtle shadow for definition */
    }
    .css-1d391kg .stButton > button { /* Sidebar button specific styling */
        background-color: #e94560; /* Use accent color for sidebar buttons */
        border-color: #e94560;
        width: 100%; /* Make sidebar buttons full width */
        margin-bottom: 10px;
    }
    .css-1d391kg .stButton > button:hover {
        background-color: #ff6a80; /* Lighter accent on hover */
        border-color: #ff6a80;
    }

    /* Styling for chat messages */
    .stChatMessage {
        background-color: #2e2e4e; /* Darker chat bubble */
        border-radius: 12px; /* Smooth rounded corners */
        padding: 15px;
        margin-bottom: 12px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); /* Enhanced shadow */
        font-family: 'Segoe UI', Arial, sans-serif;
        border-left: 3px solid #e94560; /* Accent border */
    }
    .stChatMessage.st-chat-message-user {
        background-color: #3f3f6e; /* Slightly different shade for user messages */
        border-left: 3px solid #537d88; /* Different accent for user */
    }

    /* Styling for the main content block, including chat input and forms */
    .st-emotion-cache-1c7v05w, .stForm {
        background-color: #1a1a2e; /* Match main background or a slightly lighter shade */
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        font-family: 'Segoe UI', Arial, sans-serif;
        border: 1px solid #16213e; /* Subtle border */
    }
    
    /* Text input fields */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        background-color: #2d2d4a; /* Darker input fields */
        color: #e0e0e0;
        border: 1px solid #537d88;
        border-radius: 5px;
        padding: 10px;
    }
    .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
        border-color: #e94560; /* Highlight focus with accent color */
        box-shadow: 0 0 0 0.1rem rgba(233, 69, 96, 0.5);
    }
    
    /* Info and Error messages */
    .stAlert {
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
    }
    .stAlert.st-success {
        background-color: #28a745;
        color: white;
    }
    .stAlert.st-error {
        background-color: #dc3545;
        color: white;
    }
    .stAlert.st-info {
        background-color: #17a2b8;
        color: white;
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
    with col2:
        if st.button("Sign Up"):
            st.session_state.page = 'signup'

def show_login_page():
    st.title("Login to Your Account")
    with st.form("login_form"):
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Enter")

        if submitted:
            if email:
                st.session_state.logged_in = True
                st.session_state.user_id = 'prototype_user_id'
                st.session_state.user_name = 'Prototype User'
                st.session_state.page = 'home'
                st.rerun()
            else:
                st.error("Please enter an email to log in.")


def show_signup_page():
    st.title("Create Your Account")
    with st.form("signup_form"):
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        email = st.text_input("Email Address")
        password1 = st.text_input("New Password (min. 8 characters & 1 Special Character)", type="password")
        password2 = st.text_input("Confirm Password", type="password")
        submitted = st.form_submit_button("Create Account")

        if submitted:
            if not first_name or not last_name or not email or not password1 or not password2:
                st.error("Please fill in all fields.")
            
            elif password1 != password2:
                st.error("Password mismatch!")

            else:
                try:
                    docs = db.collection(f'artifacts/{app_id}/users').where(filter=FieldFilter("email", "==", email)).stream()
                    if len(list(docs)) > 0:
                        st.error("An account with this email already exists. Please log in.")
                    else:
                        user_ref = db.collection(f'artifacts/{app_id}/users').document()
                        user_ref.set({
                            'uid': user_ref.id,
                            'first_name': first_name,
                            'last_name': last_name,
                            'email': email,
                            'created_at': firestore.SERVER_TIMESTAMP
                        })
                        st.success("Account created successfully! Please log in.")
                        st.session_state.page = 'login'
                        st.rerun()
                except Exception as e:
                    st.error(f"An error occurred: {e}")

def show_home_page():
    st.title("💬 Chat with Penny")
    st.markdown("Hello there! I'm Penny, your budgeting assistant. How can I help you today?")
    st.markdown("---")

    if "persona" not in st.session_state:
        st.session_state.persona = "Friendly"
    st.session_state.persona = st.radio(
        "Choose Penny's persona:",
        ("Friendly", "Professional"),
        index=("Friendly", "Professional").index(st.session_state.persona)
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"], unsafe_allow_html=True)

    if prompt := st.chat_input("Ask Penny a question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            persona_prompt = ""
            if st.session_state.persona == "Friendly":
                persona_prompt = "You are a friendly, calm, and supportive financial assistant for teens. Keep your language simple and encouraging."
            elif st.session_state.persona == "Professional":
                persona_prompt = "You are a professional financial advisor for adults. Use technical but clear language, focusing on practical advice."
            
            user_id = st.session_state.user_id
            budget_ref = db.collection(f'artifacts/{app_id}/users').document(user_id).collection('budget').document('current')
            budget_data = budget_ref.get().to_dict()

            if budget_data:
                budget_info = f"""
                Here is the user's current budget information:
                - Monthly Income: {budget_data.get('income', 'N/A')}
                - Monthly Budget: {budget_data.get('monthly_budget', 'N/A')}
                - Rent: {budget_data.get('rent', 'N/A')}
                - Food: {budget_data.get('food', 'N/A')}
                - Transport: {budget_data.get('transport', 'N/A')}
                - Other Liabilities: {budget_data.get('liabilities', 'N/A')}
                - Extra Info: {budget_data.get('extra_info', 'None provided')}
                Use this information to answer the user's questions.
                """
                full_prompt = f"{persona_prompt}\n\n{budget_info}\n\nUser: {prompt}"
            else:
                full_prompt = f"{persona_prompt}\n\nUser: {prompt}"
            
            with st.spinner('Thinking...'):
                response = genai.GenerativeModel(model_name="gemini-2.0-flash").generate_content(full_prompt)
                assistant_response_raw = response.text
                
                assistant_response_plain = md.render(assistant_response_raw)
                
                st.markdown(assistant_response_plain, unsafe_allow_html=True)
        
        st.session_state.messages.append({"role": "assistant", "content": assistant_response_plain})

def show_budget_page():
    st.title("📝 Budget Details")
    st.markdown("Please provide your financial information below.")
    st.markdown("---")
    user_id = st.session_state.user_id
    budget_ref = db.collection(f'artifacts/{app_id}/users').document(user_id).collection('budget').document('current')

    try:
        doc = budget_ref.get()
        budget_data = doc.to_dict() if doc.exists else {}
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        budget_data = {}

    with st.form("budget_form"):
        st.subheader("Income & Budget")
        income = st.text_input("Monthly Income:", value=str(budget_data.get('income', '')), placeholder="e.g., 1500 XCD")
        monthly_budget = st.text_input("Overall Monthly Budget:", value=str(budget_data.get('monthly_budget', '')), placeholder="e.g., 1000 XCD")

        st.subheader("Expenses & Liabilities")
        rent = st.text_input("Rent:", value=str(budget_data.get('rent', '')), placeholder="e.g., 500 XCD")
        food = st.text_input("Food:", value=str(budget_data.get('food', '')), placeholder="e.g., 300 XCD")
        transport = st.text_input("Transport:", value=str(budget_data.get('transport', '')), placeholder="e.g., 100 XCD")
        liabilities = st.text_input("Other Liabilities:", value=str(budget_data.get('liabilities', '')), placeholder="e.g., 50 XCD")
        
        st.subheader("Extra Information")
        extra_info = st.text_area("Tell us more about your situation:", value=budget_data.get('extra_info', ''))

        submitted = st.form_submit_button("Save Budget Details")

        if submitted:
            try:
                budget_ref.set({
                    'income': float(income or 0),
                    'monthly_budget': float(monthly_budget or 0),
                    'rent': float(rent or 0),
                    'food': float(food or 0),
                    'transport': float(transport or 0),
                    'liabilities': float(liabilities or 0),
                    'extra_info': extra_info,
                    'updated_at': firestore.SERVER_TIMESTAMP
                })
                st.success("Budget details saved successfully!")
                time.sleep(1)
                st.rerun()
            except ValueError:
                st.error("Please ensure all financial inputs are valid numbers.")
            except Exception as e:
                st.error(f"An error occurred: {e}")

def show_financial_goals_page():
    st.title("🎯 Financial Goals")
    st.markdown("Set your goals and see if they are achievable.")
    st.markdown("---")
    user_id = st.session_state.user_id
    goals_ref = db.collection(f'artifacts/{app_id}/users').document(user_id).collection('goals')

    try:
        docs = goals_ref.stream()
        goals = {doc.id: doc.to_dict() for doc in docs}
    except Exception as e:
        st.error(f"Error fetching goals: {e}")
        goals = {}

    if 'editing_goal_id' in st.session_state and st.session_state.editing_goal_id:
        goal_id = st.session_state.editing_goal_id
        goal_data = goals.get(goal_id, {})
        st.subheader("Edit Goal")
        with st.form("edit_goal_form"):
            new_goal_name = st.text_input("Goal Name:", value=goal_data.get('goal_name', ''))
            new_goal_amount = st.text_input("Cost:", value=str(goal_data.get('goal_amount', '')))
            new_time_span = st.text_input("Months to Save:", value=str(goal_data.get('time_span', '')))
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Save Changes"):
                    try:
                        goals_ref.document(goal_id).update({
                            'goal_name': new_goal_name,
                            'goal_amount': float(new_goal_amount or 0),
                            'time_span': int(new_time_span or 1),
                            'updated_at': firestore.SERVER_TIMESTAMP
                        })
                        st.success("Goal updated successfully!")
                        st.session_state.editing_goal_id = None
                        time.sleep(1)
                        st.rerun()
                    except ValueError:
                        st.error("Please enter valid numbers for amount and time span.")
                    except Exception as e:
                        st.error(f"An error occurred while updating: {e}")
            with col2:
                if st.form_submit_button("Cancel"):
                    st.session_state.editing_goal_id = None
                    st.rerun()
        st.markdown("---")


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
                
                budget_data = db.collection(f'artifacts/{app_id}/users').document(user_id).collection('budget').document('current').get().to_dict()
                monthly_saving_capacity = (budget_data.get('income', 0) or 0) - (budget_data.get('monthly_budget', 0) or 0)
                
                monthly_saving_needed = goal_amount_val / time_span_val
                
                prompt = f"Goal: {goal_name} for {goal_amount_val} over {time_span_val} months. Monthly saving needed: {monthly_saving_needed:.2f}. User's estimated monthly saving capacity: {monthly_saving_capacity:.2f}. Is this goal achievable? Provide a friendly, detailed explanation."
                
                with st.spinner('Checking your goal...'):
                    response = genai.GenerativeModel(model_name="gemini-2.0-flash").generate_content(prompt)
                    st.subheader("Penny's Achievability Analysis")
                    
                    rendered_text = md.render(response.text)
                    st.markdown(rendered_text, unsafe_allow_html=True)

                goals_ref.add({
                    'goal_name': goal_name,
                    'goal_amount': goal_amount_val,
                    'time_span': time_span_val,
                    'created_at': firestore.SERVER_TIMESTAMP
                })
                st.success("Goal saved!")
                st.rerun()
            except ValueError:
                st.error("Please enter valid numbers for amount and time span.")
            except Exception as e:
                st.error(f"An error occurred: {e}")

def show_graphs_page():
    st.title("📈 Financial Graphs")
    st.markdown("Visualize your budget and financial progress.")
    st.markdown("---")
    user_id = st.session_state.user_id
    budget_ref = db.collection(f'artifacts/{app_id}/users').document(user_id).collection('budget').document('current')

    try:
        doc = budget_ref.get()
        budget_data = doc.to_dict() if doc.exists else {}

        if budget_data:
            st.subheader("Monthly Budget Breakdown")
            
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

    except Exception as e:
        st.error(f"An error occurred: {e}")

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
