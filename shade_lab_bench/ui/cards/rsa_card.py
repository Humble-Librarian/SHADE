import streamlit as st

from core.asymmetric import generate_rsa_keypair


def render_rsa_keygen(ss):
    from ui.layout import explanation, zone_controls, zone_output
    left, right = st.columns([1, 2])
    with left, zone_controls():
        st.markdown("#### Controls")
        run = st.button("🔑 Generate RSA-2048 key pair", use_container_width=True)
    with right, zone_output():
        st.markdown("#### Live output")
        if run:
            result = generate_rsa_keypair()
            ss["rsa_private_key"], ss["rsa_public_key"] = result["private_key"], result["public_key"]
            st.success(f"Generated a {result['bits']}-bit receiver key pair")
            st.code(result["public_key"].decode(), language="text")
        elif "rsa_public_key" in ss:
            st.caption("Current receiver public key")
            st.code(ss["rsa_public_key"].decode(), language="text")
        else: st.caption("Generate an in-memory key pair to continue.")
    explanation("The public key may be shared; only the private key can unwrap a session key.", "hybrid_encrypt")
