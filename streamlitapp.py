import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse
import re
import random
import pandas as pd
import numpy as np

def is_meme_image(url):
    meme_hosts = ["imgur", "me.me", "imgflip", "9gag", "memedroid"]
    keywords = ["meme", "funny", "humor", "caption", "template"]
    return any(host in url.lower() for host in meme_hosts) or any(word in url.lower() for word in keywords)

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
            if src.endswith((".jpg", ".jpeg", ".png", ".gif")) and is_meme_image(src):
                image_urls.append(src)
            if len(image_urls) >= 50:
                break
        return image_urls
    except Exception as e:
        st.warning(f"⚠️ Imgur error: {e}")
        return []

def get_bing_memes(query):
    headers = {"User-Agent": "Mozilla/5.0"}
    encoded_query = urllib.parse.quote_plus(query + " meme")
    url = f"https://www.bing.com/images/search?q={encoded_query}&form=HDRSC2"
    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        matches = re.findall(r'murl&quot;:&quot;(https://[^\"]+\.(?:jpg|jpeg|png|gif))', res.text)
        meme_urls = [url for url in matches if is_meme_image(url)]
        return meme_urls[:50]
    except Exception as e:
        st.warning(f"⚠️ Bing error: {e}")
        return []


def main():
    st.set_page_config(page_title="MemeStream", page_icon="🌊", layout="wide")


    st.markdown("""
        <style>
        .review-button {
            position: fixed;
            top: 10px;
            right: 20px;
            z-index: 9999;
            background-color: #ff4b4b;
            color: white;
            padding: 10px 18px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: bold;
            box-shadow: 0 0 10px #ff4b4b55;
            transition: background-color 0.3s ease;
        }
        .review-button:hover {
            background-color: #ff1f1f;
        }
        </style>
        <a href="https://www.menti.com/alsp2dxw9tx9" target="_blank" class="review-button">⭐ Review</a>
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
        with st.spinner("🔣 Fishing memes from Imgur..."):
            meme_urls = get_imgur_memes(query_to_search)
        if not meme_urls:
            st.info("🔁 Trying Bing as fallback...")
            meme_urls = get_bing_memes(query_to_search)
        if meme_urls:
            cols = st.columns(3)
            for i, url in enumerate(meme_urls):
                with cols[i % 3]:
                    if url.endswith(".gif"):
                        st.image(url, use_container_width=True)
                    else:
                        st.image(url, use_container_width=True)
        else:
            st.warning("😕 No memes found. Try another keyword.")


    if not query_to_search:
        st.subheader("📈 People's Meme Mood")
        mood_labels = ["Funny 🤣", "Sad 😭", "Angry 😠", "Weird 🌀"]
        raw = np.random.rand(4)
        percentages = (raw / raw.sum() * 100).round().astype(int)
        mood_df = pd.DataFrame({"Mood": mood_labels, "Percentage": percentages})

        col1, col2 = st.columns([1.2, 2.5])
        with col1:
            st.markdown("### 😎 Meme Mood")
            st.bar_chart(mood_df.set_index("Mood"), use_container_width=True)
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


        music_memes = get_imgur_memes("music memes")[:15]
        if music_memes:
            music_html = """
            <style>
            .music-container {
                overflow: hidden;
                white-space: nowrap;
                box-sizing: border-box;
                padding: 10px;
                background: #000;
                border-radius: 10px;
                margin-top: 20px;
            }
            .music-track {
                display: inline-block;
                animation: scroll-right 45s linear infinite;
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
                music_html += f'<img src="{url}" alt="music meme" />'
            music_html += "</div></div>"
            st.markdown("### 🎵 Music Meme Ticker")
            st.markdown(music_html, unsafe_allow_html=True)

    else:
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

if __name__ == "__main__":
    main()
