import streamlit as st
import requests
import random

# --- 1. AYARLAR ---
UYGULAMA_ADI = "CEMRENİN MÜZİK KUTUSU"
LOGO_URL = "https://p7.hiclipart.com/preview/256/896/4/vodafone-park-be%C5%9Fikta%C5%9F-j-k-football-team-super-lig-bjk-akatlar-arena-football.jpg"
API_KEY = "AIzaSyAfXdRpKAV9pxZKRGYx5Cj_Btw1lIdCVaw"
MUZIK_FOLDER_ID = "11gcrukvEObg-9Vwu4l_vFW4vRS5Oc2Wz"
FOTO_FOLDER_ID = "1-wlcQSKbhyKPXBB3T0_hvk-rgCTNVICT"
UYGULAMA_SIFRESI = "1234"

st.set_page_config(page_title=UYGULAMA_ADI, page_icon="🦅", layout="centered")

# --- 2. CSS TASARIMI (Mobil Uyumlu) ---
st.markdown(f"""
<style>
    .stApp {{
        background: linear-gradient(135deg, #000000, #1a1a1a, #050505);
        color: white;
    }}
    .logo-container {{ text-align: center; padding: 10px; }}
    .logo-img {{ 
        border-radius: 50%; border: 3px solid #ffffff; 
        width: 120px; height: 120px; object-fit: cover; 
    }}
    .stButton>button {{
        width: 100%; border-radius: 20px; border: none;
        background: linear-gradient(90deg, #111, #333); 
        color: white; font-weight: bold; padding: 12px;
        border: 1px solid #444;
        font-size: 16px;
    }}
    .stButton>button:hover {{ 
        background: #ffffff; color: black;
    }}
    .song-card {{
        background: rgba(255, 255, 255, 0.05); border-radius: 12px;
        padding: 12px; margin-bottom: 8px; border-left: 4px solid #ffffff;
    }}
</style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if "auth" not in st.session_state: st.session_state.auth = False
if "idx" not in st.session_state: st.session_state.idx = 0

# Giriş Ekranı
if not st.session_state.auth:
    st.markdown(f'<div class="logo-container"><img class="logo-img" src="{LOGO_URL}"></div>', unsafe_allow_html=True)
    sifre = st.text_input("Şifre", type="password")
    if st.button("🦅 Giriş Yap"):
        if sifre == UYGULAMA_SIFRESI:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Hatalı Şifre!")
    st.stop()

# --- 4. VERİ ÇEKME ---
@st.cache_data(ttl=600)
def get_files(f_id):
    try:
        url = f"https://www.googleapis.com/drive/v3/files?q='{f_id}'+in+parents&fields=files(id, name)&key={API_KEY}"
        res = requests.get(url).json()
        return res.get('files', [])
    except:
        return []

songs = sorted([f for f in get_files(MUZIK_FOLDER_ID) if f['name'].lower().endswith(('.mp3', '.m4a'))], key=lambda x: x['name'])
photos = get_files(FOTO_FOLDER_ID)

# --- 5. ANA EKRAN ---
st.markdown(f'<div class="logo-container"><img class="logo-img" src="{LOGO_URL}"></div>', unsafe_allow_html=True)
st.title("Kartal Müzik")

search = st.text_input("🔍 Şarkı Ara...", placeholder="Bir parça ismi yaz...")
filtered = [s for s in songs if search.lower() in s['name'].lower()]

# Şarkı Listesi
for s in filtered:
    col_txt, col_btn = st.columns([4, 1])
    with col_txt:
        st.markdown(f'<div class="song-card"><b>{s["name"].split(".")[0]}</b></div>', unsafe_allow_html=True)
    with col_btn:
        if st.button("▶️", key=f"play_{s['id']}"):
            st.session_state.idx = songs.index(s)
            st.rerun()

# --- 6. OYNATICI (Mobil İçin Geliştirilmiş) ---
if songs:
    cur = songs[st.session_state.idx]
    cur_clean = cur['name'].split('.')[0]
    
    st.markdown("---")
    st.subheader(f"🎵 {cur_clean}")
    
    # Fotoğrafı Getir
    match = next((p for p in photos if cur_clean.lower() in p['name'].lower()), None)
    p_id = match['id'] if match else (random.choice(photos)['id'] if photos and len(photos)>0 else None)
    
    if p_id:
        img_url = f"https://www.googleapis.com/drive/v3/files/{p_id}?alt=media&key={API_KEY}"
        st.image(img_url, use_container_width=True)

    # Ses Bağlantısı (Direct Link)
    audio_url = f"https://www.googleapis.com/drive/v3/files/{cur['id']}?alt=media&key={API_KEY}"
    
    # TELEFONLAR İÇİN HTML5 PLAYER (Daha sağlam çalışır)
    st.markdown(f"""
        <audio controls autoplay style="width: 100%; margin-top: 10px;">
            <source src="{audio_url}" type="audio/mpeg">
            Tarayıcınız bu oynatıcıyı desteklemiyor.
        </audio>
    """, unsafe_allow_html=True)
    
    # Alt Navigasyon
    nav1, nav2 = st.columns(2)
    with nav1:
        if st.button("⏮️ Önceki"):
            st.session_state.idx = (st.session_state.idx - 1) % len(songs)
            st.rerun()
    with nav2:
        if st.button("Sonraki ⏭️"):
            st.session_state.idx = (st.session_state.idx + 1) % len(songs)
            st.rerun()

st.markdown("<br><center><small>🦅 Beşiktaş 1903 🦅</small></center>", unsafe_allow_html=True)