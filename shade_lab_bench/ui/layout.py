"""
Shared layout pieces: sidebar (progress + guided/free toggle + dependency
graph + reset), dashboard grid, and the 3-zone card template every card
render function uses (Controls / Visual Output / Explanation strip).
"""

import streamlit as st

from ui.registry import CARDS, LAYER_LABELS, LAYER_ORDER, cards_in_layer
from ui.state import card_status, open_card, open_dashboard, open_summary, reset_all

STATUS_ICON = {"done": "✅", "locked": "🔒", "not_started": "⬜"}


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

def render_sidebar():
    with st.sidebar:
        st.markdown("## 🏥 SHADE Lab Bench")
        st.caption("Secure Hospital And Document Exchange")

        if st.button("🏠 Dashboard", use_container_width=True):
            open_dashboard()
            st.rerun()

        st.session_state.guided_mode = st.toggle(
            "Guided mode", value=st.session_state.guided_mode,
            help="Highlights the recommended next card instead of leaving everything equally weighted."
        )

        st.divider()
        st.markdown("#### Progress")
        for layer in LAYER_ORDER:
            cards = cards_in_layer(layer)
            done_count = sum(1 for c in cards if card_status(c) == "done")
            st.caption(f"{LAYER_LABELS[layer]}  ({done_count}/{len(cards)})")
            icons = " ".join(STATUS_ICON[card_status(c)] for c in cards)
            st.markdown(icons)

        st.divider()
        with st.expander("🕸️ Dependency graph"):
            st.graphviz_chart(_build_dependency_graph())

        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 Summary", use_container_width=True):
                open_summary()
                st.rerun()
        with col2:
            if st.button("🔄 Reset All", use_container_width=True):
                reset_all()
                st.rerun()


def _build_dependency_graph() -> str:
    from ui.theme import contrasting_text, get_palette

    p = get_palette()
    fill = {
        "done": p["accent"],
        "locked": p["border"],
        "not_started": p["bg"],
    }
    font = {k: contrasting_text(v) for k, v in fill.items()}

    lines = [
        "digraph {",
        "rankdir=LR;",
        f'bgcolor="{p["bg_secondary"]}";',
        f'node [shape=box, style="filled,rounded", fontsize=10, '
        f'color="{p["border"]}", fontname="Inter"];',
        f'edge [color="{p["text_secondary"]}"];',
    ]
    for card in CARDS:
        status = card_status(card)
        lines.append(
            f'"{card.id}" [label="{card.title}", fillcolor="{fill[status]}", '
            f'fontcolor="{font[status]}"];'
        )
        for req in card.requires:
            lines.append(f'"{req}" -> "{card.id}";')
    lines.append("}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Dashboard grid
# ---------------------------------------------------------------------------

def render_dashboard():
    st.title("🏥 SHADE — Crypto Lab Bench")
    st.caption(
        "An interactive cryptography suite for hospital EMR exchange. "
        "Pick a card below, or follow the highlighted suggestion in Guided mode."
    )

    suggested_id = _suggested_next_card_id() if st.session_state.guided_mode else None

    for layer in LAYER_ORDER:
        st.markdown(f"### {LAYER_LABELS[layer]}")
        cards = cards_in_layer(layer)
        cols = st.columns(4)
        for i, card in enumerate(cards):
            with cols[i % 4]:
                _render_card_tile(card, highlighted=(card.id == suggested_id))
        st.write("")

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶ Run Full Pipeline", use_container_width=True,
                      help="Runs every implemented card end to end, then shows the results summary."):
            from ui.pipeline import run_full_pipeline
            with st.spinner("Running all 13 cards..."):
                run_full_pipeline(st.session_state)
            open_summary()
            st.rerun()
    with col2:
        if st.button("📋 Show Results Summary", use_container_width=True):
            open_summary()
            st.rerun()


def _suggested_next_card_id():
    for card in CARDS:
        status = card_status(card)
        if status == "not_started" and card.render is not None:
            return card.id
    return None


def _render_card_tile(card, highlighted: bool):
    status = card_status(card)
    icon = STATUS_ICON[status]
    border_note = "🟢 **Start here**" if highlighted else ""

    with st.container(border=True):
        st.markdown(f"**{icon} {card.title}**")
        st.caption(card.description)
        if border_note:
            st.markdown(border_note)

        if card.render is None:
            st.button("Coming soon", key=f"open_{card.id}", disabled=True, use_container_width=True)
        elif status == "locked":
            missing = [r for r in card.requires if card_status(_by_id(r)) != "done"]
            st.caption(f"Needs: {', '.join(_by_id(r).title for r in missing)}")
            if st.button("Open anyway", key=f"open_{card.id}", use_container_width=True):
                open_card(card.id)
                st.rerun()
        else:
            label = "Reopen" if status == "done" else "Open"
            if st.button(label, key=f"open_{card.id}", use_container_width=True):
                open_card(card.id)
                st.rerun()


def _by_id(card_id):
    from ui.registry import CARDS_BY_ID
    return CARDS_BY_ID[card_id]


# ---------------------------------------------------------------------------
# Card detail: shared 3-zone template
# ---------------------------------------------------------------------------

def render_card_detail(card):
    if st.button("← Back to bench"):
        open_dashboard()
        st.rerun()

    st.title(card.title)
    st.caption(card.description)

    status = card_status(card)
    if status == "locked":
        missing = [_by_id(r).title for r in card.requires if card_status(_by_id(r)) != "done"]
        st.warning(
            f"This card normally needs: {', '.join(missing)}. "
            "You can still run it below -- missing inputs will be generated automatically."
        )

    st.divider()
    card.render(st.session_state)


def zone_controls():
    return st.container(border=True)


def zone_output():
    return st.container(border=True)


def explanation(text: str, related_card_id: str = None):
    st.info(text)
    if related_card_id:
        related = _by_id(related_card_id)
        if st.button(f"→ Try: {related.title}", key=f"crosslink_{related_card_id}"):
            open_card(related_card_id)
            st.rerun()
