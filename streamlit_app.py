import streamlit as st
import requests
import uuid
import json
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

load_dotenv()

# Hide Streamlit menu and footer
st.set_page_config(
    page_title="Chat Interface",
    menu_items={},  # Empty dict removes all menu items
    initial_sidebar_state="collapsed"
)

# Hide hamburger menu and "deploy" button with more specific selectors
hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        [data-testid="stToolbar"] {visibility: hidden !important;}
        [data-testid="stDecoration"] {visibility: hidden !important;}
        [data-testid="stHeader"] {visibility: hidden !important;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

# Constants
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://n8n-a48r.onrender.com/webhook/invoke_agent")
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "teste01")
HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}",
    "Content-Type": "application/json"
}

# Add these constants from .env
MAX_MESSAGES = int(os.getenv("MAX_MESSAGES", 50))
TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", 30))

def initialize_session_state():
    """Initialize session state variables if they don't exist"""
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "message_count" not in st.session_state:
        st.session_state.message_count = 0

    # Cleanup old messages if too many
    if len(st.session_state.messages) > MAX_MESSAGES:
        st.session_state.messages = st.session_state.messages[-MAX_MESSAGES:]

def display_chat_history():
    """Display all messages in the chat history"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

def add_message(role: str, content: str) -> None:
    """
    Add a message to the chat history.
    
    Args:
        role (str): The role of the message sender ('user' or 'assistant')
        content (str): The content of the message
    """
    st.session_state.messages.append({"role": role, "content": content})

def send_message_to_webhook(session_id: str, user_input: str) -> Dict:
    """Send message to webhook and return response"""
    payload = {
        "sessionId": session_id,
        "chatInput": user_input
    }
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            headers=HEADERS,
            json=payload,
            timeout=TIMEOUT_SECONDS  # Use environment variable
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Request failed: {str(e)}")
        return {"output": "Desculpe, ocorreu um erro ao processar seu pedido. Por favor, tente novamente."}

def main():
    st.title("Análise e Otimização de Anúncios Imobiliários")
    
    # Add reset button in sidebar
    if st.sidebar.button("Nova Conversa"):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()
    
    # Initialize session state
    initialize_session_state()
    
    # Display chat history
    display_chat_history()
    
    # Chat input with placeholder
    if user_input := st.chat_input(
        placeholder="Cole aqui o texto do seu anúncio imobiliário..."
    ):
        # Add user message to chat
        add_message("user", user_input)
        
        # Display user message
        with st.chat_message("user"):
            st.write(user_input)
        
        # Get bot response with proper loading state
        with st.chat_message("assistant"):
            with st.spinner("Analisando seu anúncio..."):
                response = send_message_to_webhook(
                    st.session_state.session_id,
                    user_input
                )
                bot_response = response.get("output", "Desculpe, não foi possível processar sua solicitação.")
                st.write(bot_response)
                add_message("assistant", bot_response)

if __name__ == "__main__":
    main()