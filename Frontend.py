from PIL import Image
import streamlit as st
import re
import html
import pandas as pd
import matplotlib.pyplot as plt
from googleapiclient.discovery import build
from textblob import TextBlob
import http.client
import json
import requests
import os

# Function to extract video ID from URL
def extract_video_id(url):
    if "youtube.com/watch?v=" in url:
        return url.split("v=")[1].split("&")[0]
    return None

# Function to extract tweet ID from URL
def extract_tweet_id(url):
    return url.strip('/').split("/")[-1]

# Preprocess Comment (Preserve Telugu and other non-ASCII characters)
def preprocess_comment(comment):
    comment = html.unescape(comment)
    comment = re.sub(r'http[s]?://\S+|www\.\S+', '', comment)  # Remove URLs
    comment = re.sub(r'<.*?>', '', comment)  # Remove HTML tags
    comment = re.sub(r'@\w+', '', comment)  # Remove Twitter handles (e.g., @username)
    return ' '.join(comment.split())  # Remove extra spaces (but keep Telugu)

# Fetch YouTube comments
def fetch_youtube_comments(video_id, api_key):
    youtube = build('youtube', 'v3', developerKey=api_key)
    comments = []
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        textFormat="plainText",
        maxResults=100
    )
    while request:
        results = request.execute()
        for item in results['items']:
            comments.append(item['snippet']['topLevelComment']['snippet']['textDisplay'])
        request = youtube.commentThreads().list_next(request, results)
    return comments

# Fetch tweets using Twitter API
def fetch_tweets(tweet_id, api_key):
    conn = http.client.HTTPSConnection("twitter-api45.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': "twitter-api45.p.rapidapi.com"
    }
    conn.request("GET", f"/latest_replies.php?id={tweet_id}", headers=headers)
    res = conn.getresponse()
    data = res.read()
    if res.status == 200:
        tweets = json.loads(data.decode("utf-8"))
        return [tweet['text'] for tweet in tweets.get('timeline', [])]
    return []

# Sentiment Analysis
def analyze_sentiment(text):
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    sentiment = 'positive' if polarity > 0 else 'negative' if polarity < 0 else 'neutral'
    return {'sentiment': sentiment, 'polarity': polarity}

# Translate Text using RapidAPI (Handle empty comments)
def transliterate_and_translate(text):
    if not text.strip():
        return None
    try:
        rapidapi_key = os.getenv('RAPIDAPI_KEY')  # Use environment variables to store the key
        url = "https://translation-api4.p.rapidapi.com/translation"
        querystring = {"from": "auto", "to": "en", "query": text}
        
        headers = {
            "x-rapidapi-key": rapidapi_key,
            "x-rapidapi-host": "translation-api4.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)

        if response.status_code == 200:
            translation = response.json()
            return translation.get('translation', 'No translation found')
        return None
    except Exception as e:
        return None

# Streamlit UI
st.markdown("<h1 style='text-align: center;'>Sentiment Analysis of Transliterated Social Media Comments</h1>", unsafe_allow_html=True)

st.markdown("<h4 style='text-align: center;'>Select a platform to analyze comments</h4>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

# Social Button Function
def social_button(icon_path, label, key):
    st.image(icon_path, width=50)
    button_style = """
    <style>
    .stButton > button {{
        background-color: #B0B0B0;
        color: black;
        border: none;
        border-radius: 5px;
        font-size: 14px;
        font-weight: bold;
    }}
    .stButton > button:hover {{
        background-color: #B0B0B0;
        color: black;
    }}
    </style>
    """
    st.markdown(button_style, unsafe_allow_html=True)
    if st.button(label, key=key):
        st.session_state.platform_selected = key

with col1:
    social_button("images/Youtube.jpeg", "YouTube", "youtube")
with col2:
    social_button("images/Twitter.jpeg", "⠀⠀X⠀⠀", "twitter")
with col3:
    social_button("images/Instagram.jpeg", "Instagram", "ig")
with col4:
    social_button("images/Facebook.jpeg", "Facebook", "fb")

# Function to run the sentiment analysis
def run_analysis(comments):
    total_comments = len(comments)
    sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
    translations = []
    
    progress_bar = st.progress(0)
    
    for i, comment in enumerate(comments):
        translated_text = transliterate_and_translate(preprocess_comment(comment))
        if translated_text:
            sentiment = analyze_sentiment(translated_text)
            sentiment_counts[sentiment['sentiment']] += 1
            translations.append({
                'Original Comment': comment,
                'Translated Comment': translated_text,
                'Sentiment': sentiment['sentiment']
            })
        progress_bar.progress(min(int(((i + 1) / total_comments) * 100), 100))
    
    df = pd.DataFrame(translations)
    st.success("Analysis complete!")
    st.dataframe(df)
    
    # Sentiment distribution pie chart
    fig, ax = plt.subplots(figsize=(2, 2))
    ax.pie(
        sentiment_counts.values(), 
        labels=sentiment_counts.keys(), 
        autopct='%1.1f%%', 
        colors=['green', 'red', 'gray'],
        textprops={'color': 'white'}
    )
    ax.set_title("Sentiment Distribution", fontsize=8, fontweight='bold', color='white')
    fig.patch.set_facecolor("#0E1117")
    ax.set_facecolor("#0E1117")
    st.pyplot(fig)
    
    most_common_sentiment = max(sentiment_counts, key=sentiment_counts.get)
    sentiment_percentage = (sentiment_counts[most_common_sentiment] / sum(sentiment_counts.values())) * 100
    
    st.markdown(f"""
    <div style='text-align: center;'>
        <h2 style="color: white; font-size: 30px; font-weight: bold;">Overall Sentiment</h2>
        <h2 style="color: white; font-size: 25px;">{most_common_sentiment.capitalize()} ({sentiment_percentage:.2f}%)</h2>
    </div>
    """, unsafe_allow_html=True)

# Make sure the platform is selected before running the analysis
if st.session_state.platform_selected:
    if st.session_state.platform_selected == "youtube":
        youtube_url = st.text_input("Enter the YouTube video URL:")
        if st.button("Analyze"):
            video_id = extract_video_id(youtube_url)
            if video_id:
                run_analysis(fetch_youtube_comments(video_id, "YOUR_YOUTUBE_API_KEY"))
            else:
                st.error("Invalid YouTube URL!")
    elif st.session_state.platform_selected == "twitter":
        tweet_url = st.text_input("Enter the Tweet URL:")
        if st.button("Analyze"):
            tweet_id = extract_tweet_id(tweet_url)
            run_analysis(fetch_tweets(tweet_id, "YOUR_TWITTER_API_KEY"))
    else:
        st.warning("🚀 Check back later! Support for this platform is coming soon.")
