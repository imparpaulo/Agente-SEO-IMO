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
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
BEARER_TOKEN = os.getenv("BEARER_TOKEN")

# Validate required environment variables
if not WEBHOOK_URL or not BEARER_TOKEN:
    st.error("Missing required environment variables. Please check your .env file.")
    st.stop()

HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}",
    "Content-Type": "application/json"
}

# App configuration
MAX_MESSAGES = 2  # Hard limit of 2 messages
TIMEOUT_SECONDS = 60  # Increased timeout to 60 seconds

def initialize_session_state():
    """Initialize session state variables if they don't exist"""
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "message_count" not in st.session_state:
        st.session_state.message_count = 0

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
            timeout=(5, TIMEOUT_SECONDS)  # (connection timeout, read timeout)
        )
        response.raise_for_status()
        return response.json()
    except requests.Timeout:
        st.error("O servidor está demorando para responder. Por favor, aguarde um momento e tente novamente.")
        return {"output": "Tempo limite excedido. Por favor, tente novamente em alguns instantes."}
    except requests.RequestException as e:
        st.error(f"Request failed: {str(e)}")
        return {"output": "Desculpe, ocorreu um erro ao processar seu pedido. Por favor, tente novamente."}

def main():
    st.title("Análise e Otimização de Anúncios Imobiliários")
    
    # Add instructions
    st.markdown("""
    #### Basta fazer copy/paste do seu anúncio original
    #### Limite: 2 anúncios por sessão
    """)
    
    # Initialize session state
    initialize_session_state()
    
    # Display chat history
    display_chat_history()
    
    # Check message limit before showing input
    if len(st.session_state.messages) >= MAX_MESSAGES * 2:  # *2 because each interaction has 2 messages (user + assistant)
        st.warning("Você atingiu o limite de 2 anúncios.")
        st.stop()
    
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
            with st.spinner("Analisando o seu anúncio..."):
                response = send_message_to_webhook(
                    st.session_state.session_id,
                    user_input
                )
                bot_response = response.get("output", "Desculpe, não foi possível processar a sua solicitação.")
                st.write(bot_response)
                add_message("assistant", bot_response)

if __name__ == "__main__":
    main()