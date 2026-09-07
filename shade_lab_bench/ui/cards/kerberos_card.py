import streamlit as st

from core.auth import simulate_kerberos


def render_kerberos(ss):
    from ui.layout import explanation, zone_controls, zone_output
    left, right = st.columns([1, 2])
    with left, zone_controls():
        st.markdown("#### Controls")
        client = st.text_input("Client", "Dr. Sender")
        service = st.text_input("Service", "HospitalRecordServer")
        run = st.button("🎫 Run ticket exchange", use_container_width=True)
    with right, zone_output():
        st.markdown("#### Live output")
        if run:
            result = simulate_kerberos(client, service)
            ss["kerberos_stage"] = result["ticket"]
            st.metric("TGT / service ticket", f"{len(result['tgt'])} B / {len(result['service_ticket'])} B")
            st.success(f"Access granted to {result['ticket']['client']} ✅" if result["access_granted"] else "Access denied ❌")
            st.json({k: v for k, v in result["ticket"].items() if k != "session_key"})
        else: st.caption("The server receives an encrypted service ticket, not the client password.")
    explanation("Kerberos avoids sending passwords by using short-lived encrypted tickets.", "x509_cert")
