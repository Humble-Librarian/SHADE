import streamlit as st

from ui.registry import CARDS, LAYER_LABELS, LAYER_ORDER, cards_in_layer
from ui.state import card_status, open_dashboard

STATUS_ICON = {"done": "✅", "locked": "🔒", "not_started": "⬜"}

LAYER_SUMMARY = {
    "symmetric": "Protects the data itself -- encrypts the EMR so it's unreadable in transit.",
    "asymmetric": "Protects the key -- lets sender and receiver agree on a secret without ever sending it.",
    "integrity": "Catches corruption -- proves the data wasn't altered, accidentally or maliciously.",
    "auth": "Proves identity -- confirms who really sent it and binds that identity to a key.",
}


def render_summary():
    if st.button("← Back to bench"):
        open_dashboard()
        st.rerun()

    st.title("📋 Results Summary")
    st.caption("Mirrors the CLI's option 16 -- a pass/fail snapshot across every card.")

    done = sum(1 for c in CARDS if card_status(c) == "done")
    implemented = sum(1 for c in CARDS if c.render is not None)
    st.metric("Cards completed", f"{done} / {len(CARDS)}", f"{implemented} implemented so far")

    st.divider()
    cols = st.columns(len(LAYER_ORDER))
    for col, layer in zip(cols, LAYER_ORDER):
        with col:
            st.markdown(f"**{LAYER_LABELS[layer]}**")
            for card in cards_in_layer(layer):
                status = card_status(card)
                icon = STATUS_ICON[status]
                note = "" if card.render is not None else " _(soon)_"
                st.markdown(f"{icon} {card.title}{note}")

    st.divider()
    st.markdown("#### How the layers connect")
    st.write(
        "Encrypting the EMR (Layer 1) only protects the data if the encryption key itself "
        "stays secret -- that's what Layer 2 solves, by wrapping the key with RSA or agreeing "
        "on it via Diffie-Hellman instead of ever transmitting it directly. Layer 3 catches "
        "any corruption of the encrypted data along the way, whether accidental or malicious. "
        "Layer 4 answers a different question entirely: not 'was it read or altered?' but "
        "'was it really sent by who it claims?' -- signatures, certificates, and Kerberos all "
        "establish identity rather than confidentiality."
    )
    for layer in LAYER_ORDER:
        st.caption(f"**{LAYER_LABELS[layer]}** -- {LAYER_SUMMARY[layer]}")
