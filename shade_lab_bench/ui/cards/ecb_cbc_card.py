import streamlit as st

from core.image_modes import encrypt_bmp_pixels
from core.sample_data import get_sample_bmp


def render_ecb_vs_cbc(ss):
    from ui.layout import explanation, zone_controls, zone_output
    col_controls, col_output = st.columns([1, 2])

    with col_controls:
        with zone_controls():
            st.markdown("#### Controls")
            uploaded = st.file_uploader("Upload a BMP (optional)", type=["bmp"])
            if uploaded:
                bmp_bytes = uploaded.read()
                st.caption("Using your uploaded image")
            else:
                bmp_bytes = get_sample_bmp()
                st.caption("Using generated sample image")
            st.image(bmp_bytes, caption="Original", width=180)
            run = st.button("🔓 Encrypt under ECB and CBC", use_container_width=True)

    with col_output:
        with zone_output():
            st.markdown("#### Live output")
            if run:
                ecb_result = encrypt_bmp_pixels(bmp_bytes, mode="ECB")
                cbc_result = encrypt_bmp_pixels(bmp_bytes, key=ecb_result["key"], mode="CBC")

                ss["ecb_output_bmp"] = ecb_result["output_bmp"]
                ss["cbc_output_bmp"] = cbc_result["output_bmp"]

                c1, c2 = st.columns(2)
                with c1:
                    st.image(ecb_result["output_bmp"], caption="ECB — pattern leakage visible")
                with c2:
                    st.image(cbc_result["output_bmp"], caption="CBC — pseudo-random noise")
            elif "ecb_output_bmp" in ss:
                c1, c2 = st.columns(2)
                with c1:
                    st.image(ss["ecb_output_bmp"], caption="ECB (last run)")
                with c2:
                    st.image(ss["cbc_output_bmp"], caption="CBC (last run)")
            else:
                st.caption("Click the button to see both modes side by side.")

    explanation(
        "ECB mode encrypts each block independently, so identical plaintext blocks always "
        "produce identical ciphertext blocks -- shapes and repeated patterns stay visible. "
        "CBC chains each block against the previous ciphertext block, eliminating that leak.",
        related_card_id="avalanche",
    )
