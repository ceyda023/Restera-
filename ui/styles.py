import streamlit as st


def load_css():

    st.markdown("""
    <style>

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
        background-color: #0e1117;
        color: #e0e0e0;
    }

    .metric-card{
        background-color:#1e2130;
        border-radius:12px;
        padding:20px;
        box-shadow:0 4px 15px rgba(0,0,0,.3);
        margin-bottom:20px;
        border-left:5px solid #1f77b4;
    }

    .border-green{
        border-left-color:#2ca02c!important;
    }

    .border-orange{
        border-left-color:#ff7f0e!important;
    }

    .border-blue{
        border-left-color:#1f77b4!important;
    }

    .metric-title{
        font-size:1rem;
        color:#8c92a5;
        margin-bottom:8px;
        font-weight:600;
    }

    .metric-value{
        font-size:2rem;
        font-weight:bold;
        color:white;
    }

    .action-box{
        padding:25px;
        border-radius:15px;
        text-align:center;
        font-weight:bold;
        font-size:1.5rem;
        margin-bottom:15px;
    }

    .action-al{
        background:rgba(44,160,44,.2);
        color:#2ca02c;
        border:2px solid #2ca02c;
    }

    .action-sat{
        background:rgba(255,127,14,.2);
        color:#ff7f0e;
        border:2px solid #ff7f0e;
    }

    .action-bekle{
        background:rgba(31,119,180,.2);
        color:#1f77b4;
        border:2px solid #1f77b4;
    }

    .warning-card{
        background:rgba(255,69,58,.1);
        border:1px solid #ff453a;
        color:#ff453a;
        padding:15px;
        border-radius:8px;
        margin-bottom:10px;
        font-weight:600;
    }

    </style>
    """, unsafe_allow_html=True)