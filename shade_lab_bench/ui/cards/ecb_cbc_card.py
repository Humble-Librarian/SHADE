import io

import streamlit as st
from PIL import Image

from core.image_modes import encrypt_bmp_pixels
from core.sample_data import get_sample_bmp

# Cap dimensions so a large phone-camera JPEG doesn't blow up pixel-block
# encryption time or the rendered preview -- same defensive instinct as the
# avalanche-heatmap fix, applied before anything reaches the unchanged
# core encryption logic below.
MAX_DIMENSION = 300


def _to_bmp_bytes(uploaded_file) -> bytes:
    """
    Converts any Pillow-readable image (PNG, JPG, JPEG, BMP, ...) into raw
    BMP bytes. encrypt_bmp_pixels() only understands the BMP header format,
    so this conversion happens BEFORE that function ever sees the data --
    the core encryption logic itself is untouched and unaware the original
    upload wasn't already a BMP.
    """
    img = Image.open(uploaded_file).convert("RGB")
    if max(img.size) > MAX_DIMENSION:
        img.thumbnail((MAX_DIMENSION, MAX_DIMENSION))
    buffer = io.BytesIO()
    img.save(buffer, format="BMP")
    return buffer.getvalue()


def render_ecb_vs_cbc(ss):
    from ui.layout import explanation, zone_controls, zone_output
    col_controls, col_output = st.columns([1, 2])

    with col_controls:
        with zone_controls():
            st.markdown("#### Controls")
            uploaded = st.file_uploader(
                "Upload an image (optional)",
                type=["bmp", "png", "jpg", "jpeg"],
            )
            if uploaded:
                try:
                    bmp_bytes = _to_bmp_bytes(uploaded)
                    st.caption(f"Using your uploaded image ({uploaded.name})")
                except Exception:
                    st.error("Couldn't read that file as an image -- using the sample instead.")
                    bmp_bytes = get_sample_bmp()
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
