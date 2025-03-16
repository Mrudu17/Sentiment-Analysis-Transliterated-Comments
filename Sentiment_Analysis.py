import streamlit as st
import re
import html
import pandas as pd
import matplotlib.pyplot as plt
from googleapiclient.discovery import build
from textblob import TextBlob
from googletrans import Translator
import http.client
import json
import requests
from dotenv import load_dotenv
import os

# Load environment variables explicitly
load_dotenv(dotenv_path=".env")

# Fetch API keys
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")

# Check if API keys are available
if not YOUTUBE_API_KEY or not TWITTER_API_KEY:
    st.error("⚠️ API keys are missing! Please check your `.env` file.")

# Function to extract video ID from YouTube URL
def extract_video_id(url):
    match = re.search(r"(?<=v=)[^&]+", url)
    return match.group(0) if match else None

# Function to extract tweet ID from URL
def extract_tweet_id(url):
    return url.strip('/').split("/")[-1]

# Preprocess Comment (Preserve Telugu and other non-ASCII characters)
def preprocess_comment(comment):
    comment = html.unescape(comment)
    comment = re.sub(r'http[s]?://\S+|www\.\S+', '', comment)  # Remove URLs
    comment = re.sub(r'<.*?>', '', comment)  # Remove HTML tags
    comment = re.sub(r'@\w+', '', comment)  # Remove Twitter handles
    return ' '.join(comment.split())  # Remove extra spaces

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

# Translate Text using Google Translator
def transliterate_and_translate(text):
    if not text.strip():
        return None
    try:
        translator = Translator()
        translation = translator.translate(text, src='auto', dest='en')
        return translation.text
    except Exception as e:
        st.warning(f"⚠️ Translation error: {e}")
        return None

# Streamlit UI
st.markdown("<h1 style='text-align: center;'>Sentiment Analysis of Social Media Comments</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center;'>Select a platform to analyze comments</h4>", unsafe_allow_html=True)

# Social media platform selection
col1, col2, col3, col4 = st.columns(4)

def social_button(icon_path, label, key):
    st.image(icon_path, width=50)
    if st.button(label, key=key):
        st.session_state.platform_selected = key

with col1:
    social_button("images/Youtube.jpeg", "YouTube", "youtube")
with col2:
    social_button("images/X.jpeg", "X (Twitter)", "twitter")
with col3:
    social_button("images/Instagram.jpeg", "Instagram", "instagram")
with col4:
    social_button("images/Facebook.jpeg", "Facebook", "facebook")

# Initialize platform selection state
if "platform_selected" not in st.session_state:
    st.session_state.platform_selected = None

# Common function to run analysis
def run_analysis(comments):
    if not comments:
        st.warning("⚠️ No comments found!")
        return

    total_comments = len(comments)
    sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
    translations = []

    progress_bar = st.progress(0)

    for i, comment in enumerate(comments):
        preprocessed_comment = preprocess_comment(comment)
        translated_text = transliterate_and_translate(preprocessed_comment)

        if translated_text:
            sentiment = analyze_sentiment(translated_text)
            sentiment_counts[sentiment['sentiment']] += 1
            translations.append({
                'Original Comment': comment,
                'Preprocessed Comment': preprocessed_comment,
                'Translated Comment': translated_text,
                'Sentiment': sentiment['sentiment']
            })

        progress_bar.progress(min(int(((i + 1) / total_comments) * 100), 100))

    df = pd.DataFrame(translations)
    st.success("✅ Analysis complete!")
    st.dataframe(df)

    # Download CSV button
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download CSV", data=csv, file_name="sentiment_analysis.csv", mime="text/csv")

    # Sentiment Pie Chart
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.pie(
        sentiment_counts.values(),
        labels=sentiment_counts.keys(),
        autopct='%1.1f%%',
        colors=['green', 'red', 'gray'],
        textprops={'fontsize': 10}
    )
    ax.set_title("Sentiment Distribution", fontsize=12, fontweight='bold')
    st.pyplot(fig)

    # Display overall sentiment
    most_common_sentiment = max(sentiment_counts, key=sentiment_counts.get)
    sentiment_percentage = (sentiment_counts[most_common_sentiment] / sum(sentiment_counts.values())) * 100

    st.markdown(f"""
    <div style='text-align: center;'>
        <h2 style="color: black; font-size: 24px; font-weight: bold;">Overall Sentiment</h2>
        <h3 style="color: black; font-size: 20px;">{most_common_sentiment.capitalize()} ({sentiment_percentage:.2f}%)</h3>
    </div>
    """, unsafe_allow_html=True)

# Handle platform selection and input
if st.session_state.platform_selected:
    if st.session_state.platform_selected == "youtube":
        youtube_url = st.text_input("🎥 Enter YouTube video URL:")
        if st.button("Analyze"):
            video_id = extract_video_id(youtube_url)
            if video_id:
                run_analysis(fetch_youtube_comments(video_id, YOUTUBE_API_KEY))
            else:
                st.error("❌ Invalid YouTube URL!")
    elif st.session_state.platform_selected == "twitter":
        tweet_url = st.text_input("🐦 Enter Tweet URL:")
        if st.button("Analyze"):
            tweet_id = extract_tweet_id(tweet_url)
            run_analysis(fetch_tweets(tweet_id, TWITTER_API_KEY))
    else:
        st.warning("🚀 Support for this platform is coming soon!")
