"""
Single source of truth for every card in the Lab Bench. The dashboard grid,
sidebar progress checklist, and dependency graph are all driven off this list
-- see claude.md rule #4. Do not hand-wire new cards into app.py.

Cards whose `render` is None are declared but not yet implemented (Phase 1+).
They still appear on the dashboard, greyed out with a "Coming soon" badge,
so the full 13-card map is visible from day one.
"""

from dataclasses import dataclass, field
from typing import Callable, Optional


@dataclass
class CardSpec:
    id: str
    title: str
    layer: str            # "symmetric" | "asymmetric" | "integrity" | "auth"
    description: str
    requires: list = field(default_factory=list)   # ids of prerequisite cards
    produces: list = field(default_factory=list)    # session_state keys this card fills
    render: Optional[Callable] = None                # render_<id>(ss) function, or None


LAYER_LABELS = {
    "symmetric": "Layer 1 — Symmetric Encryption",
    "asymmetric": "Layer 2 — Asymmetric & Key Exchange",
    "integrity": "Layer 3 — Integrity",
    "auth": "Layer 4 — Authentication",
}

LAYER_ORDER = ["symmetric", "asymmetric", "integrity", "auth"]


def _load_cards():
    # Local imports to avoid circular imports between registry and card modules.
    from ui.cards.aes_card import render_aes_cbc
    from ui.cards.des_card import render_des_cbc
    from ui.cards.avalanche_card import render_avalanche
    from ui.cards.ecb_cbc_card import render_ecb_vs_cbc
    from ui.cards.integrity_card import render_sha256_integrity
    from ui.cards.tamper_card import render_tamper_detection
    from ui.cards.rsa_card import render_rsa_keygen
    from ui.cards.hybrid_card import render_hybrid_encrypt
    from ui.cards.dh_card import render_diffie_hellman
    from ui.cards.mitm_card import render_mitm
    from ui.cards.signature_card import render_digital_signature
    from ui.cards.cert_card import render_x509_cert
    from ui.cards.kerberos_card import render_kerberos

    return [
        CardSpec(
            id="aes_cbc", title="AES-128 CBC", layer="symmetric",
            description="Locks your file so no one but the intended reader can open it.",
            produces=["aes_key", "aes_iv", "aes_ciphertext", "aes_plaintext"],
            render=render_aes_cbc,
        ),
        CardSpec(
            id="des_cbc", title="3-DES CBC", layer="symmetric",
            description="An older, slower symmetric cipher -- compare its speed against AES.",
            produces=["des_key", "des_iv", "des_ciphertext", "des_plaintext"],
            render=render_des_cbc,
        ),
        CardSpec(
            id="avalanche", title="Avalanche Effect", layer="symmetric",
            description="Flip one bit of plaintext and watch how much of the ciphertext changes.",
            requires=["aes_cbc"],
            produces=["avalanche_result"],
            render=render_avalanche,
        ),
        CardSpec(
            id="ecb_vs_cbc", title="ECB vs CBC (Image)", layer="symmetric",
            description="Encrypt an image two ways and see why ECB mode leaks visual patterns.",
            produces=["ecb_output_bmp", "cbc_output_bmp"],
            render=render_ecb_vs_cbc,
        ),
        CardSpec(
            id="rsa_keygen", title="RSA-2048 Keygen", layer="asymmetric",
            description="Generate a public/private key pair for asymmetric encryption.",
            produces=["rsa_public_key", "rsa_private_key"],
            render=render_rsa_keygen,
        ),
        CardSpec(
            id="hybrid_encrypt", title="Hybrid Envelope Encryption", layer="asymmetric",
            description="Wrap an AES session key with RSA so only the receiver can unlock it.",
            requires=["aes_cbc", "rsa_keygen"],
            produces=["encrypted_aes_key"],
            render=render_hybrid_encrypt,
        ),
        CardSpec(
            id="diffie_hellman", title="Diffie-Hellman Exchange", layer="asymmetric",
            description="Two parties agree on a shared secret without ever sending it.",
            produces=["dh_shared_secret"],
            render=render_diffie_hellman,
        ),
        CardSpec(
            id="mitm", title="MITM Attack Simulation", layer="asymmetric",
            description="Watch an eavesdropper defeat unauthenticated Diffie-Hellman.",
            requires=["diffie_hellman"],
            produces=["mitm_secrets"],
            render=render_mitm,
        ),
        CardSpec(
            id="sha256_integrity", title="SHA-256 Integrity", layer="integrity",
            description="Fingerprint a document so any change to it can be detected.",
            produces=["sha256_original"],
            render=render_sha256_integrity,
        ),
        CardSpec(
            id="tamper_detection", title="Tamper Detection", layer="integrity",
            description="Corrupt a ciphertext in transit and watch the integrity check catch it.",
            requires=["aes_cbc", "sha256_integrity"],
            produces=["tampered_ciphertext"],
            render=render_tamper_detection,
        ),
        CardSpec(
            id="digital_signature", title="Digital Signature", layer="auth",
            description="Prove who sent a document and that it wasn't altered.",
            requires=["rsa_keygen", "sha256_integrity"],
            produces=["signature"],
            render=render_digital_signature,
        ),
        CardSpec(
            id="x509_cert", title="X.509 Certificate", layer="auth",
            description="Bind an identity to a public key, the way HTTPS certificates work.",
            requires=["rsa_keygen"],
            produces=["sender_certificate"],
            render=render_x509_cert,
        ),
        CardSpec(
            id="kerberos", title="Kerberos SSO", layer="auth",
            description="Walk through a 4-step ticket-granting single sign-on exchange.",
            produces=["kerberos_stage"],
            render=render_kerberos,
        ),
    ]


CARDS = _load_cards()
CARDS_BY_ID = {c.id: c for c in CARDS}


def cards_in_layer(layer: str):
    return [c for c in CARDS if c.layer == layer]
