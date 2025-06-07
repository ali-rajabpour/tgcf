import streamlit as st
import os
import base64
from tgcf.web_ui.utils import hide_st, switch_theme
from tgcf.config import read_config

# Set page config first
st.set_page_config(
    page_title="Phoenix TGFW",
    page_icon="🐦‍🔥",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Load config and setup theme
CONFIG = read_config()
hide_st(st)
switch_theme(st, CONFIG)

# Custom CSS for better layout
st.markdown("""
    <style>
    .main .block-container {
        padding-top: 2rem;
        max-width: 800px;
    }
    .stExpander > div:first-child {
        background-color: #f0f2f6;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# Center the title
st.markdown("<h1 style='text-align: center;'>Welcome to Phoenix TGFW</h1>", unsafe_allow_html=True)

# Image handling
def get_base64_encoded_image(image_path):
    with open(image_path, 'rb') as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

img_path = os.path.join(os.path.dirname(__file__), 'static/PhoenixTransparent.png')
img_base64 = get_base64_encoded_image(img_path)

html = f"""
<div style='display: flex; justify-content: center; margin: 20px 0;'>
    <img src="data:image/png;base64,{img_base64}" alt="Phoenix logo" width=120>
</div>
"""
st.components.v1.html(html, height=180)

# Add spacing to prevent overlap
st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True)

# Features expander (expanded by default)
with st.expander("Features", expanded=True):
    st.markdown("""
    **Phoenix TGFW** is the ultimate tool to automate custom telegram message forwarding.

    **Key Features:**

    - **Message Forwarding**: Forward messages as "forwarded" or send copies from source to destination chats (groups, channels, or users)
    - **Operation Modes**: 
      - **Past Mode**: Process all existing messages
      - **Live Mode**: Handle upcoming messages in real-time
    - **Flexible Authentication**: Login with a bot or user account
    - **Message Manipulation**: Filter, format, replace, watermark, OCR, and more

    ---
    **Credits & Links**
    - Improved By: Ali Rajabpour Sanati
    - [Rajabpour.com](https://Rajabpour.com)
    - [GitHub Repository](https://github.com/ali-rajabpour/Phoenix-TGFW)
    - [Phoenix Trade Solutions](https://PhoenixTradeSolutions.ir)
    """)

st.warning("Please press Save after changing any config.")
