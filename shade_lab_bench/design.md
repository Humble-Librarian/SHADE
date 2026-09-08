# SHADE — Design Document

Status: Living document. Update as decisions change.
Scope: UI/UX architecture for the "Crypto Lab Bench" frontend on top of the existing SHADE cryptography suite.

---

## 1. Background

SHADE (Secure Hospital And Document Exchange) is a Python cryptography demo suite covering symmetric
encryption, hybrid/asymmetric encryption, key exchange, integrity checking, digital signatures, PKI,
and Kerberos — currently exposed only via standalone scripts and an interactive terminal CLI
(`shade_cli.py`) with a stateful `STATE` dict and a dependency guard.

This document defines the **web frontend** built on top of that logic: a Streamlit-based "Lab Bench"
that also borrows the guided narrative from a linear-pipeline concept, so it works for both
first-time learners and people who want to explore concepts out of order.

---

## 2. Chosen Direction: "Crypto Lab Bench" (+ Guided Mode)

- **Primary model:** a dashboard of independent cards, one per cryptographic concept (13 total),
  grouped into 4 layers (Symmetric, Asymmetric/Key Exchange, Integrity, Authentication) — mirroring
  the README's existing Task A–D structure.
- **Secondary model, folded in:** a top-level **Guided / Free** toggle. In Guided mode the
  recommended next card is highlighted and out-of-order cards are dimmed (not blocked). In Free mode
  everything is equally clickable. This gives beginners a path without sacrificing exploration.
- **Dependency graph:** a small sidebar diagram shows which cards feed into which (e.g. AES key →
  Hybrid Encryption; RSA keygen → Signatures). Locked cards show a 🔒 badge with an
  **"Auto-generate for me"** shortcut — a soft version of the CLI's hard dependency guard.
- **Session state:** Streamlit's `st.session_state` replaces the CLI's `STATE` dict — same purpose
  (hold keys/IVs/ciphertexts/certs across steps without redundant disk I/O), scoped per browser
  session instead of per process.

---

## 3. Stack

| Concern | Choice | Why |
|---|---|---|
| UI framework | **Streamlit** | Pure Python, no JS layer, native widgets map onto the card template, `session_state` mirrors CLI's `STATE` dict, renders images/charts natively |
| Crypto | `pycryptodome`, `cryptography` | Already used by the underlying scripts; no change to crypto primitives |
| Charts | `st.bar_chart`, `matplotlib` (via `st.pyplot`) for bit-heatmaps | Built into Streamlit / trivial to embed |
| Graph (dependency map) | `st.graphviz_chart` | Native Streamlit support, no extra frontend |
| Images | `st.image` | Native support, needed for ECB vs CBC BMP card |

Not chosen (for reference): Gradio (poor fit for dashboard-of-cards layout), Flet (heavier layout API,
only worth it later if custom animation becomes a priority), PyQt/Tkinter (no need for desktop-native).

---

## 4. Information Architecture

```
app.py                     Entry point: sidebar + view router
├── Dashboard view         Grid of 13 cards grouped into 4 layers
├── Card Detail view       Opened per-card; same 3-zone template every time
│   ├── Controls zone       Inputs specific to that card (upload / sliders / run button)
│   ├── Visual Output zone  Card-specific visualization (chart / heatmap / diagram / images)
│   └── Explanation strip   Plain-language recap + cross-link to a related card
└── Results Summary view   Replicates CLI option 16: pass/fail list across all 14 checks
```

