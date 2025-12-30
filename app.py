import streamlit as st
import requests
import random
import base64

# --- 1. AYARLAR ---
UYGULAMA_ADI = "CEMRENİN MÜZİK KUTUSU"
LOGO_URL = "https://p7.hiclipart.com/preview/256/896/4/vodafone-park-be%C5%9Fikta%C5%9F-j-k-football-team-super-lig-bjk-akatlar-arena-football.jpg"
API_KEY = "AIzaSyAfXdRpKAV9pxZKRGYx5Cj_Btw1lIdCVaw"
MUZIK_FOLDER_ID = "11gcrukvEObg-9Vwu4l_vFW4vRS5Oc2Wz"
FOTO_FOLDER_ID = "1-wlcQSKbhyKPXBB3T0_hvk-rgCTNVICT"
UYGULAMA_SIFRESI = "1234"

st.set_page_config(page_title=UYGULAMA_ADI, page_icon="🦅", layout="centered")

# --- 2. CSS TASARIMI ---
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
    .stButton>button:hover {{ background: #ffffff; color: black; }}
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
        url = f"https://www.googleapis.com/drive/v3/files?q='{f_id}'+in+parents&fields=files(id, name)&key={API_KEY}"
        return requests.get(url).json().get('files', [])
    except: return []

# Dosyaları (Ses veya Resim) Base64 formatına çeviren genel fonksiyon
@st.cache_resource
def get_base64_data(file_id):
    try:
        url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media&key={API_KEY}"
        data = requests.get(url).content
        return base64.b64encode(data).decode()
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

# --- 6. OYNATICI VE GÖRSEL ---
if songs:
    cur = songs[st.session_state.idx]
    cur_clean = cur['name'].split('.')[0]
    
    with st.sidebar:
        st.markdown("### 🦅 Şimdi Çalıyor")
        st.info(f"**{cur_clean}**")
        
        # --- GÖRSEL ÇÖZÜMÜ ---
        match = next((p for p in photos if cur_clean.lower() in p['name'].lower()), None)
        p_id = match['id'] if match else (random.choice(photos)['id'] if photos else None)
        
        if p_id:
            img_base64 = get_base64_data(p_id)
            if img_base64:
                # Görselin telefonda ve PC'de düzgün görünmesi için HTML kullanıyoruz
                st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" style="width:100%; border-radius:10px; border: 1px solid #fff;">', unsafe_allow_html=True)
        
        # --- SES ÇÖZÜMÜ ---
        with st.spinner("Şarkı hazırlanıyor..."):
            audio_base64 = get_base64_data(cur['id'])
            if audio_base64:
                audio_html = f'<audio controls autoplay style="width:100%; margin-top:10px;"><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>'
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