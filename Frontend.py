import streamlit as st
import re
import html
import pandas as pd
import matplotlib.pyplot as plt
from googletrans import Translator
from googleapiclient.discovery import build
from textblob import TextBlob

# Function to extract video ID from URL
def extract_video_id(url):
    if "youtube.com/watch?v=" in url:
        return url.split("v=")[1].split("&")[0]
    return None

# Preprocess Comment
def preprocess_comment(comment):
    comment = html.unescape(comment)
    comment = re.sub(r'http[s]?://\S+|www\.\S+', '', comment)
    comment = re.sub(r'<.*?>', '', comment)
    comment = re.sub(r'[^\x00-\x7F]+', '', comment)
    return ' '.join(comment.split())

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

# Sentiment Analysis
def analyze_sentiment(text):
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    sentiment = 'positive' if polarity > 0 else 'negative' if polarity < 0 else 'neutral'
    return {'sentiment': sentiment, 'polarity': polarity}

# Translate Text
def transliterate_and_translate(text):
    if not text.strip():
        return None
    try:
        translator = Translator()
        translation = translator.translate(text, src='auto', dest='en')
        return translation.text
    except Exception:
        return None

# Streamlit UI
st.markdown("<h1 style='text-align: center;'>Sentiment Analysis of Transliterated Social Media Comments</h1>", unsafe_allow_html=True)

st.markdown("<h4 style='text-align: center;'>Select a platform to analyze comments</h4>", unsafe_allow_html=True)

# Column layout for platform buttons
col1, col2, col3, col4 = st.columns(4)

# Platform selection buttons
def social_button(icon_path, label, key):
    st.image(icon_path, width=50)
    if st.button(label, key=key):
        st.session_state.platform_selected = label.lower()

with col1:
    social_button("C:\\Users\\User\\Downloads\\Youtube.jpeg", "YouTube", "yt")
with col2:
    social_button("C:\\Users\\User\\Downloads\\Instagram.jpeg", "Instagram", "ig")
with col3:
    social_button("C:\\Users\\User\\Downloads\\Twitter.jpeg", "Twitter", "tw")
with col4:
    social_button("C:\\Users\\User\\Downloads\\Facebook.jpeg", "Facebook", "fb")

# Session state for inputs
if "platform_selected" not in st.session_state:
    st.session_state.platform_selected = None
if "youtube_url" not in st.session_state:
    st.session_state.youtube_url = ""
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# YouTube Analysis
def run_analysis():
    video_id = extract_video_id(st.session_state.youtube_url)
    if not video_id:
        st.error("Invalid YouTube URL!")
        return
    
    try:
        with st.spinner("Fetching comments..."):
            comments = fetch_youtube_comments(video_id, st.session_state.api_key)
            total_comments = len(comments)  # Total comments fetched
            max_results_per_request = 100  # Number of comments per request

            # Create a progress bar
            progress_bar = st.progress(0)
            translations = []
            sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}

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
                
                # Update the progress bar
                progress_percentage = min(int(((i + 1) / total_comments) * 100), 100)
                progress_bar.progress(progress_percentage)
            
            df = pd.DataFrame(translations)
            st.success("Analysis complete!")
            st.dataframe(df)

            # Download button
            csv = df.to_csv(index=False).encode('utf-8')
            st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
            st.download_button("Download CSV", data=csv, file_name="sentiment_analysis.csv", mime="text/csv")
            st.markdown("</div>", unsafe_allow_html=True)

            # Pie Chart
            fig, ax = plt.subplots(figsize=(2, 2))
            wedges, texts, autotexts = ax.pie(
                sentiment_counts.values(), 
                labels=sentiment_counts.keys(), 
                autopct='%1.1f%%', 
                colors=['green', 'red', 'gray'],
                textprops={'color': 'white'}
            )
            ax.set_title("Sentiment Distribution", fontsize=8, fontweight='bold', color='white')
            for wedge in wedges:
                wedge.set_edgecolor("white")
                wedge.set_linewidth(1)
            fig.patch.set_facecolor("#0E1117")
            ax.set_facecolor("#0E1117")
            
            # Display pie chart
            st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
            st.pyplot(fig)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Overall Sentiment
            most_common_sentiment = max(sentiment_counts, key=sentiment_counts.get)
            sentiment_percentage = (sentiment_counts[most_common_sentiment] / sum(sentiment_counts.values())) * 100
            
            st.markdown(f"""
            <div style='text-align: center;'>
                <h2 style="color: white; font-size: 30px; font-weight: bold;">Overall Sentiment</h2>
                <h2 style="color: white; font-size: 25px;">{most_common_sentiment.capitalize()} ({sentiment_percentage:.2f}%)</h2>
            </div>
            """, unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"Error: {e}")

# Handling platform selection
if st.session_state.platform_selected:
    if st.session_state.platform_selected == "youtube":
        st.session_state.youtube_url = st.text_input("Enter the YouTube video URL:", value=st.session_state.youtube_url)
        st.session_state.api_key = "AIzaSyBjkB-c3lvG0dSyoQ0Byij5FLrhaewIilg"
        if st.button("Analyze"):
            run_analysis()
    else:
        st.warning("🚀 Check back later! Support for this platform is coming soon.")