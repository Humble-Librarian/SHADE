import streamlit as st

from core.auth import generate_x509_certificate


def render_x509_cert(ss):
    from ui.layout import explanation, zone_controls, zone_output
    left, right = st.columns([1, 2])
    with left, zone_controls():
        st.markdown("#### Controls")
        run = st.button("📜 Create self-signed certificate", use_container_width=True)
    with right, zone_output():
        st.markdown("#### Live output")
        if run:
            result = generate_x509_certificate(ss.get("rsa_private_key"))
            ss["sender_certificate"] = result["certificate"]
            st.success("Certificate is currently valid ✅" if result["valid"] else "Certificate is not currently valid ❌")
            st.write(f"**Subject:** {result['subject']}")
            st.write(f"**Public key:** {result['public_key_bits']} bits")
        else: st.caption("The certificate binds Dr. Sender's identity to a public key.")
    explanation("Certificates let recipients authenticate public keys before using them.", "rsa_keygen")
