"""
SHADE Lab Bench -- entry point.

Routes between Dashboard / Card Detail / Results Summary views based on
st.session_state.active_view. See design.md section 4 for the information
architecture and claude.md for contribution rules.
"""

import streamlit as st

from ui.layout import render_card_detail, render_dashboard, render_sidebar
from ui.registry import CARDS_BY_ID
from ui.state import init_state
from ui.summary import render_summary
from ui.theme import apply_theme, inject_theme_css

st.set_page_config(
    page_title="SHADE — Crypto Lab Bench",
    page_icon="🏥",
    layout="wide",
)

init_state()
apply_theme()
render_sidebar()

view = st.session_state.active_view

if view == "dashboard":
    render_dashboard()
elif view == "card":
    card = CARDS_BY_ID[st.session_state.active_card_id]
    render_card_detail(card)
elif view == "summary":
    render_summary()
else:
    render_dashboard()

inject_theme_css()
