import streamlit as st

from core.key_exchange import diffie_hellman_exchange


def render_diffie_hellman(ss):
    from ui.layout import explanation, zone_controls, zone_output
    left, right = st.columns([1, 2])
    with left, zone_controls():
        st.markdown("#### Controls")
        run = st.button("🤝 Exchange DH keys", use_container_width=True)
    with right, zone_output():
        st.markdown("#### Live output")
        if run:
            result = diffie_hellman_exchange()
            ss["dh_shared_secret"] = result["shared_secret"]
            st.metric("DH modulus", f"{result['modulus_bits']} bits")
            st.code(result["shared_secret"].hex()[:64] + "…", language=None)
            st.success("Both parties derived the same secret ✅" if result["match"] else "Secrets differ ❌")
        else: st.caption("No shared secret is transmitted across the network.")
    explanation("DH establishes secrecy but does not authenticate who supplied the public keys.", "mitm")
