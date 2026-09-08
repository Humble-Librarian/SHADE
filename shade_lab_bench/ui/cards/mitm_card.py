import streamlit as st

from core.key_exchange import simulate_dh_mitm


def render_mitm(ss):
    from ui.layout import explanation, zone_controls, zone_output
    left, right = st.columns([1, 2])
    with left, zone_controls():
        st.markdown("#### Controls")
        run = st.button("⚠️ Simulate Mallory substitution", use_container_width=True)
    with right, zone_output():
        st.markdown("#### Live output")
        if run:
            result = simulate_dh_mitm()
            ss["mitm_secrets"] = result
            st.error("MITM attack succeeded: Mallory holds a separate secret with each party." if result["attack_succeeded"] else "Attack anomaly")
            st.caption("Sender secret: " + result["sender_shared"].hex()[:40] + "…")
            st.caption("Receiver secret: " + result["receiver_shared"].hex()[:40] + "…")
        else: st.caption("Watch what unauthenticated public-key substitution enables.")
    explanation("Signatures and certificates authenticate key exchange and prevent this substitution.", "digital_signature")
