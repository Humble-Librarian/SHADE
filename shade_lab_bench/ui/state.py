"""
session_state helpers. This is the Streamlit-web equivalent of the CLI's
STATE dict -- see design.md section 6 for the schema and claude.md rule #3
(this file is the one place allowed to import streamlit AND touch session
state directly; card render functions receive `ss` as a parameter instead
of importing streamlit.session_state themselves, to keep them testable).
"""

import streamlit as st


def init_state():
    if "active_view" not in st.session_state:
        st.session_state.active_view = "dashboard"   # "dashboard" | "card" | "summary"
    if "active_card_id" not in st.session_state:
        st.session_state.active_card_id = None
    if "guided_mode" not in st.session_state:
        st.session_state.guided_mode = True


def open_card(card_id: str):
    st.session_state.active_view = "card"
    st.session_state.active_card_id = card_id


def open_dashboard():
    st.session_state.active_view = "dashboard"
    st.session_state.active_card_id = None


def open_summary():
    st.session_state.active_view = "summary"
    st.session_state.active_card_id = None


def card_status(card_spec) -> str:
    """
    Derived, not stored -- a card is "done" once ALL of its declared
    `produces` keys exist in session_state. "locked" if any `requires`
    card isn't done. Otherwise "not_started".
    """
    from ui.registry import CARDS_BY_ID

    for req_id in card_spec.requires:
        req = CARDS_BY_ID[req_id]
        if card_status(req) != "done":
            return "locked"

    if card_spec.produces and all(k in st.session_state for k in card_spec.produces):
        return "done"
    return "not_started"


def reset_all():
    """Clears every artifact key declared across the registry, plus resets view state."""
    from ui.registry import CARDS

    keys_to_clear = set()
    for card in CARDS:
        keys_to_clear.update(card.produces)

    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

    open_dashboard()
