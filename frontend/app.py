import streamlit as st
import requests
import uuid
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000/api/v1/chat")
PAGE_TITLE = "Cosmetics Assistant"
PAGE_ICON = "💄"

st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON)

# Initialize Session State
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.title("Settings")
    st.write(f"**Session ID:** `{st.session_state.session_id}`")
    if st.button("Reset Session"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

# Main UI
st.title(f"{PAGE_ICON} {PAGE_TITLE}")
st.write("Welcome! Ask me anything about our cosmetics products.")

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Input
if prompt := st.chat_input("How can I help you today?"):
    # Add User Message to State
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call Backend API
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
        
        try:
            payload = {
                "session_id": st.session_state.session_id,
                "user_input": prompt
            }
            
            response = requests.post(BACKEND_URL, json=payload)
            response.raise_for_status()
            
            data = response.json()
            bot_response = data.get("response", "No response received.")
            metadata = data.get("metadata", {})
            
            # Show Agent reasoning/route if needed (Debugging/Demo purpose)
            if metadata.get("route"):
                with st.expander(f"Processed by: {metadata.get('route')}"):
                    st.json(metadata)

            # --- Summarization Display ---
            summaries = data.get("summaries", [])
            if summaries:
                with st.sidebar:
                    st.subheader("📜 Conversation Summaries")
                    for i, summary in enumerate(summaries):
                        with st.expander(f"Summarization {i+1}"):
                            st.info(summary)

            message_placeholder.markdown(bot_response)
            
            # Add Assistant Message to State
            st.session_state.messages.append({"role": "assistant", "content": bot_response})
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Error communicating with backend: {e}"
            message_placeholder.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
