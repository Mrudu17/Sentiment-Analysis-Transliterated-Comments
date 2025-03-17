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

# Load API keys from Streamlit secrets
TWITTER_API_KEY = st.secrets["TWITTER_API_KEY"]
YOUTUBE_API_KEY = st.secrets["YOUTUBE_API_KEY"]

if not YOUTUBE_API_KEY or not TWITTER_API_KEY:
    st.error("API keys are missing! Please check your .env file!")

# Function to extract video ID from YouTube URL
def extract_video_id(url):
    if "youtube.com/watch?v=" in url:
        return url.split("v=")[1].split("&")[0]
    return None

# Function to extract tweet ID from Twitter URL
def extract_tweet_id(url):
    return url.strip('/').split("/")[-1]

# Preprocess Comment (Preserve Hindi and Telugu characters)
def preprocess_comment(comment):
    comment = html.unescape(comment)
    comment = re.sub(r'http[s]?://\S+|www\.\S+', '', comment)  # Remove URLs
    comment = re.sub(r'<.*?>', '', comment)  # Remove HTML tags
    comment = re.sub(r'@\w+', '', comment)  # Remove Twitter handles (e.g., @username)
    comment = re.sub(r'[^\x00-\x7F\u0900-\u097F\u0C00-\u0C7F]+', '', comment)  # Preserve Hindi and Telugu characters
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

# Improved Translation Function for Pure Hindi and Telugu Comments
def transliterate_and_translate(text):
    if not text.strip():
        return None
    try:
        translator = Translator()
        
        # Detect language
        detected_lang = translator.detect(text).lang
        
        # Explicitly set source language if it's pure Hindi or Telugu
        if re.match(r'^[\u0900-\u097F\s]+$', text):  # Pure Hindi
            translation = translator.translate(text, src='hi', dest='en')
        elif re.match(r'^[\u0C00-\u0C7F\s]+$', text):  # Pure Telugu
            translation = translator.translate(text, src='te', dest='en')
        else:
            translation = translator.translate(text, src='auto', dest='en')
        
        return translation.text
    except Exception as e:
        print(f"Error during translation for '{text}': {e}")
        return None

# Streamlit UI
st.markdown("<h1 style='text-align: center;'>Sentiment Analysis of Transliterated Social Media Comments</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center;'>Select a platform to analyze comments</h4>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

def social_button(icon_path, label, key):
    st.image(icon_path, width=50)
    if st.button(label, key=key):
        st.session_state.platform_selected = key

with col1:
    social_button("images/Youtube.jpeg", "YouTube", "youtube")
with col2:
    social_button("images/X .jpeg", "⠀⠀X⠀⠀", "twitter")
with col3:
    social_button("images/Instagram.jpeg", "instagram", "ig")
with col4:
    social_button("images/Facebook.jpeg", "facebook", "fb")

if "platform_selected" not in st.session_state:
    st.session_state.platform_selected = None

# Common function to run analysis
def run_analysis(comments):
    total_comments = len(comments)
    sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
    translations = []
    
    progress_bar = st.progress(0)
    
    for i, comment in enumerate(comments):
        preprocessed_comment = preprocess_comment(comment)  # Preprocess comment
        translated_text = transliterate_and_translate(preprocessed_comment)  # Translate preprocessed comment
        
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
    st.success("Analysis complete!")
    st.dataframe(df)
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", data=csv, file_name="sentiment_analysis.csv", mime="text/csv")
    
    fig, ax = plt.subplots(figsize=(2, 2))
    ax.pie(
        sentiment_counts.values(), 
        labels=sentiment_counts.keys(), 
        autopct='%1.1f%%', 
        colors=['green', 'red', 'gray'],
        textprops={'color': 'white', 'fontsize': 5}
    )
    ax.set_title("Sentiment Distribution", fontsize=10, fontweight='bold', color='white')
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

if st.session_state.platform_selected:
    if st.session_state.platform_selected == "youtube":
        youtube_url = st.text_input("Enter the YouTube video URL:")
        if st.button("Analyze"):
            video_id = extract_video_id(youtube_url)
            if video_id:
                run_analysis(fetch_youtube_comments(video_id, YOUTUBE_API_KEY))
            else:
                st.error("Invalid YouTube URL!")
    elif st.session_state.platform_selected == "twitter":
        tweet_url = st.text_input("Enter the Tweet URL:")
        if st.button("Analyze"):
            tweet_id = extract_tweet_id(tweet_url)
            run_analysis(fetch_tweets(tweet_id, TWITTER_API_KEY))
    else:
        st.warning("🚀 Check back later! Support for this platform is coming soon.")
