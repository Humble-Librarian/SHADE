import streamlit as st

from core.sample_data import get_sample_report, get_sample_bmp  # noqa: F401 (bmp kept for symmetry with other cards)
from core.symmetric import (
    benchmark_cipher, decrypt_aes_cbc, encrypt_aes_cbc, generate_aes_key, generate_iv,
)


def render_aes_cbc(ss):
    from ui.layout import explanation, zone_controls, zone_output
    col_controls, col_output = st.columns([1, 2])

    with col_controls:
        with zone_controls():
            st.markdown("#### Controls")
            source = st.radio(
                "Input", ["Sample EMR", "Type my own", "Upload .txt file"], key="aes_source"
            )
            if source == "Type my own":
                text = st.text_area("Plaintext", value="Patient vitals: BP 128/82, HR 78 bpm", height=100)
                plaintext = text.encode("utf-8")
            elif source == "Upload .txt file":
                uploaded = st.file_uploader("Upload a .txt file", type=["txt"])
                if uploaded:
                    plaintext = uploaded.read()
                    st.caption(f"Using uploaded file ({len(plaintext)} bytes)")
                else:
                    plaintext = get_sample_report("default")
                    st.caption("No file uploaded yet -- using sample EMR for now")
            else:
                plaintext = get_sample_report("default")
                st.caption(f"Using sample EMR ({len(plaintext)} bytes)")

            run = st.button("🔒 Encrypt with AES-128-CBC", use_container_width=True)

    with col_output:
        with zone_output():
            st.markdown("#### Live output")
            if run:
                result = encrypt_aes_cbc(plaintext)
                dec = decrypt_aes_cbc(result["ciphertext"], result["key"], result["iv"])

                ss["aes_key"] = result["key"]
                ss["aes_iv"] = result["iv"]
                ss["aes_ciphertext"] = result["ciphertext"]
                ss["aes_plaintext"] = plaintext

                st.metric("Encryption time", f"{result['elapsed_ms']:.3f} ms")
                c1, c2 = st.columns(2)
                with c1:
                    st.caption("Key (hex)")
                    st.code(result["key"].hex(), language=None)
                    st.caption("IV (hex)")
                    st.code(result["iv"].hex(), language=None)
                with c2:
                    st.caption(f"Ciphertext ({len(result['ciphertext'])} bytes, hex, truncated)")
                    st.code(result["ciphertext"].hex()[:200] + "...", language=None)

                match = dec["plaintext"] == plaintext
                st.success("Decrypted output matches original plaintext ✅") if match else \
                    st.error("Mismatch on decrypt ❌")

                # Benchmark across standard sizes, mirroring the original README table
                st.markdown("##### Benchmark across payload sizes")
                datasets = {
                    "1 KB": get_sample_report("1kb"),
                    "100 KB": get_sample_report("100kb"),
                    "1 MB": get_sample_report("1mb"),
                }
                timings = benchmark_cipher(lambda d: encrypt_aes_cbc(d), datasets)
                st.bar_chart(timings)
            elif "aes_ciphertext" in ss:
                st.caption("Last run:")
                st.code(ss["aes_ciphertext"].hex()[:200] + "...", language=None)
            else:
                st.caption("Click Encrypt to see live output here.")

    explanation(
        "AES-CBC XORs each 16-byte block with the previous ciphertext block before "
        "encrypting it, which is why identical plaintext blocks don't produce identical "
        "ciphertext. Compare this against ECB mode to see why that matters visually.",
        related_card_id="ecb_vs_cbc",
    )
