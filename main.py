import streamlit as st
import os
import base64
import google.generativeai as genai
from dotenv import load_dotenv
import logging


# Initialize Streamlit app (must be at the very beginning of the script)
st.set_page_config(page_title="techbire-AI", page_icon="favicon.ico")

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Load environment variables
load_dotenv()

# Check and configure generative AI
api_key = os.getenv("GOOGLE_API_KEY")
if api_key is None:
    raise ValueError("GOOGLE_API_KEY environment variable is not set.")

# Configure the generative AI model
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-pro")
except Exception as e:
    logging.error(f"Error configuring generative AI: {e}")
    st.write("An error occurred while configuring the generative AI model.")

# Initialize session state for chat history and context if it doesn't exist
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
    try:
        st.session_state['chat_context'] = model.start_chat(history=[])
    except Exception as e:
        logging.error(f"Error initializing chat context: {e}")
        st.write("An error occurred while initializing the chat context.")

# Function to handle input change or button press
def handle_input():
    if st.session_state.input:
        try:
            # Send the user's message and get the response from the AI
            response = st.session_state['chat_context'].send_message(st.session_state.input, stream=True)
            
            # Update chat history and response text
            st.session_state['chat_history'].append(("You", st.session_state.input))
            response_text = ""
            for chunk in response:
                response_text += chunk.text
            st.session_state['chat_history'].append(("Bot", response_text))
            st.session_state.input = ""  # Clear the input box
        except Exception as e:
            logging.error(f"Error handling input: {e}")
            st.write("An error occurred while processing your request.")

# Input box for user with on_change event
input_box = st.text_input("Input: ", key="input", on_change=handle_input)
submit_button = st.button("Ask the question", on_click=handle_input)

# Function to format and display the response properly
def display_formatted_response(response_text):
    parts = response_text.split('```')
    for i, part in enumerate(parts):
        if i % 2 == 0:
            # This is a text part
            st.markdown(part)
        else:
            # This is a code part
            code_lines = part.strip().split('\n')
            if code_lines and code_lines[0].strip().lower() in ["cpp", "c++", "python", "java", "javascript", "csharp", "html", "css", "sql", "plsql", "ruby", "php"]:
                language = code_lines[0].strip().lower()
                if language in ["cpp", "c++", "java", "javascript", "csharp"]:
                    code_lines[0] = f"// {code_lines[0]}"
                elif language == "python":
                    code_lines[0] = f"# {code_lines[0]}"
                elif language == "html":
                    code_lines[0] = f"<!-- {code_lines[0]} -->"
                elif language in ["css", "sql", "plsql", "ruby", "php"]:
                    code_lines[0] = f"/* {code_lines[0]} */"
            st.code('\n'.join(code_lines))

# Function to display chat history
def display_chat_history(chat_history):
    for i, (role, text) in enumerate(chat_history):
        lines = text.split('\n')
        if len(lines) > 3:  # More than 3 lines
            short_text = '\n'.join(lines[:3])
            remaining_text = '\n'.join(lines[3:])
            st.write(f"{role}: {short_text}")
            with st.expander("READ MORE"):
                st.write(remaining_text)
        else:
            if "```" in text:  # Check if text contains code snippet
                code_blocks = text.split("```")
                for j in range(len(code_blocks)):
                    if j % 2 == 0:  # Text parts
                        st.write(f"{role}: {code_blocks[j]}")
                    else:  # Code parts
                        code_lines = code_blocks[j].strip().split('\n')
                        st.code('\n'.join(code_lines), language='')
            else:
                st.write(f"{role}: {text}")

        # Add three spaces after each complete interaction (You + Bot)
        if role == "Bot" and i < len(chat_history) - 1:
            st.write("&nbsp;" * 3)

# Display chat history
if 'chat_history' in st.session_state:
    display_chat_history(st.session_state['chat_history'])

# # Display chat history
# st.subheader("\n\n\n")
# st.subheader("Chat History:")
# display_chat_history(st.session_state['chat_history'])
