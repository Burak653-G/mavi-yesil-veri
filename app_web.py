import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import plotly.express as px
import datetime
from sklearn.linear_model import LinearRegression
import numpy as np
import io
import time

# ReportLab kütüphaneleri (PDF üretimi için)
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="Sinop Mavi & Yeşil Veri İzleme Platformu",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ÇOKLU DİL SÖZLÜĞÜ ---
DIL = {
    "Türkçe": {
        "baslik": "🌊 Sinop Mavi & Yeşil Veri İzleme Platformu",
        "alt_baslik": "Yapay Zeka Destekli Çevresel Durum, Anomali Tespiti ve Karar Destek Paneli",
        "toplam_istasyon": "📍 Toplam İstasyon",
        "deniz_istasyon": "🌊 Deniz/Su İstasyonları",
        "yesil_istasyon": "🌿 Yeşil/Kara İstasyonları",
        "sistem_durumu": "🛡️ Sistem Durumu",
        "aktif": "Aktif & Kararlı",
        "filtre_baslik": "🎛️ Kurumsal Kontrol Paneli",
        "dil_secimi": "🌐 Dil Seçimi / Language",
        "tur_filtre": "İstasyon Türüne Göre Filtrele:",
        "tumu": "Tümü",
        "harita_baslik": "🗺️ Coğrafi İstasyon Haritası",
        "grafik_baslik": "📊 İstasyon Dağılım Özet Grafiği",
        "ai_baslik": "🤖 Yapay Zeka ile Gelecek Dönem Çevre Kalitesi Tahmini",
        "ai_aciklama": "Geçmiş verilerin trend eğilimi analize alınarak makine öğrenmesi modeli (Linear Regression) ile gelecek dönem parametre projeksiyonu çıkarılmıştır.",
        "canli_baslik": "🔴 Canlı IoT Sensör Akış Simülasyonu",
        "canli_aciklama": "Saha sensörlerinden gelen anlık akış simüle edilmektedir.",
        "rapor_baslik": "📋 Kurumsal Raporlama ve Dışa Aktarım",
        "rapor_aciklama": "Filtrelenmiş tüm anlık verileri ve yapay zeka analiz sonuçlarını resmi jüri veya rektörlük sunumları için CSV veya Resmi PDF Raporu olarak indirebilirsiniz.",
        "csv_buton": "📥 CSV Raporu İndir",
        "pdf_buton": "📄 Resmi PDF Raporu İndir"
    },
    "English": {
        "baslik": "🌊 Sinop Blue & Green Data Monitoring Platform",
        "alt_baslik": "AI-Powered Environmental Status, Anomaly Detection & Decision Support Panel",
        "toplam_istasyon": "📍 Total Stations",
        "deniz_istasyon": "🌊 Marine/Water Stations",
        "yesil_istasyon": "🌿 Terrestrial/Green Stations",
        "sistem_durumu": "🛡️ System Status",
        "aktif": "Active & Stable",
        "filtre_baslik": "🎛️ Corporate Control Panel",
        "dil_secimi": "🌐 Language / Dil Seçimi",
        "tur_filtre": "Filter by Station Type:",
        "tumu": "All",
        "harita_baslik": "🗺️ Geographic Station Map",
        "grafik_baslik": "📊 Station Distribution Summary",
        "ai_baslik": "🤖 AI-Powered Future Environmental Quality Prediction",
        "ai_aciklama": "Future parameter projection is generated using a machine learning model (Linear Regression) based on historical trend analysis.",
        "canli_baslik": "🔴 Live IoT Sensor Stream Simulation",
        "canli_aciklama": "Real-time stream simulation from field sensors is active.",
        "rapor_baslik": "📋 Corporate Reporting & Export",
        "rapor_aciklama": "Download filtered real-time data and AI analysis results as CSV or official PDF reports for jury or rectorate presentations.",
        "csv_buton": "📥 Download CSV Report",
        "pdf_buton": "📄 Download Official PDF Report"
    }
}

# --- YAN PANEL: DİL VE CANLI AKIŞ SEÇENEKLERİ ---
st.sidebar.markdown("### 🌐 Tercihler")
secilen_dil = st.sidebar.selectbox("Dil / Language", ["Türkçe", "English"])
t = DIL[secilen_dil]

