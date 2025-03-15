import streamlit as st
import re
import html
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns  # For better visualization
from googleapiclient.discovery import build
from textblob import TextBlob
from googletrans import Translator
import os
from dotenv import load_dotenv
import requests

# Load environment variables from .env file
load_dotenv()

# Fetch API keys from environment variables
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')

# Function to extract video ID from URL
def extract_video_id(url):
    if "youtube.com/watch?v=" in url:
        return url.split("v=")[1].split("&")[0]
    return None

# Function to extract tweet ID from URL
def extract_tweet_id(url):
    return url.strip('/').split("/")[-1]

# Preprocess Comment (Preserve Telugu and other non-ASCII characters and remove emojis)
def preprocess_comment(comment):
    if not comment:
        return ""
    comment = html.unescape(comment)  # Decode HTML entities
    comment = re.sub(r'http[s]?://\S+|www\.\S+', '', comment)  # Remove URLs
    comment = re.sub(r'<.*?>', '', comment)  # Remove HTML tags
    comment = re.sub(r'@\w+', '', comment)  # Remove Twitter handles
    comment = re.sub(r'[^\x00-\x7F]+', '', comment)  # Remove non-ASCII (emojis)
    return ' '.join(comment.split())  # Remove extra spaces

# Fetch YouTube comments
def fetch_youtube_comments(video_id, api_key):
    try:
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
            for item in results.get('items', []):
                comments.append(item['snippet']['topLevelComment']['snippet']['textDisplay'])
            request = youtube.commentThreads().list_next(request, results)
        return comments
    except Exception as e:
        st.error(f"Error fetching YouTube comments: {e}")
        return []

# Fetch tweets using Twitter API
def fetch_tweets(tweet_id, api_key):
    url = f"https://twitter-api45.p.rapidapi.com/latest_replies.php?id={tweet_id}"
    headers = {
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': "twitter-api45.p.rapidapi.com"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            tweets = response.json()
            return [tweet['text'] for tweet in tweets.get('timeline', [])]
        else:
            st.error(f"Error fetching tweets: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error occurred while fetching tweets: {e}")
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
        st.warning(f"Error during translation for '{text}': {e}")
        return None

# Streamlit UI: Display profiles at the bottom-right
st.markdown("""
    <div style="position: fixed; bottom: 10px; right: 10px; background-color: rgba(0, 0, 0, 0.5); padding: 10px; border-radius: 8px; width: auto;">
        <h3 style="color: white;">Project By:</h3>
        <p style="color: white;">
            <strong>S.K.Mruduvani</strong><br>
            <a href="https://github.com/Mrudu17" target="_blank">GitHub</a> | 
            <a href="https://www.linkedin.com/in/s-k-mruduvani" target="_blank">LinkedIn</a><br><br>
            <strong>Kataru Shreya</strong><br>
            <a href="https://github.com/KataruShreya" target="_blank">GitHub</a> | 
            <a href="https://www.linkedin.com/in/shreyakataru" target="_blank">LinkedIn</a>
        </p>
    </div>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>Sentiment Analysis of Social Media Comments</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center;'>Select a platform to analyze comments</h4>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

def social_button(icon_path, label, key):
    st.image(icon_path, width=50)
    if st.button(label, key=key):
        st.session_state.platform_selected = key

with col1:
    social_button("images/Youtube.jpeg", "Youtube", "youtube")
with col2:
    social_button("images/X .jpeg", "⠀⠀X⠀⠀", "twitter")
with col3:
    social_button("images/Instagram.jpeg", "Instagram", "ig")
with col4:
    social_button("images/Facebook.jpeg", "Facebook", "fb")

if "platform_selected" not in st.session_state:
    st.session_state.platform_selected = None

# Function to run analysis
def run_analysis(comments):
    total_comments = len(comments)
    if total_comments == 0:
        st.warning("No comments found to analyze!")
        return

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
        progress_bar.progress((i + 1) / total_comments)
    
    df = pd.DataFrame(translations)
    st.success("Analysis complete!")
    st.dataframe(df)
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", data=csv, file_name="sentiment_analysis.csv", mime="text/csv")

    # Plot sentiment distribution
    fig, ax = plt.subplots()
    ax.pie(sentiment_counts.values(), labels=sentiment_counts.keys(), autopct='%1.1f%%', colors=['green', 'red', 'gray'])
    st.pyplot(fig)

# Handling platform selection and analysis
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

