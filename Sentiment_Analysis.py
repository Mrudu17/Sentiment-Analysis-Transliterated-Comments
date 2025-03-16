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

# Load environment variables from .env file
load_dotenv()

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
    try:
        conn = http.client.HTTPSConnection("twitter-api45.p.rapidapi.com")
        headers = {
            'x-rapidapi-key': api_key,
            'x-rapidapi-host': "twitter-api45.p.rapidapi.com"
        }
        
        # Ensure headers are properly formatted
        for key, value in headers.items():
            if not isinstance(value, str):
                headers[key] = str(value)
        
        # Make the API request
        conn.request("GET", f"/latest_replies.php?id={tweet_id}", headers=headers)
        res = conn.getresponse()
        data = res.read()
        
        if res.status == 200:
            tweets = json.loads(data.decode("utf-8"))
            return [tweet['text'] for tweet in tweets.get('timeline', [])]
        else:
            st.error(f"Failed to fetch tweets: {res.status} {res.reason}")
            return []
    except Exception as e:
        st.error(f"An error occurred while fetching tweets: {e}")
        return []

# Sentiment Analysis
def analyze_sentiment(text):
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    sentiment = 'positive' if polarity > 0 else 'negative' if polarity < 0 else 'neutral'
    return {'sentiment': sentiment, 'polarity': polarity}

# Translate Text using Google Translator (with fallback)
def transliterate_and_translate(text):
    if not text.strip():
        return text  # Return original text if empty
    
    try:
        translator = Translator()
        translation = translator.translate(text, src='auto', dest='en')
        return translation.text
    except Exception as e:
        print(f"Translation failed for '{text}': {e}")
        return text  # Return original text if translation fails

# Streamlit UI: Display profiles immediately at the top-right
st.markdown("""
    <div style="position: fixed; bottom: 10px; right: 10px; background-color: rgba(0, 0, 0, 0.5); padding: 10px; border-radius: 8px; width: auto;">
        <h3 style="color: white; font-size: 18px; font-weight: bold; text-align: center;">Project By:</h3>
        <p style="color: white; font-size: 14px; line-height: 1.6;">
            <strong>S.K.Mruduvani</strong><br>
            GitHub <a href="https://github.com/Mrudu17" target="_blank">
                <img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" width="18" height="18" style="vertical-align: middle;">
            </a><br>
            LinkedIn <a href="https://www.linkedin.com/in/s-k-mruduvani" target="_blank">
                <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" width="18" height="18" style="vertical-align: middle;">
            </a><br><br>
            <strong>Kataru Shreya</strong><br>
            GitHub <a href="https://github.com/KataruShreya" target="_blank">
                <img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" width="18" height="18" style="vertical-align: middle;">
            </a><br>
            LinkedIn <a href="https://www.linkedin.com/in/shreyakataru" target="_blank">
                <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" width="18" height="18" style="vertical-align: middle;">
            </a><br>
        </p>
    </div>
""", unsafe_allow_html=True)

# Streamlit UI: Title and Platform Selection
st.markdown("<h1 style='text-align: center;'>Sentiment Analysis of Transliterated Social Media Comments</h1>", unsafe_allow_html=True)

st.markdown("<h4 style='text-align: center;'>Select a platform to analyze comments</h4>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

def social_button(icon_path, label, key):
    st.image(icon_path, width=50)
    
    # Updated button style with grey background and black text on hover
    button_style = """
    <style>
    .stButton > button {{
        background-color: #B0B0B0; /* Professional grey */
        color: black; /* Black text color */
        border: none;
        border-radius: 5px;
        font-size: 14px;
        font-weight: bold;
    }}
    .stButton > button:hover {{
        background-color: #B0B0B0; /* Keep grey background on hover */
        color: black; /* Keep text color black on hover */
    }}
    </style>
    """
    st.markdown(button_style, unsafe_allow_html=True)
    
    if st.button(label, key=key):
        st.session_state.platform_selected = key  # Store the key (not label)


with col1:
    social_button("images/Youtube.jpeg", "YouTube", "youtube")
with col2:
    social_button("images/X .jpeg", "⠀⠀X⠀⠀", "twitter")  # The key is still "twitter"
with col3:
    social_button("images/Instagram.jpeg", "Instagram", "ig")
with col4:
    social_button("images/Facebook.jpeg", "Facebook", "fb")

if "platform_selected" not in st.session_state:
    st.session_state.platform_selected = None

# Common function to run analysis
def run_analysis(comments):
    if not comments:
        st.warning("No comments found to analyze!")
        return

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
    
    # Check if sentiment_counts has valid values
    if sum(sentiment_counts.values()) == 0:
        st.warning("No valid sentiment data to display!")
        return
    
    # Plot the pie chart
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
                comments = fetch_youtube_comments(video_id, os.getenv("YOUTUBE_API_KEY"))
                if not comments:
                    st.warning("No comments found for this video!")
                else:
                    run_analysis(comments)
            else:
                st.error("Invalid YouTube URL!")
    elif st.session_state.platform_selected == "twitter":
        tweet_url = st.text_input("Enter the Tweet URL:")
        if st.button("Analyze"):
            tweet_id = extract_tweet_id(tweet_url)
            tweets = fetch_tweets(tweet_id, os.getenv("TWITTER_API_KEY"))
            if not tweets:
                st.warning("No tweets found for this URL!")
            else:
                run_analysis(tweets)
    else:
        st.warning("🚀 Check back later! Support for this platform is coming soon.")
