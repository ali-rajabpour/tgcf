import streamlit as st

import os
from tgcf.web_ui.utils import hide_st, switch_theme
from tgcf.config import read_config

CONFIG = read_config()

st.set_page_config(
    page_title="Phoenix TGFW",
    page_icon="🐦‍🔥",
)
hide_st(st)
switch_theme(st,CONFIG)
st.write("# Welcome to Phoenix TGFW")

import base64

def get_base64_encoded_image(image_path):
    with open(image_path, 'rb') as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

# Get base64 string for the image
img_path = os.path.join(os.path.dirname(__file__), 'static/PhoenixTransparent.png')
img_base64 = get_base64_encoded_image(img_path)

html = f"""
<p align="center">
<img src="data:image/png;base64,{img_base64}" alt="Phoenix logo" width=120>
</p>
"""

st.components.v1.html(html, width=None, height=None, scrolling=False)
with st.expander("Features"):
    st.markdown(
        """
    Phoenix TGFW is the ultimate tool to automate custom telegram message forwarding.

    The key features are:

    - Forward messages as "forwarded" or send a copy of the messages from source to destination chats. A chat can be anything: a group, channel, person or even another bot.

    - Supports two modes of operation past or live. The past mode deals with all existing messages, while the live mode is for upcoming ones.

    - You may login with a bot or an user account. Telegram imposes certain limitations on bot accounts. You may use an user account to perform the forwards if you wish.

    - Perform custom manipulation on messages. You can filter, format, replace, watermark, ocr and do whatever else you need !

    - Improved By: Ali Rajabpour Sanati
    
    - https://Rajabpour.com
    
    - https://github.com/ali-rajabpour/Phoenix-TGFW
    
    - https://PhoenixTradeSolutions.ir


        """
    )

st.warning("Please press Save after changing any config.")
