import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from core.integrity import compute_sha256, tamper_bytes, verify_integrity
from core.sample_data import get_sample_report
from core.symmetric import decrypt_aes_cbc, encrypt_aes_cbc


def render_tamper_detection(ss):
    from ui.layout import explanation, zone_controls, zone_output
    plaintext = ss.get("aes_plaintext") or get_sample_report("default")

    if "aes_ciphertext" in ss:
        ciphertext, key, iv = ss["aes_ciphertext"], ss["aes_key"], ss["aes_iv"]
    else:
        enc = encrypt_aes_cbc(plaintext)
        ciphertext, key, iv = enc["ciphertext"], enc["key"], enc["iv"]

    original_hash = ss.get("sha256_original") or compute_sha256(plaintext)

    col_controls, col_output = st.columns([1, 2])

    with col_controls:
        with zone_controls():
            st.markdown("#### Controls")
            st.caption(f"Ciphertext: {len(ciphertext)} bytes")
            byte_a = st.slider("Byte position to corrupt (#1)", 0, len(ciphertext) - 1, 10)
            byte_b = st.slider("Byte position to corrupt (#2)", 0, len(ciphertext) - 1,
                                min(50, len(ciphertext) - 1))
            run = st.button("🚨 Simulate MITM tampering", use_container_width=True)

    with col_output:
        with zone_output():
            st.markdown("#### Live output")
            if run:
                tamper_result = tamper_bytes(ciphertext, [(byte_a, 0xFF), (byte_b, 0xAA)])
                tampered = tamper_result["tampered"]
                ss["tampered_ciphertext"] = tampered

                try:
                    dec = decrypt_aes_cbc(tampered, key, iv)
                    tampered_plaintext = dec["plaintext"]
                    check = verify_integrity(tampered_plaintext, original_hash)
                    tampered_hash = check["actual_hash"]
                except (ValueError, KeyError):
                    # Padding can break entirely depending on which byte was flipped --
                    # that's itself a valid, visible symptom of tampering.
                    tampered_hash = None
                    check = {"match": False}

                # Static transit illustration: ciphertext is intercepted before receipt.
                from ui.theme import get_palette
                pal = get_palette()
                fig, ax = plt.subplots(figsize=(7.2, 1.55))
                fig.patch.set_facecolor(pal["bg_secondary"])
                ax.set_facecolor(pal["bg_secondary"])
                ax.set_xlim(0, 10)
                ax.set_ylim(0, 2)
                ax.axis("off")
                envelope = FancyBboxPatch((0.45, 0.55), 1.75, 0.9, boxstyle="round,pad=0.08",
                                          facecolor=pal["code_bg"], edgecolor=pal["accent"], linewidth=1.8)
                receiver = FancyBboxPatch((7.75, 0.45), 1.75, 1.1, boxstyle="round,pad=0.08",
                                          facecolor=pal["bg"], edgecolor=pal["border"], linewidth=2)
                ax.add_patch(envelope)
                ax.add_patch(receiver)
                ax.text(1.325, 1.0, "✉\nSealed", ha="center", va="center", fontsize=11, weight="bold",
                        color=pal["text_primary"])
                ax.add_patch(FancyArrowPatch((2.35, 1), (7.5, 1), arrowstyle="->", mutation_scale=15,
                                             linewidth=2, color=pal["text_secondary"]))
                ax.text(5, 1.3, "☝", ha="center", va="center", fontsize=24, color=pal["accent"])
                ax.text(5, 0.6, "intercepted", ha="center", va="center", fontsize=9,
                        color=pal["text_secondary"])
                ax.text(8.625, 1.0, "Receiver\n✕", ha="center", va="center", fontsize=11,
                        weight="bold", color=pal["text_primary"])
                st.pyplot(fig, use_container_width=True)
                plt.close(fig)

                c1, c2 = st.columns(2)
                with c1:
                    st.caption("Expected SHA-256 (original)")
                    st.code(original_hash, language=None)
                with c2:
                    st.caption("Calculated SHA-256 (tampered)")
                    st.code(tampered_hash or "(decryption failed — padding corrupted)", language=None)

                if check["match"]:
                    st.success("Integrity verified — no tampering detected")
                else:
                    st.error("🚨 ALERT: Hash mismatch — tampering detected! Document rejected.")
            elif "tampered_ciphertext" in ss:
                st.caption("Last run produced a tampered ciphertext — press the button again to re-run.")
            else:
                st.caption("Click the button to corrupt the ciphertext and watch detection happen.")

    explanation(
        "Flipping even a couple of bytes in the ciphertext cascades into a completely "
        "different decrypted plaintext (thanks to CBC chaining), which produces a totally "
        "different SHA-256 hash — an unmistakable, cheap-to-check tampering signal.",
        related_card_id="sha256_integrity",
    )
