import streamlit as st

from core.auth import sign_and_verify
from core.sample_data import get_sample_report


def render_digital_signature(ss):
    from ui.layout import explanation, zone_controls, zone_output
    left, right = st.columns([1, 2])
    with left, zone_controls():
        st.markdown("#### Controls")
        run = st.button("✍️ Sign and verify document", use_container_width=True)
    with right, zone_output():
        st.markdown("#### Live output")
        if run:
            result = sign_and_verify(get_sample_report(), ss.get("rsa_private_key"))
            ss["signature"] = result["signature"]
            st.code(result["hash"], language=None)
            st.success("Original document signature is valid ✅" if result["valid"] else "Signature invalid ❌")
            st.error("One-bit tampering was rejected ✅" if result["tamper_detected"] else "Tampering unexpectedly passed ❌")
        else: st.caption("A signature binds the signer to this exact document hash.")
    explanation("A signature proves both authenticity and integrity; compare the underlying hash here.", "sha256_integrity")
