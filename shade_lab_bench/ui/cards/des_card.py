import streamlit as st

from core.sample_data import get_sample_report
from core.symmetric import (
    benchmark_cipher, decrypt_3des_cbc, encrypt_3des_cbc, encrypt_aes_cbc,
)


def render_des_cbc(ss):
    from ui.layout import explanation, zone_controls, zone_output
    col_controls, col_output = st.columns([1, 2])

    with col_controls:
        with zone_controls():
            st.markdown("#### Controls")
            plaintext = get_sample_report("default")
            st.caption(f"Using sample EMR ({len(plaintext)} bytes)")
            run = st.button("🔒 Encrypt with 3-DES-CBC", use_container_width=True)

    with col_output:
        with zone_output():
            st.markdown("#### Live output")
            if run:
                result = encrypt_3des_cbc(plaintext)
                dec = decrypt_3des_cbc(result["ciphertext"], result["key"], result["iv"])

                ss["des_key"] = result["key"]
                ss["des_iv"] = result["iv"]
                ss["des_ciphertext"] = result["ciphertext"]
                ss["des_plaintext"] = plaintext

                st.metric("Encryption time", f"{result['elapsed_ms']:.3f} ms")
                match = dec["plaintext"] == plaintext
                st.success("Decrypted output matches original plaintext ✅") if match else \
                    st.error("Mismatch on decrypt ❌")

                st.markdown("##### AES vs 3-DES speed, across payload sizes")
                datasets = {
                    "1 KB": get_sample_report("1kb"),
                    "100 KB": get_sample_report("100kb"),
                    "1 MB": get_sample_report("1mb"),
                }
                aes_timings = benchmark_cipher(lambda d: encrypt_aes_cbc(d), datasets)
                des_timings = benchmark_cipher(lambda d: encrypt_3des_cbc(d), datasets)
                st.bar_chart({
                    "AES-128": aes_timings,
                    "3-DES": des_timings,
                })
            elif "des_ciphertext" in ss:
                st.caption("Last run:")
                st.code(ss["des_ciphertext"].hex()[:200] + "...", language=None)
            else:
                st.caption("Click Encrypt to see live output here.")

    explanation(
        "3-DES runs the DES cipher three times in sequence with a 64-bit block size, "
        "compared to AES's single-pass, hardware-accelerated 128-bit blocks -- which is "
        "why it's consistently slower at every payload size.",
        related_card_id="aes_cbc",
    )
