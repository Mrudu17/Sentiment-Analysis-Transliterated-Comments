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
import time
from dotenv import load_dotenv
import os

# Load environment variables from the .env file (only once at the start of the script)
load_dotenv()

# Fetch API keys from environment variables
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")

# Ensure API keys are loaded correctly
if not YOUTUBE_API_KEY or not TWITTER_API_KEY:
    st.error("API keys are missing! Please check your .env file.")

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
    comment = re.sub(r'[^\x00-\x7F\u0C00-\u0C7F]+', '', comment)  # Preserve Telugu characters
    return ' '.join(comment.split())  # Remove extra spaces

# Fetch YouTube comments
def fetch_youtube_comments(video_id, api_key):
    start_time = time.time()  # Track API call duration
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

    duration = time.time() - start_time  # Measure time taken for the API request
    st.write(f"Fetched {len(comments)} YouTube comments in {duration:.2f} seconds.")  # Log duration
    return comments

# Fetch tweets using Twitter API
def fetch_tweets(tweet_id, api_key):
    start_time = time.time()  # Track API call duration
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
        duration = time.time() - start_time  # Measure time taken for the API request
        st.write(f"Fetched {len(tweets.get('timeline', []))} tweets in {duration:.2f} seconds.")  # Log duration
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
        
        # Detect the language of the text
        detected_lang = translator.detect(text).lang
        
        # Translate the text to English
        translation = translator.translate(text, src=detected_lang, dest='en')
        
        return translation.text
    except Exception as e:
        print(f"Error during translation for '{text}': {e}")
        return None

# Common function to run analysis
def run_analysis(comments):
    total_comments = len(comments)
    sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
    translations = []
    
    progress_bar = st.progress(0)
    
    for i, comment in enumerate(comments):
        preprocessed_comment = preprocess_comment(comment)  # Preprocess the comment
        translated_text = transliterate_and_translate(preprocessed_comment)
        
        if translated_text:
            sentiment = analyze_sentiment(translated_text)
            sentiment_counts[sentiment['sentiment']] += 1
            translations.append({
                'Original Comment': comment,
                'Preprocessed Comment': preprocessed_comment,  # Add preprocessed comment to the DataFrame
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



