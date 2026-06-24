import streamlit as st
from shared_code import *

load_and_display_css()

st.title(f"👋 À bientôt! Vous êtes déconnecté.")

for key in list(st.session_state.keys()):
    del st.session_state[key]
    