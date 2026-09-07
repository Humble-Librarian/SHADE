import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

from core.asymmetric import generate_rsa_keypair, hybrid_encrypt_decrypt
from core.sample_data import get_sample_report
from core.symmetric import encrypt_aes_cbc


def render_hybrid_encrypt(ss):
    from ui.layout import explanation, zone_controls, zone_output
    left, right = st.columns([1, 2])
    with left, zone_controls():
        st.markdown("#### Controls")
        run = st.button("📦 Wrap AES key with RSA-OAEP", use_container_width=True)
    with right, zone_output():
        st.markdown("#### Live output")
        if run:
            plaintext = ss.get("aes_plaintext", get_sample_report())
            enc = {"key": ss["aes_key"], "iv": ss["aes_iv"], "ciphertext": ss["aes_ciphertext"]} if "aes_ciphertext" in ss else encrypt_aes_cbc(plaintext)
            keys = {"private_key": ss["rsa_private_key"], "public_key": ss["rsa_public_key"]} if "rsa_private_key" in ss else generate_rsa_keypair()
            result = hybrid_encrypt_decrypt(plaintext, enc["key"], enc["iv"], enc["ciphertext"], keys["public_key"], keys["private_key"])
            ss["encrypted_aes_key"] = result["encrypted_aes_key"]
            st.metric("RSA-OAEP envelope", f"{len(result['encrypted_aes_key'])} bytes")
            from ui.theme import get_palette
            pal = get_palette()
            fig, ax = plt.subplots(figsize=(6.8, 1.5))
            fig.patch.set_facecolor(pal["bg_secondary"])
            ax.set_facecolor(pal["bg_secondary"])
            ax.set_xlim(0, 10)
            ax.set_ylim(0, 2)
            ax.axis("off")
            key = FancyBboxPatch((0.55, 0.55), 2.0, 0.85, boxstyle="round,pad=0.08",
                                 facecolor=pal["code_bg"], edgecolor=pal["accent"], linewidth=1.8)
            wrapped = FancyBboxPatch((7.25, 0.55), 2.05, 0.85, boxstyle="round,pad=0.08",
                                     facecolor=pal["bg"], edgecolor=pal["accent"], linewidth=1.8)
            ax.add_patch(key)
            ax.add_patch(wrapped)
            ax.text(1.55, 0.98, "🔑 AES key", ha="center", va="center", fontsize=11, weight="bold",
                    color=pal["text_primary"])
            ax.add_patch(FancyArrowPatch((2.75, 0.98), (6.95, 0.98), arrowstyle="->", mutation_scale=15,
                                         linewidth=2, color=pal["text_secondary"]))
            ax.add_patch(Rectangle((4.57, 1.1), 0.55, 0.43, facecolor=pal["text_secondary"],
                                   edgecolor=pal["border"]))
            ax.add_patch(plt.Circle((4.845, 1.1), 0.28, fill=False, linewidth=2.6, color=pal["border"]))
            ax.text(4.845, 0.45, "RSA-OAEP seals", ha="center", va="center", fontsize=9,
                    color=pal["text_secondary"])
            ax.text(8.275, 0.98, "🔒 Wrapped key", ha="center", va="center", fontsize=10, weight="bold",
                    color=pal["text_primary"])
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
            st.caption("Wrapped AES key (hex, truncated)")
            st.code(result["encrypted_aes_key"].hex()[:200] + "…", language=None)
            st.success("Recovered plaintext matches the original ✅" if result["match"] else "Recovery mismatch ❌")
        else: st.caption("RSA encrypts the small AES key; AES handles the document.")
    explanation("Hybrid encryption combines RSA's secure key exchange with AES's speed for payloads.", "rsa_keygen")
