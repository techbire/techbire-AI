import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv
# Load environment variables
load_dotenv()

# Configure generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to load Gemini Pro model and get responses
model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])

def get_gemini_response(question):
    response = chat.send_message(question, stream=True)
    return response

# Initialize Streamlit app
st.set_page_config(page_title="techbire-AI")
st.header("TechBire AI")

# Initialize session state for chat history if it doesn't exist
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# Function to handle input change or button press
def handle_input():
    if 'response_text' not in st.session_state:
        st.session_state['response_text'] = ""
    if st.session_state.input:
        response = get_gemini_response(st.session_state.input)
        st.session_state['chat_history'].append(("You", st.session_state.input))
        st.session_state['response_text'] = ""
        for chunk in response:
            st.session_state['response_text'] += chunk.text
        st.session_state['chat_history'].append(("Bot", st.session_state['response_text']))
        st.session_state.input = ""  # Clear the input box

# Input box for user with on_change event
input = st.text_input("Input: ", key="input", on_change=handle_input)
submit = st.button("Ask the question", on_click=handle_input)

# Function to format and display the response properly
def display_formatted_response(response_text):
    parts = response_text.split('```')
    for i, part in enumerate(parts):
        if i % 2 == 0:
            # This is a text part
             st.markdown(f"{part}")
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

# Display formatted response
if 'response_text' in st.session_state:
    display_formatted_response(st.session_state['response_text'])

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
st.subheader("\n\n\n")
st.subheader("Chat History:")
display_chat_history(st.session_state['chat_history'])

