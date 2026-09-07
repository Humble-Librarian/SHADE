import streamlit as st

from core.integrity import compute_sha256, verify_integrity
from core.sample_data import get_sample_report


def render_sha256_integrity(ss):
    from ui.layout import explanation, zone_controls, zone_output
    plaintext = ss.get("aes_plaintext") or get_sample_report("default")

    col_controls, col_output = st.columns([1, 2])

    with col_controls:
        with zone_controls():
            st.markdown("#### Controls")
            st.caption(f"Document: {len(plaintext)} bytes")
            run = st.button("🔑 Compute SHA-256 fingerprint", use_container_width=True)

    with col_output:
        with zone_output():
            st.markdown("#### Live output")
            if run:
                digest = compute_sha256(plaintext)
                ss["sha256_original"] = digest
                st.code(digest, language=None)

                # Re-verify immediately to demonstrate the check passing
                check = verify_integrity(plaintext, digest)
                if check["match"]:
                    st.success("✅ Integrity verified — hashes match perfectly!")
                else:
                    st.error("❌ Hash mismatch")
            elif "sha256_original" in ss:
                st.code(ss["sha256_original"], language=None)
            else:
                st.caption("Click the button to fingerprint the document.")

    explanation(
        "SHA-256 produces a fixed-size fingerprint of any input. Recomputing it after "
        "transmission and comparing to the original is how a receiver detects even a "
        "single flipped bit -- try the Tamper Detection card to see it catch corruption.",
        related_card_id="tamper_detection",
    )
