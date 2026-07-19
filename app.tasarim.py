import streamlit as st
import pandas as pd
import numpy as np
import time
import os
from datetime import datetime
import plotly.graph_objects as plotly_go

# Özel Modüller
import model_utils
import batarya_kontrol

from ui.styles import load_css
from ui.sidebar import create_sidebar



# --- Sayfa ve UI Yapılandırması ---
st.set_page_config(page_title="Restera Decision Support System", page_icon="⚡", layout="wide")
load_css()

# --- State Yönetimi ---
if 'models' not in st.session_state: st.session_state.models = model_utils.load_models()
if 'soc_history' not in st.session_state: st.session_state.soc_history = []
if 'history_df' not in st.session_state:
    st.session_state.history_df = pd.DataFrame(columns=['Zaman', 'Gerçek_PTF', 'Tahmin_PTF', 'Gerçek_Ruzgar', 'Tahmin_Ruzgar', 'Gerçek_Gunes', 'Tahmin_Gunes'])

# --- Canlı Veri Hazırlığı ---
now = datetime.now()
time_str = now.strftime("%H:%M:%S")

# Anlık Gerçek Veriler
real_soc = round(np.random.uniform(20.1, 79.9), 1)
st.session_state.soc_history.append(real_soc)
if len(st.session_state.soc_history) > 30: st.session_state.soc_history.pop(0)
real_ptf = round(np.random.uniform(1500, 3500), 2)
real_wind = round(np.random.uniform(5, 120), 2)
real_solar = round(np.random.uniform(0, 150) if 6 <= now.hour <= 19 else 0, 2)

# AI Tahminleri
pred_ptf = model_utils.predict_price(st.session_state.models)
error_margin = np.random.uniform(0.70, 1.30) 
pred_wind = round(real_wind * error_margin, 2)
pred_solar = model_utils.predict_solar(st.session_state.models)

# Grafik verisi
new_row = {'Zaman': time_str, 'Gerçek_PTF': real_ptf, 'Tahmin_PTF': pred_ptf, 'Gerçek_Ruzgar': real_wind, 'Tahmin_Ruzgar': pred_wind, 'Gerçek_Gunes': real_solar, 'Tahmin_Gunes': pred_solar}
st.session_state.history_df = pd.concat([st.session_state.history_df, pd.DataFrame([new_row])]).tail(30)

# Karar Motoru
action, reason, warnings = batarya_kontrol.evaluate_system_state(soc=real_soc, ptf=real_ptf, solar=real_solar, wind=real_wind)

# --- Sidebar ---
page = create_sidebar() 

# --- Sayfa İçerik Yapısı (GHOST BOX ÇÖZÜMÜ) ---
page_placeholder = st.empty()

