import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import plotly.express as px
import datetime

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="Sinop Mavi & Yeşil Veri İzleme Platformu",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS İLE ÖZEL STİL ---
st.markdown("""
    <style>
        .main-header { font-size: 2.2rem; color: #0e4e8a; font-weight: 700; }
        .sub-header { font-size: 1.1rem; color: #555555; margin-bottom: 20px; }
        .kpi-card { background-color: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 5px solid #0e4e8a; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
        .alert-box { background-color: #ffcccc; padding: 10px; border-radius: 8px; border-left: 5px solid #ff4d4d; color: #990000; font-weight: bold; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

# --- VERİ YÜKLEME ---
@st.cache_data
def data_yukle():
    return pd.read_csv("veri.csv")

try:
    df = data_yukle()
except Exception as e:
    st.error(f"Veri yüklenirken hata oluştu: {e}")
    st.stop()

# --- BAŞLIK & AÇIKLAMA ---
st.markdown('<p class="main-header">🌊 Sinop Mavi & Yeşil Veri İzleme Platformu</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Gelişmiş Çevresel Durum, Akıllı Anomali Tespiti ve Karar Destek Paneli | Kurumsal Sürüm</p>', unsafe_allow_html=True)

# --- YÖNETİCİ ÖZET KARTLARI (KPI METRİKLERİ) ---
col1, col2, col3, col4 = st.columns(4)
toplam_istasyon = len(df)
mavi_sayisi = len(df[df['tur'].str.lower() == 'mavi']) if 'tur' in df.columns else 0
yesil_sayisi = len(df[df['tur'].str.lower() == 'yesil']) if 'tur' in df.columns else 0

with col1:
    st.metric(label="📍 Toplam İstasyon", value=toplam_istasyon)
with col2:
    st.metric(label="🌊 Deniz/Su İstasyonları", value=mavi_sayisi)
with col3:
    st.metric(label="🌿 Yeşil/Kara İstasyonları", value=yesil_sayisi)
with col4:
    st.metric(label="🛡️ Sistem Durumu", value="Aktif & Kararlı")

st.divider()

# --- AKILLI ANOMALİ & UYARI MEKANİZMASI ---
if 'deger' in df.columns:
    kritik_sinir = df['deger'].quantile(0.90)
    anomaliler = df[df['deger'] > kritik_sinir]
    if not anomaliler.empty:
        st.markdown(f'<div class="alert-box">🚨 <b>Akıllı Uyarı Sistemi:</b> {len(anomaliler)} istasyonda eşik değer aşımı (anomali) tespit edildi. Bölgesel inceleme önerilir.</div>', unsafe_allow_html=True)

# --- YAN PANEL: FİLTRELEME ---
st.sidebar.header("🎛️ Veri Filtreleme Paneli")

if 'tur' in df.columns:
    secilen_tur = st.sidebar.selectbox("İstasyon Türüne Göre Filtrele:", ["Tümü"] + list(df['tur'].unique()))
    if secilen_tur != "Tümü":
        df_filtrelenmis = df[df['tur'] == secilen_tur]
    else:
        df_filtrelenmis = df
else:
    df_filtrelenmis = df

# --- ANA GÖVDE: HARİTA VE GRAFİKLER ---
col_sol, col_sag = st.columns([1.3, 1])

with col_sol:
    st.subheader("🗺️ Coğrafi İstasyon Haritası")
    
    sinop_merkez = [42.0282, 35.1517]
    m = folium.Map(location=sinop_merkez, zoom_start=10, tiles=None)
    
    folium.TileLayer('OpenStreetMap', name='OpenStreetMap').add_to(m)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Uydu Görünümü'
    ).add_to(m)
    
    marker_cluster = MarkerCluster().add_to(m)
    
    for _, row in df_filtrelenmis.iterrows():
        if 'enlem' in row and 'boylam' in row:
            renk = 'blue' if str(row.get('tur', '')).lower() == 'mavi' else 'green'
            popup_text = f"<b>İstasyon:</b> {row.get('ad', 'Bilinmiyor')}<br><b>Tür:</b> {row.get('tur', 'Belirtilmedi')}"
            folium.Marker(
                location=[row['enlem'], row['boylam']],
                popup=popup_text,
                icon=folium.Icon(color=renk, icon='info-sign')
            ).add_to(marker_cluster)
            
    folium.LayerControl().add_to(m)
    st_folium(m, width=None, height=450)

with col_sag:
    st.subheader("📊 İstasyon Dağılım Özet Grafiği")
    if 'tur' in df.columns:
        fig_pie = px.pie(df, names='tur', title="Kara ve Deniz İstasyon Oranı", hole=0.4, color_discrete_sequence=['#0e4e8a', '#2ca02c'])
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("Grafik için uygun 'tur' sütunu bulunamadı.")

# --- ZAMAN SERİSİ & TREND ANALİZİ ---
st.divider()
st.subheader("📈 Zaman Serisi & Çevresel Trend Analizi")
if 'tarih' in df.columns and 'deger' in df.columns:
    fig_line = px.line(df, x='tarih', y='deger', color='tur' if 'tur' in df.columns else None, title="Parametrelerin Zaman İçindeki Değişim Eğilimi")
    st.plotly_chart(fig_line, use_container_width=True)
else:
    tarih_ornek = pd.date_range(start="2026-01-01", periods=10, freq="D")
    df_trend = pd.DataFrame({"Tarih": tarih_ornek, "Değer": [20, 24, 19, 28, 35, 30, 25, 22, 29, 32], "Parametre": "Genel Çevre Kalite İndeksi"})
    fig_trend = px.line(df_trend, x="Tarih", y="Değer", markers=True, title="Çevresel Kalite İndeksi Eğilim Analizi (Simüle Edilmiş Trend)")
    st.plotly_chart(fig_trend, use_container_width=True)

# --- OTOMATİK RAPORLAMA / İNDİRME ÖZELLİĞİ ---
st.divider()
col_rapor1, col_rapor2 = st.columns([3, 1])
with col_rapor1:
    st.markdown("### 📋 Kurumsal Raporlama ve Dışa Aktarım")
    st.write("Filtrelenmiş tüm anlık verileri ve analiz sonuçlarını resmi jüri veya rektörlük sunumları için CSV formatında indirebilirsiniz.")
with col_rapor2:
    csv_verisi = df_filtrelenmis.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Resmi Raporu İndir (CSV)",
        data=csv_verisi,
        file_name=f"sinop_mavi_yesil_rapor_{datetime.date.today()}.csv",
        mime='text/csv',
    )