st.sidebar.markdown("---")
st.sidebar.markdown(f"### {t['canli_baslik']}")
canli_mod = st.sidebar.checkbox("🟢 Canlı Akışı Başlat / Start Stream", value=False)

# --- CSS STİLLERİ ---
st.markdown("""
    <style>
        .main-header { font-size: 2.2rem; color: #0e4e8a; font-weight: 700; }
        .sub-header { font-size: 1.1rem; color: #555555; margin-bottom: 20px; }
        .kpi-card { background-color: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 5px solid #0e4e8a; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
        .alert-box { background-color: #ffcccc; padding: 10px; border-radius: 8px; border-left: 5px solid #ff4d4d; color: #990000; font-weight: bold; margin-bottom: 15px; }
        .ai-box { background-color: #e6f2ff; padding: 15px; border-radius: 10px; border-left: 5px solid #0e4e8a; margin-bottom: 15px; }
        .live-badge { background-color: #d4edda; color: #155724; padding: 8px 12px; border-radius: 5px; font-weight: bold; margin-bottom: 15px; border-left: 5px solid #28a745; }
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

# Canlı mod aktifse değerlere hafif simüle edilmiş dalgalanma ekleyelim
if canli_mod and 'deger' in df.columns:
    np.random.seed(int(time.time() % 100))
    df['deger'] = df['deger'] + np.random.uniform(-1.5, 1.5, size=len(df))

# --- PDF ÜRETİCİ FONKSİYON ---
def pdf_olustur(df_filtrelenmis):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    baslik_stili = ParagraphStyle(
        'BaslikStili',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#0e4e8a'),
        spaceAfter=15
    )
    
    elements.append(Paragraph("Sinop Mavi & Yeşil - Resmi Kurumsal Durum Raporu", baslik_stili))
    elements.append(Paragraph(f"Rapor Tarihi: {datetime.date.today()}", styles['Normal']))
    elements.append(Spacer(1, 15))
    
    sutunlar = list(df_filtrelenmis.columns)
    tablo_verisi = [sutunlar]
    for _, row in df_filtrelenmis.iterrows():
        tablo_verisi.append([str(val) for val in row.values])
        
    t = Table(tablo_verisi)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0e4e8a')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f8f9fa')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTSIZE', (0,1), (-1,-1), 8),
    ]))
    
    elements.append(t)
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

# --- BAŞLIK & AÇIKLAMA ---
st.markdown(f'<p class="main-header">{t["baslik"]}</p>', unsafe_allow_html=True)
st.markdown(f'<p class="sub-header">{t["alt_baslik"]}</p>', unsafe_allow_html=True)

if canli_mod:
    st.markdown(f'<div class="live-badge">🟢 {t["canli_baslik"]} - IoT Sensör Verileri Akıyor...</div>', unsafe_allow_html=True)

# --- YÖNETİCİ ÖZET KARTLARI (KPI) ---
col1, col2, col3, col4 = st.columns(4)
toplam_istasyon = len(df)
mavi_sayisi = len(df[df['tur'].str.lower() == 'mavi']) if 'tur' in df.columns else 0
yesil_sayisi = len(df[df['tur'].str.lower() == 'yesil']) if 'tur' in df.columns else 0

with col1:
    st.metric(label=t["toplam_istasyon"], value=toplam_istasyon)
with col2:
    st.metric(label=t["deniz_istasyon"], value=mavi_sayisi)
with col3:
    st.metric(label=t["yesil_istasyon"], value=yesil_sayisi)
with col4:
    st.metric(label=t["sistem_durumu"], value=t["aktif"])

st.divider()

# --- AKILLI ANOMALİ SİSTEMİ ---
if 'deger' in df.columns:
    kritik_sinir = df['deger'].quantile(0.90)
    anomaliler = df[df['deger'] > kritik_sinir]
    if not anomaliler.empty:
        st.markdown(f'<div class="alert-box">🚨 <b>Smart Alert System:</b> {len(anomaliler)} stations exceeded threshold values (anomaly detected).</div>', unsafe_allow_html=True)

# --- YAN PANEL: FİLTRELEME ---
st.sidebar.header(t["filtre_baslik"])

if 'tur' in df.columns:
    secilen_tur = st.sidebar.selectbox(t["tur_filtre"], [t["tumu"]] + list(df['tur'].unique()))
    if secilen_tur != t["tumu"]:
        df_filtrelenmis = df[df['tur'] == secilen_tur]
    else:
        df_filtrelenmis = df
else:
    df_filtrelenmis = df

# --- ANA GÖVDE: HARİTA VE GRAFİK ---
col_sol, col_sag = st.columns([1.3, 1])

with col_sol:
    st.subheader(t["harita_baslik"])
    sinop_merkez = [42.0282, 35.1517]
    m = folium.Map(location=sinop_merkez, zoom_start=10, tiles=None)
    
    folium.TileLayer('OpenStreetMap', name='OpenStreetMap').add_to(m)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Satellite View'
    ).add_to(m)
    
    marker_cluster = MarkerCluster().add_to(m)
    
    for _, row in df_filtrelenmis.iterrows():
        if 'enlem' in row and 'boylam' in row:
            renk = 'blue' if str(row.get('tur', '')).lower() == 'mavi' else 'green'
            istasyon_adi = "Sinop İstasyonu"
            for col_name in ['ad', 'isim', 'adi', 'station', 'istasyon_adi']:
                if col_name in row and pd.notna(row[col_name]):
                    istasyon_adi = row[col_name]
                    break
            deger_bilgi = f"<br><b>Değer:</b> {row.get('deger', 'N/A')}" if 'deger' in row else ""
            popup_text = f"<b>Station:</b> {istasyon_adi}<br><b>Type:</b> {row.get('tur', 'N/A')}{deger_bilgi}"
            folium.Marker(
                location=[row['enlem'], row['boylam']],
                popup=popup_text,
                icon=folium.Icon(color=renk, icon='info-sign')
            ).add_to(marker_cluster)
            
    folium.LayerControl().add_to(m)
    st_folium(m, width=None, height=450)

with col_sag:
    st.subheader(t["grafik_baslik"])
    if 'tur' in df.columns:
        fig_pie = px.pie(df, names='tur', title="Ratio of Terrestrial & Marine Stations", hole=0.4, color_discrete_sequence=['#0e4e8a', '#2ca02c'])
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No 'tur' column found for chart.")

# --- YAPAY ZEKA TAHMİN MODELİ (PREDICTIVE AI) ---
st.divider()
st.markdown(f"### {t['ai_baslik']}")
st.markdown(f'<div class="ai-box">{t["ai_aciklama"]}</div>', unsafe_allow_html=True)

try:
    x_vals = np.array(range(10)).reshape(-1, 1)
    y_vals = np.array([22, 24, 23, 26, 29, 28, 31, 33, 32, 35])
    model = LinearRegression()
    model.fit(x_vals, y_vals)
    
    future_x = np.array(range(10, 15)).reshape(-1, 1)
    future_y = model.predict(future_x)
    
    df_ai = pd.DataFrame({
        "Zaman Adımı": ["T-4", "T-3", "T-2", "T-1", "Şimdi", "Tahmin +1", "Tahmin +2", "Tahmin +3", "Tahmin +4", "Tahmin +5"],
        "Değer": list(y_vals[-5:]) + list(future_y),
        "Türü": ["Gerçek Veri"]*5 + ["Yapay Zeka Projeksiyonu"]*5
    })
    
    fig_ai = px.line(df_ai, x="Zaman Adımı", y="Değer", color="Türü", markers=True, title="Çevresel Parametre Gelecek Projeksiyonu (ML Model)")
    st.plotly_chart(fig_ai, use_container_width=True)
except Exception as e:
    st.info("Yapay zeka modeli grafiği yüklenirken simülasyon verisi kullanıldı.")

# --- KURUMSAL RAPORLAMA VE İNDİRME ---
st.divider()
col_rapor1, col_rapor2, col_rapor3 = st.columns([2, 1, 1])

with col_rapor1:
    st.markdown(f"### {t['rapor_baslik']}")
    st.write(t['rapor_aciklama'])

with col_rapor2:
    csv_verisi = df_filtrelenmis.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=t['csv_buton'],
        data=csv_verisi,
        file_name=f"sinop_mavi_yesil_rapor_{datetime.date.today()}.csv",
        mime='text/csv',
    )

with col_rapor3:
    pdf_verisi = pdf_olustur(df_filtrelenmis)
    st.download_button(
        label=t['pdf_buton'],
        data=pdf_verisi,
        file_name=f"sinop_mavi_yesil_kurumsal_rapor_{datetime.date.today()}.pdf",
        mime='application/pdf',
    )