Sidebar (persistent across views):
- Guided/Free toggle
- Per-layer progress checklist (mirrors CLI's `[✅]/[⬜]`)
- Dependency graph (expander)
- "Run Full Pipeline" (mirrors CLI option 15)
- "Reset All" (mirrors CLI option 17)

---

## 5. Card Registry (single source of truth)

Every card is declared once, in one place (`ui/registry.py`), as metadata — not scattered across the
UI code. This is what drives the dashboard grid, the dependency graph, and the lock/unlock logic.

```python
CardSpec(
    id="aes_cbc",
    title="AES-128 CBC",
    layer="symmetric",
    description="Locks your file so no one but the intended reader can open it.",
    requires=[],                 # ids of prerequisite cards
    produces=["aes_key"],        # session_state keys this card can populate
)
```

Adding a 14th card later means adding one `CardSpec` + one render function — nothing else in the
dashboard/sidebar/graph code needs to change.

---

## 6. Session State Schema

Flat namespace under `st.session_state`, one entry per artifact, e.g.:

```
aes_key, aes_iv, aes_ciphertext
des_key, des_iv, des_ciphertext
rsa_public_key, rsa_private_key
encrypted_aes_key            # RSA-OAEP wrapped AES key
dh_shared_secret_sender, dh_shared_secret_receiver
sha256_original, sha256_recomputed
signature, sender_cert
kerberos_stage                # int, 0-4, for the stepper
card_status                   # dict[card_id] -> "not_started" | "done" | "locked"
```

`card_status` is derived from which other keys are populated — a card is "done" once its `produces`
keys exist in session_state, so status doesn't need to be tracked redundantly.

---

## 7. Why the Backend Logic Must Be Function-Based

(Full rationale already covered in project discussion; summarized here for reference.)

1. Streamlit needs return values to put into `session_state`, not files on disk.
2. Card-based UI needs callable, parameterized units ("encrypt *this* input with *these*
   parameters"), not top-level script execution.
3. Multi-user safety — concurrent Streamlit sessions must not share files like `key.bin`.
4. No change to the underlying cryptography — purely a structural refactor.

Target function convention: every core function takes explicit bytes/params in, returns a **named
dict** (not a tuple) of outputs, e.g. `encrypt_aes_cbc(plaintext, key=None, iv=None) -> dict` with
keys `ciphertext`, `key`, `iv`, `elapsed_ms`.

---

## 8. Per-Card Visual Treatment (reference table)

| Card | Visualization |
|---|---|
| AES / 3-DES | Timing bar chart across 1KB/100KB/1MB |
| Avalanche Effect | Bit-grid heatmap, red = flipped, live % counter |
| ECB vs CBC (Image) | Original / ECB / CBC images side by side |
| RSA Keygen | Public/private key cards with truncated PEM preview |
| Hybrid Encryption | AES key "wrapped" inside a padlock icon (receiver's public key) |
| Diffie-Hellman | Alice/Bob columns, step-by-step number reveal, converging secret |
| MITM Attack | Same as DH, split into 3 columns once "Enable Mallory" is toggled |
| SHA-256 Integrity | Character-level hash diff (green = match, red = mismatch) |
| Tamper Detection | Byte-level before/after view + cascading hash mismatch |
| Digital Signature | Sign/verify checklist, "flip 1 bit" tamper-test button |
| X.509 Certificate | Rendered "ID card" with CN/O/ST/C + validity dates |
| Kerberos SSO | 4-step horizontal stepper, one arrow animates per click |

---

## 9. Implementation Phases

1. **Phase 0 (done in this pass):** `design.md`, `claude.md`, project skeleton, registry, sidebar,
   dashboard shell, session-state pattern, 3 fully working cards (AES, Avalanche, ECB vs CBC) to
   validate the 3-zone template end to end. SHA-256 integrity + tamper detection also wired as
   working cards since they share the same primitives.
2. **Phase 1:** RSA keygen + Hybrid envelope encryption cards.
3. **Phase 2:** Diffie-Hellman + MITM cards (shared DH core, 3-column view).
4. **Phase 3:** Digital signature + X.509 certificate cards.
5. **Phase 4:** Kerberos stepper (structurally different — multi-step protocol, not single
   input→output).
6. **Phase 5:** Full Pipeline runner + Results Summary view, dependency graph polish, "auto-generate
   for me" shortcuts on every locked card.

---

## 10. Open Questions

- Should `session_state` artifacts be exportable to disk (mirroring the original scripts' file
  outputs) as an explicit "Export" action per card, or only at the end via a bundled zip?
- Do we want per-card "reset just this card" in addition to global Reset All?
- Multi-page Streamlit (`st.navigation`) vs. single-page view-swapping via `session_state` — current
  skeleton uses the latter for simplicity; revisit if the app grows large.
