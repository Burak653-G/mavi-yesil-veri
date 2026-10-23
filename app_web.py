import streamlit as st
import folium
import pandas as pd
from streamlit_folium import st_folium
import plotly.express as px

# Sayfa yapılandırması (Geniş ekran modu)
st.set_page_config(page_title="Sinop Mavi & Yeşil Veri Platformu", layout="wide")

st.title("🌊🌿 Sinop Mavi & Yeşil Veri İzleme Platformu")
st.markdown("**Gelişmiş Çevresel Durum, İstasyon Analiz ve Filtreleme Paneli** | Sistem Durumu: Aktif ve Kararlı")

# CSV dosyasından verilerimizi okuyoruz
veri = pd.read_csv("veri.csv")

# ----------------- YAN MENÜ (FİLTRELEME PANELİ) -----------------
st.sidebar.header("🔍 Veri Filtreleme Paneli")
secilen_tur = st.sidebar.selectbox(
    "İstasyon Türüne Göre Filtrele:",
    ["Tümü", "Yeşil Kara İstasyonları", "Mavi Deniz İstasyonları"]
)

# Filtreleme mantığı
if secilen_tur == "Yeşil Kara İstasyonları":
    filtrelenmis_veri = veri[veri["tur"] == "yesil"]
elif secilen_tur == "Mavi Deniz İstasyonları":
    filtrelenmis_veri = veri[veri["tur"] == "mavi"]
else:
    filtrelenmis_veri = veri

sinop_enlem = 42.0231
sinop_boylam = 35.1531

# Harita Oluşturma
m = folium.Map(location=[sinop_enlem, sinop_boylam], zoom_start=11, tiles="OpenStreetMap", name="Sokak Haritasi")
folium.TileLayer(
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attr="Esri",
    name="Uydu Gorunumu"
).add_to(m)

yesil_grup = folium.FeatureGroup(name="🌿 Yesil Veri Noktalari").add_to(m)
mavi_grup = folium.FeatureGroup(name="💧 Mavi Veri Noktalari").add_to(m)

# Filtrelenmiş verileri haritaya ekleme
for index, row in filtrelenmis_veri.iterrows():
    isim = row["isim"]
    enlem = row["enlem"]
    boylam = row["boylam"]
    tur = row["tur"]
    detay = row["detay"]
    
    if tur == "yesil":
        icon_name = "leaf"
        icon_color = "green"
        badge_bg = "#d4edda"
        badge_color = "#155724"
    else:
        icon_name = "tint"
        icon_color = "blue"
        badge_bg = "#cce5ff"
        badge_color = "#004085"
        
    popup_html = f"""
    <div style="font-family: Arial, sans-serif; width: 220px; padding: 5px;">
        <h4 style="margin: 0 0 8px 0; color: #2c3e50; border-bottom: 2px solid {icon_color}; padding-bottom: 4px;">{isim}</h4>
        <div style="background-color: {badge_bg}; color: {badge_color}; padding: 6px 10px; border-radius: 6px; font-size: 12px; font-weight: bold; margin-bottom: 6px;">
            Tür: {tur.upper()} İnceleme Alanı
        </div>
        <p style="margin: 4px 0; font-size: 12px; color: #333;"><b>Parametreler:</b><br>{detay.replace(' | ', '<br>')}</p>
    </div>
    """
    
    hedef_grup = yesil_grup if tur == "yesil" else mavi_grup
    
    folium.Marker(
        location=[enlem, boylam],
        popup=folium.Popup(popup_html, max_width=250),
        tooltip=isim,
        icon=folium.Icon(color=icon_color, icon=icon_name)
    ).add_to(hedef_grup)

# Bölgesel Etki Alanı
folium.Circle(
    location=[sinop_enlem, sinop_boylam],
    radius=3000,
    color="teal",
    fill=True,
    fill_color="teal",
    fill_opacity=0.10,
    popup="Mavi & Yesil Veri Bolgesel Etki Alani (3.0 km)"
).add_to(m)

folium.LayerControl(position="topright", collapsed=False).add_to(m)

# Arayüz Yerleşimi (İki Sütun: Sol Harita, Sağ Grafik/Özet)
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🗺️ Coğrafi İstasyon Haritası")
    st_folium(m, width=700, height=500)

with col2:
    st.subheader("📊 İstasyon Dağılım Özeti")
    # Plotly ile etkileşimli pasta grafik
    fig = px.pie(veri, names='tur', title='Kara ve Deniz İstasyon Oranı', hole=0.4,
                 color_discrete_map={'yesil': '#2ecc71', 'mavi': '#3498db'})
    st.plotly_chart(fig, use_container_width=True)

st.success("Platform başarıyla güncellendi! Yan menüden filtreleme yapabilir ve grafik analizi inceleyebilirsiniz.")