with page_placeholder.container():
    if page == "1. Ana Panel":
        st.markdown("<h2>⚡ Gerçek Zamanlı BESS İzleme</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="metric-card border-blue"><div class="metric-title">Zaman</div><div class="metric-value">{time_str}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-card border-green"><div class="metric-title">Güneş Üretimi (Anlık)</div><div class="metric-value">{real_solar} MW</div></div>', unsafe_allow_html=True)
        with col2:
            soc_color = "border-orange" if real_soc < 30 or real_soc > 75 else "border-green"
            st.markdown(f'<div class="metric-card {soc_color}"><div class="metric-title">Batarya Doluluk (SoC)</div><div class="metric-value">%{real_soc}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-card border-blue"><div class="metric-title">Rüzgâr Üretimi (Anlık)</div><div class="metric-value">{real_wind} MW</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-card border-orange"><div class="metric-title">Piyasa Takas Fiyatı (PTF)</div><div class="metric-value">{real_ptf} ₺</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-card border-green"><div class="metric-title">Sistem Durumu</div><div class="metric-value">Aktif & Kararlı</div></div>', unsafe_allow_html=True)

    elif page == "2. Tahminler":
        st.markdown("<h2>📈 Yapay Zekâ Üretim ve Fiyat Tahminleri</h2>", unsafe_allow_html=True)
        df = st.session_state.history_df
        fig_ptf = plotly_go.Figure()
        fig_ptf.add_trace(plotly_go.Scatter(x=df['Zaman'], y=df['Gerçek_PTF'], mode='lines', name='Gerçek PTF', line=dict(color='#1f77b4', width=3)))
        fig_ptf.add_trace(plotly_go.Scatter(x=df['Zaman'], y=df['Tahmin_PTF'], mode='lines', name='Tahmin PTF', line=dict(color='#ff7f0e', width=3, dash='dash')))
        fig_ptf.update_layout(title="Elektrik Piyasa Takas Fiyatı (TL/MWh)", template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_ptf, width='stretch')

        col1, col2 = st.columns(2)
        with col1:
            fig_wind = plotly_go.Figure()
            fig_wind.add_trace(plotly_go.Scatter(x=df['Zaman'], y=df['Gerçek_Ruzgar'], mode='lines', fill='tozeroy', name='Gerçek Rüzgar', line=dict(color='#2ca02c')))
            fig_wind.add_trace(plotly_go.Scatter(x=df['Zaman'], y=df['Tahmin_Ruzgar'], mode='lines', name='Tahmin Rüzgar', line=dict(color='#ffffff', dash='dot')))
            fig_wind.update_layout(title="Rüzgâr Üretimi (MW)", template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_wind, width='stretch')
        with col2:
            fig_solar = plotly_go.Figure()
            fig_solar.add_trace(plotly_go.Scatter(x=df['Zaman'], y=df['Gerçek_Gunes'], mode='lines', fill='tozeroy', name='Gerçek Güneş', line=dict(color='#ff7f0e')))
            fig_solar.add_trace(plotly_go.Scatter(x=df['Zaman'], y=df['Tahmin_Gunes'], mode='lines', name='Tahmin Güneş', line=dict(color='#ffffff', dash='dot')))
            fig_solar.update_layout(title="Güneş Üretimi (MW)", template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_solar, width='stretch')

    elif page == "3. Arbitraj":
        st.markdown("<h2>💰 Karar Destek Motoru ve Arbitraj</h2>", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 2])
        with col1:
            ac_class = "action-bekle"
            if "AL" in action: ac_class = "action-al"
            elif "SAT" in action: ac_class = "action-sat"
            st.markdown(f'<div class="action-box {ac_class}">SİSTEM ÖNERİSİ<br><span style="font-size:2.5rem;">{action}</span></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card border-blue" style="height: 145px;"><div class="metric-title">Yapay Zeka Karar Gerekçesi</div><div style="font-size: 1.2rem; margin-top:10px;">{reason}</div></div>', unsafe_allow_html=True)
        

    elif page == "4. Batarya Sağlığı":
        st.markdown("<h2>🔋 BMS (Battery Management System) Sağlık Durumu</h2>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            fig_soc = plotly_go.Figure(plotly_go.Indicator(mode = "gauge+number", value = real_soc, title = {'text': "SoC (Doluluk Oranı) %"}, gauge = {'axis': {'range': [None, 100]}, 'bar': {'color': "#2ca02c"}}))
            fig_soc.update_layout(template="plotly_dark", height=300)
            st.plotly_chart(fig_soc, width='stretch')
            st.markdown("### 📊 SoC Zaman İçindeki Değişimi")
            fig_trend = plotly_go.Figure()
            fig_trend.add_trace(plotly_go.Scatter(y=st.session_state.soc_history, mode='lines+markers', name='SoC Trend', line=dict(color='#2ca02c', width=3), fill='tozeroy'))
            fig_trend.update_layout(template="plotly_dark", height=300, yaxis=dict(range=[0, 100]))
            st.plotly_chart(fig_trend, width='stretch')
        with col2:
            temp = round(np.random.uniform(25, 38), 1)
            fig_temp = plotly_go.Figure(plotly_go.Indicator(mode = "gauge+number", value = temp, number = {'suffix': " °C"}, title = {'text': "Batarya Hücre Sıcaklığı"}, gauge = {'axis': {'range': [None, 60]}, 'bar': {'color': "#ff7f0e"}}))
            fig_temp.update_layout(template="plotly_dark", height=300)
            st.plotly_chart(fig_temp, width='stretch')
            st.markdown(f'<div class="metric-card border-blue"><div class="metric-title">Toplam Çevrim (Cycle) Sayısı</div><div class="metric-value">{np.random.randint(150, 500)} Döngü</div></div>', unsafe_allow_html=True)
            state = "Deşarj (Satış)" if "SAT" in action else "Şarj (Depolama)" if "AL" in action else "Idle (Bekleme)"
            st.markdown(f'<div class="metric-card border-green"><div class="metric-title">Fiziksel Konum</div><div class="metric-value">{state}</div></div>', unsafe_allow_html=True)

    elif page == "5. Sistem Uyarıları":
        st.markdown("<h2>🚨 Gerçek Zamanlı Uyarı ve İkaz Merkezi</h2>", unsafe_allow_html=True)
        if len(warnings) == 0:
            st.success("Bütün sistemler sorunsuz çalışıyor.")
        else:
            for w in warnings:
                st.markdown(f'<div class="warning-card">{w}</div>', unsafe_allow_html=True)

time.sleep(5)
st.rerun()