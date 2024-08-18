import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv
import logging

# Function to inject HTML for favicon
def inject_favicon():
    favicon_path = "favicon.ico"  # Adjust path if necessary
    favicon_html = f"""
    <link rel="icon" href="data:image/x-icon;base64,{base64.b64encode(open(favicon_path, 'rb').read()).decode()}">
    """
    st.markdown(favicon_html, unsafe_allow_html=True)

# Call the function to inject the favicon
inject_favicon()

# Your existing Streamlit code
st.set_page_config(page_title="techbire-AI")
st.header("TechBire AI")

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Load environment variables
load_dotenv()

# Configure generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize the generative model
model = genai.GenerativeModel("gemini-pro")


# Initialize session state for chat history and context if it doesn't exist
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
    st.session_state['chat_context'] = model.start_chat(history=[])

# Function to handle input change or button press
def handle_input():
    if st.session_state.input:
        try:
            # Send the user's message and get the response from the AI
            response = st.session_state['chat_context'].send_message(st.session_state.input, stream=True)
            
            # Update chat history with user input
            st.session_state['chat_history'].append(("You", st.session_state.input))
            
            # Safeguard for response
            response_text = ""
            for chunk in response:
                if hasattr(chunk, 'text'):
                    response_text += chunk.text
                else:
                    logging.error(f"Response chunk without 'text': {chunk}")
                    st.write("Error: Response chunk does not contain 'text' attribute.")
            
            # Update chat history with AI response
            st.session_state['chat_history'].append(("Bot", response_text))
        
        except genai.BrokenResponseError as e:
            logging.error(f"BrokenResponseError: {e}")
            st.write("An error occurred with the response.")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            st.write("An unexpected error occurred.")
        
        # Clear the input box
        st.session_state.input = ""

# Input box for user with on_change event
input = st.text_input("Input: ", key="input", on_change=handle_input)
submit = st.button("Ask the question", on_click=handle_input)

# Function to format and display the response properly
def display_formatted_response(response_text):
    parts = response_text.split('```')
    for i, part in enumerate(parts):
        if i % 2 == 0:
            st.markdown(part)
        else:
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

# Display formatted response
if 'chat_history' in st.session_state and st.session_state['chat_history']:
    last_entry = st.session_state['chat_history'][-1]
    if last_entry[0] == "Bot":
        display_formatted_response(last_entry[1])

# Function to display chat history
def display_chat_history(chat_history):
    for i, (role, text) in enumerate(chat_history):
        lines = text.split('\n')
        if len(lines) > 3:
            short_text = '\n'.join(lines[:3])
            remaining_text = '\n'.join(lines[3:])
            st.write(f"{role}: {short_text}")
            with st.expander("READ MORE"):
                st.write(remaining_text)
        else:
            if "```" in text:
                code_blocks = text.split("```")
                for j in range(len(code_blocks)):
                    if j % 2 == 0:
                        st.write(f"{role}: {code_blocks[j]}")
                    else:
                        code_lines = code_blocks[j].strip().split('\n')
                        st.code('\n'.join(code_lines), language='')
            else:
                st.write(f"{role}: {text}")
        
        # Add spacing after each interaction
        if role == "Bot" and i < len(chat_history) - 1:
            st.write("&nbsp;" * 3)

# Display chat history
st.subheader("\n\n\n")
st.subheader("Chat History:")
display_chat_history(st.session_state['chat_history'])
