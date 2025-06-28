import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse
import re
import random
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ✅ Smart filter for real memes only
def is_meme_image(url):
    meme_hosts = ["imgur", "me.me", "imgflip", "9gag", "memedroid"]
    keywords = ["meme", "funny", "humor", "caption", "template"]
    if any(host in url.lower() for host in meme_hosts):
        return True
    if any(word in url.lower() for word in keywords):
        return True
    return False

# ✅ Imgur meme fetcher
def get_imgur_memes(query):
    headers = {"User-Agent": "Mozilla/5.0"}
    encoded_query = urllib.parse.quote_plus(query + " meme")
    url = f"https://imgur.com/search?q={encoded_query}"
    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        image_urls = []
        for img in soup.find_all("img"):
            src = img.get("src")
            if not src:
                continue
            if src.startswith("//"):
                src = "https:" + src
            elif src.startswith("/"):
                src = "https://imgur.com" + src
            if src.endswith((".jpg", ".jpeg", ".png")) and is_meme_image(src):
                image_urls.append(src)
            if len(image_urls) >= 40:
                break
        return image_urls
    except Exception as e:
        st.warning(f"⚠️ Imgur error: {e}")
        return []

# ✅ Bing fallback meme fetcher
def get_bing_memes(query):
    headers = {"User-Agent": "Mozilla/5.0"}
    encoded_query = urllib.parse.quote_plus(query + " meme")
    url = f"https://www.bing.com/images/search?q={encoded_query}&form=HDRSC2"
    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        matches = re.findall(r'murl&quot;:&quot;(https://[^\"]+\.(?:jpg|jpeg|png))', res.text)
        meme_urls = [url for url in matches if is_meme_image(url)][:]
        return meme_urls
    except Exception as e:
        st.warning(f"⚠️ Bing error: {e}")
        return []

# ✅ Meme Mood Chart (vertical)
def show_mood_chart():
    st.markdown("### 😎 Meme Mood")
    moods = ['Funny 🤣', 'Sad 😭', 'Angry 😠', 'Weird 🌀']
    values = np.random.randint(10, 100, size=4)

    fig, ax = plt.subplots()
    ax.bar(moods, values, color='skyblue')
    ax.set_title('📊 Meme Mood')
    st.pyplot(fig)

# ✅ Music Meme Ticker
def show_music_meme_ticker():
    music_memes = get_imgur_memes("music memes")[:24]
    if music_memes:
        ticker_html = """
        <style>
        .music-container {
            overflow: hidden;
            white-space: nowrap;
            box-sizing: border-box;
            padding: 10px;
            background: #111;
            border-radius: 10px;
            margin-top: 30px;
        }
        .music-track {
            display: inline-block;
            animation: scroll-right 60s linear infinite;
        }
        .music-track img {
            height: 110px;
            margin-left: 20px;
            border-radius: 10px;
            box-shadow: 0 0 6px #00000088;
        }
        @keyframes scroll-right {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }
        </style>
        <div class="music-container">
            <div class="music-track">
        """
        for url in music_memes:
            ticker_html += f'<img src="{url}" alt="music meme" />'
        ticker_html += "</div></div>"

        st.markdown("### 🎵 Music Meme Ticker")
        st.markdown(ticker_html, unsafe_allow_html=True)

# ✅ MemeStream main app
def main():
    st.set_page_config(page_title="MemeStream", page_icon="🌊", layout="wide")

    # Review button top right
    st.markdown("""
        <style>
            .review-button {
                position: fixed;
                top: 20px;
                right: 20px;
                background-color: #ff4b4b;
                color: white;
                padding: 10px 18px;
                border-radius: 5px;
                text-decoration: none;
                font-weight: bold;
                z-index: 9999;
            }
        </style>
        <a href="https://www.menti.com/alsp2dxw9tx9" class="review-button" target="_blank">⭐ Review</a>
    """, unsafe_allow_html=True)

    st.title("MemeStream - Fish the meme you like...")

    if "search_query" not in st.session_state:
        st.session_state.search_query = ""

    search_query = st.text_input("Search for memes:", value=st.session_state.search_query)
    if search_query:
        st.session_state.search_query = search_query.strip()

    query_to_search = search_query.strip() or st.session_state.get("search_query", "")

    if query_to_search:
        st.subheader(f"🎯 Results for: {query_to_search}")
        with st.spinner("🎣 Fishing memes from Imgur..."):
            meme_urls = get_imgur_memes(query_to_search)

        if not meme_urls:
            st.info("🔁 Trying Bing as fallback...")
            meme_urls = get_bing_memes(query_to_search)

        if meme_urls:
            cols = st.columns(3)
            for i, url in enumerate(meme_urls):
                with cols[i % 3]:
                    st.image(url, use_container_width=True, clamp=False)
        else:
            st.warning("😕 No memes found. Try another keyword.")
    else:
        # Only show mood chart and ticker when no search is active
        col1, col2 = st.columns([1, 2])
        with col1:
            show_mood_chart()
        with col2:
            st.subheader("🔥 Trending Meme Topics")
            trending_topics = ["Random", "Surprise me", "Cat memes", "Distracted dog",
                               "NFSW", "Shaun The Sheep", "Change My Mind", "sus world", "MafuMafu"]
            cols = st.columns(3)
            for i, topic in enumerate(trending_topics):
                with cols[i % 3]:
                    if st.button(topic):
                        if topic == "Surprise me":
                            topic = random.choice([t for t in trending_topics if t != "Surprise me"])
                        elif topic == "Random":
                            topic = random.choice(["funny", "relatable", "programming", "exam", "tamil", "monday meme"])
                        st.session_state.search_query = topic
                        st.rerun()
        show_music_meme_ticker()

if __name__ == "__main__":
    main()
