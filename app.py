import streamlit as st
import requests
import random
import time
import base64

# --- 1. AYARLAR ---
UYGULAMA_ADI = "CEMRENİN MÜZİK KUTUSU"
LOGO_URL = "https://p7.hiclipart.com/preview/256/896/4/vodafone-park-be%C5%9Fikta%C5%9F-j-k-football-team-super-lig-bjk-akatlar-arena-football.jpg"
API_KEY = "AIzaSyAfXdRpKAV9pxZKRGYx5Cj_Btw1lIdCVaw"
MUZIK_FOLDER_ID = "11gcrukvEObg-9Vwu4l_vFW4vRS5Oc2Wz"
FOTO_FOLDER_ID = "1-wlcQSKbhyKPXBB3T0_hvk-rgCTNVICT"
UYGULAMA_SIFRESI = "1234"

st.set_page_config(page_title=UYGULAMA_ADI, page_icon="🦅", layout="centered")

# Google Drive'dan dosya listesini çeken fonksiyon
@st.cache_data(ttl=600)
def get_drive_files(folder_id):
    url = f"https://www.googleapis.com/drive/v3/files?q='{folder_id}'+in+parents&fields=files(id, name)&key={API_KEY}"
    response = requests.get(url)
    return response.json().get('files', [])

# Tasarım
st.markdown("<style>.stApp {background-color: #000; color: #fff;}</style>", unsafe_allow_html=True)
st.title(UYGULAMA_ADI)

# Verileri Çek
files = get_drive_files(MUZIK_FOLDER_ID)

if files:
    selected_file = st.selectbox("Bir şarkı seçin:", files, format_func=lambda x: x['name'])
    
    if selected_file:
        # HIZLI YÖNTEM: Doğrudan Link Oluşturma
        # Bu link tarayıcının dosyayı doğrudan çekmesini sağlar
        file_id = selected_file['id']
        direct_link = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media&key={API_KEY}"
        
        st.subheader(f"Şu an çalıyor: {selected_file['name']}")
        st.audio(direct_link) # Base64 kullanmadan direkt link ile oynatır
else:
    st.warning("Klasörde dosya bulunamadı veya API hatası.")

# --- 2. CSS TASARIMI (Parantez hataları düzeltildi) ---
st.markdown(f"""
<style>
    .stApp {{
        background: linear-gradient(135deg, #000000, #1a1a1a, #050505);
        color: white;
    }}
    .logo-container {{ text-align: center; padding: 20px; }}
    .logo-img {{ 
        border-radius: 50%; border: 3px solid #ffffff; 
        width: 150px; height: 150px; object-fit: cover; 
    }}
    .stButton>button {{
        width: 100%; border-radius: 30px; border: none;
        background: linear-gradient(90deg, #000000, #444444); 
        color: white; font-weight: bold; padding: 10px;
        border: 1px solid #555;
    }}
    .stButton>button:hover {{ 
        background: #ffffff; color: black;
    }}
    .song-card {{
        background: rgba(255, 255, 255, 0.03); border-radius: 15px;
        padding: 15px; margin-bottom: 10px; border-left: 5px solid #ffffff;
    }}
</style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if "auth" not in st.session_state: st.session_state.auth = False
if "idx" not in st.session_state: st.session_state.idx = 0

if not st.session_state.auth:
    st.markdown(f'<div class="logo-container"><img class="logo-img" src="{LOGO_URL}"></div>', unsafe_allow_html=True)
    sifre = st.text_input("Şifre", type="password")
    if st.button("Başlat"):
        if sifre == UYGULAMA_SIFRESI:
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- 4. VERİ ÇEKME FONKSİYONLARI ---
@st.cache_data(ttl=600)
def get_files(f_id):
    try:
        url = f"https://www.googleapis.com/drive/v3/files?q='{{f_id}}'+in+parents&fields=files(id, name)&key={API_KEY}"
        return requests.get(url.format(f_id=f_id)).json().get('files', [])
    except: return []

# Dosyayı indirip Base64 formatına çeviren sihirli fonksiyon (Engelleri bu aşar)
def get_audio_base64(file_id):
    try:
        url = f"https://www.googleapis.com/drive/v3/files/{{file_id}}?alt=media&key={API_KEY}"
        res = requests.get(url.format(file_id=file_id))
        return base64.b64encode(res.content).decode()
    except: return None

songs = sorted([f for f in get_files(MUZIK_FOLDER_ID) if f['name'].lower().endswith(('.mp3', '.m4a'))], key=lambda x: x['name'])
photos = get_files(FOTO_FOLDER_ID)

# --- 5. ANA EKRAN ---
st.markdown(f'<div class="logo-container"><img class="logo-img" src="{LOGO_URL}"></div>', unsafe_allow_html=True)
st.title(UYGULAMA_ADI)

search = st.text_input("🔍 Ara...", placeholder="Şarkı ismi...")
filtered = [s for s in songs if search.lower() in s['name'].lower()]

for s in filtered:
    col_txt, col_btn = st.columns([5, 1])
    with col_txt:
        st.markdown(f'<div class="song-card"><b>{s["name"].split(".")[0]}</b></div>', unsafe_allow_html=True)
    with col_btn:
        if st.button("▶️", key=f"p_{s['id']}"):
            st.session_state.idx = songs.index(s)
            st.rerun()

# --- 6. GÜÇLÜ SIDEBAR OYNATICI ---
if songs:
    cur = songs[st.session_state.idx]
    cur_clean = cur['name'].split('.')[0]
    
    with st.sidebar:
        st.markdown("### 🦅 Şimdi Çalıyor")
        st.info(f"**{cur_clean}**")
        
        # Görsel
        match = next((p for p in photos if cur_clean.lower() in p['name'].lower()), None)
        p_id = match['id'] if match else (random.choice(photos)['id'] if photos else None)
        if p_id:
            img_url = f"https://www.googleapis.com/drive/v3/files/{p_id}?alt=media&key={API_KEY}"
            st.image(img_url, width='stretch')
        
        # --- KESİN ÇÖZÜM: BASE64 STREAM ---
        with st.spinner("Şarkı hazırlanıyor..."):
            audio_base64 = get_audio_base64(cur['id'])
            if audio_base64:
                audio_html = f"""
                    <audio controls autoplay style="width: 100%;">
                        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                    </audio>
                """
                st.markdown(audio_html, unsafe_allow_html=True)
            else:
                st.error("Müzik yüklenemedi!")
        
        # Navigasyon
        c1, c2 = st.columns(2)
        with c1:
            if st.button("⏮️ Geri"):
                st.session_state.idx = (st.session_state.idx - 1) % len(songs)
                st.rerun()
        with c2:
            if st.button("İleri ⏭️"):
                st.session_state.idx = (st.session_state.idx + 1) % len(songs)
                st.rerun()

st.markdown("<br><hr><center><small>Beşiktaş Temalı Müzik Kutusu</small></center>", unsafe_allow_html=True)