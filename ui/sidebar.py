import streamlit as st

def create_sidebar():
    st.sidebar.markdown(
        "<h2 style='text-align:center;color:#4CAF50;'>⚡ RESTERA AI</h2>",
        unsafe_allow_html=True
    )

    page = st.sidebar.radio(
        "Sayfalar",
        [
            "1. Ana Panel",
            "2. Tahminler",
            "3. Arbitraj",
            "4. Batarya Sağlığı",
            "5. Sistem Uyarıları"
        ]
    )

    st.sidebar.markdown("---")
    
    return page