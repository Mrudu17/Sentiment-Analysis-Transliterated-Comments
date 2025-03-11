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

# Function to extract video ID from URL
def extract_video_id(url):
    if "youtube.com/watch?v=" in url:
        return url.split("v=")[1].split("&")[0]
    return None

# Function to extract tweet ID from URL
def extract_tweet_id(url):
    return url.strip('/').split("/")[-1]

# Preprocess Comment (Preserve Telugu and other non-ASCII characters)
# Preprocess Comment (Preserve Telugu and other non-ASCII characters, remove URLs, Twitter handles, and emojis)
def preprocess_comment(comment):
    # Remove emojis
    comment = re.sub(r'[^\x00-\x7F]+', '', comment)  # This removes non-ASCII characters including emojis
    
    # Remove URLs
    comment = re.sub(r'http[s]?://\S+|www\.\S+', '', comment)
    
    # Remove HTML tags
    comment = re.sub(r'<.*?>', '', comment)
    
    # Remove Twitter handles
    comment = re.sub(r'@\w+', '', comment)
    
    # Remove extra spaces
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

# Fetch tweets using Twitter API
def fetch_tweets(tweet_id, api_key):
    conn = http.client.HTTPSConnection("twitter-api45.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': "68acfccf96msh43988501728891ep174caejsna4f16e4418ad",
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
        # Replace with your RapidAPI key and endpoint
        rapidapi_key = "68acfccf96msh43988501728891ep174caejsna4f16e4418ad"  # Replace with your actual RapidAPI key
        url = "https://translation-api4.p.rapidapi.com/translation"

        # Querystring for target language (Translate text to English)
        querystring = {"from": "auto", "to": "en", "query": text}  # Translate text to English
        
        headers = {
            "x-rapidapi-key": rapidapi_key,
            "x-rapidapi-host": "translation-api4.p.rapidapi.com"
        }

        # Make the request to RapidAPI
        response = requests.get(url, headers=headers, params=querystring)

        if response.status_code == 200:
            try:
                # Parse the response JSON
                translation = response.json()
                return translation.get('translation', 'No translation found')  # Use 'translation' as the key
            except Exception as e:
                return None
        else:
            return None
    except Exception as e:
        return None

# Streamlit UI
st.markdown("<h1 style='text-align: center;'>Sentiment Analysis of Transliterated Social Media Comments</h1>", unsafe_allow_html=True)

st.markdown("<h4 style='text-align: center;'>Select a platform to analyze comments</h4>", unsafe_allow_html=True)

# Display Team Information
# Display Team Information at the bottom-right of the screen with link symbols
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




col1, col2, col3, col4 = st.columns(4)

def social_button(icon_url, label, key):
    st.image(icon_url, width=50)
    
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


# Use raw URLs to GitHub images
github_base_url = "https://raw.githubusercontent.com/Mrudu17/Sentiment-Analysis-Transliterated-Comments/main/images/"

with col1:
    social_button(f"images/Youtube.jpeg", "YouTube", "youtube")
with col2:
    social_button(f"images/Twitter.jpeg", "⠀⠀X⠀⠀", "twitter")  # The key is still "twitter"
with col3:
    social_button(f"images/Instagram.jpeg", "Instagram", "ig")
with col4:
    social_button(f"images/Facebook.jpeg", "Facebook", "fb")

if "platform_selected" not in st.session_state:
    st.session_state.platform_selected = None

# Common function to run analysis
# Common function to run analysis
def run_analysis(comments):
    total_comments = len(comments)
    sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
    translations = []
    
    # Track if any valid comments exist
    valid_comments_count = 0
    
    progress_bar = st.progress(0)
    
    for i, comment in enumerate(comments):
        preprocessed_comment = preprocess_comment(comment)
        
        # Skip empty or irrelevant comments after preprocessing
        if not preprocessed_comment.strip():
            continue  # Skip this iteration if the comment is empty or just whitespace
        
        # Translate and analyze valid comments only
        translated_text = transliterate_and_translate(preprocessed_comment)
        
        if translated_text:
            sentiment = analyze_sentiment(translated_text)
            sentiment_counts[sentiment['sentiment']] += 1
            translations.append({
                'Original Comment': comment,
                'Preprocessed Comment': preprocessed_comment,  # Added this line
                'Translated Comment': translated_text,
                'Sentiment': sentiment['sentiment']
            })
            valid_comments_count += 1
        
        progress_bar.progress(min(int(((i + 1) / total_comments) * 100), 100))
    
    # Check if there were no valid comments to analyze
    if valid_comments_count == 0:
        st.warning("No valid comments found for analysis!")
        return
    
    df = pd.DataFrame(translations)
    st.success("Analysis complete!")
    st.dataframe(df)
    
    # CSV download with the new 'Preprocessed Comment' column
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", data=csv, file_name="sentiment_analysis.csv", mime="text/csv")
    
    # Plot sentiment distribution, handle zero values in sentiment counts
    fig, ax = plt.subplots(figsize=(2, 2))
    
    # Remove categories with zero count to avoid plotting them
    non_zero_sentiments = {k: v for k, v in sentiment_counts.items() if v > 0}
    
    if non_zero_sentiments:  # Ensure there's at least one sentiment to plot
        ax.pie(
            non_zero_sentiments.values(),
            labels=non_zero_sentiments.keys(),
            autopct='%1.1f%%',
            colors=['green', 'red', 'gray'][:len(non_zero_sentiments)],  # Ensure the number of colors matches
            textprops={'color': 'white'}
        )
        ax.set_title("Sentiment Distribution", fontsize=8, fontweight='bold', color='white')
        fig.patch.set_facecolor("#0E1117")
        ax.set_facecolor("#0E1117")
        st.pyplot(fig)
    else:
        st.warning("No sentiments to plot (all sentiments are zero).")
    
    # Display overall sentiment
    most_common_sentiment = max(non_zero_sentiments, key=non_zero_sentiments.get, default=None)
    
    if most_common_sentiment:
        sentiment_percentage = (non_zero_sentiments[most_common_sentiment] / sum(non_zero_sentiments.values())) * 100
        st.markdown(f"""
        <div style='text-align: center;'>
            <h2 style="color: white; font-size: 30px; font-weight: bold;">Overall Sentiment</h2>
            <h2 style="color: white; font-size: 25px;">{most_common_sentiment.capitalize()} ({sentiment_percentage:.2f}%)</h2>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("No dominant sentiment found.")


if st.session_state.platform_selected:
    if st.session_state.platform_selected == "youtube":
        youtube_url = st.text_input("Enter the YouTube video URL:")
        if st.button("Analyze"):
            video_id = extract_video_id(youtube_url)
            if video_id:
                run_analysis(fetch_youtube_comments(video_id, "AIzaSyBjkB-c3lvG0dSyoQ0Byij5FLrhaewIilg"))
            else:
                st.error("Invalid YouTube URL!")
    elif st.session_state.platform_selected == "twitter":
        tweet_url = st.text_input("Enter the Tweet URL:")
        if st.button("Analyze"):
            tweet_id = extract_tweet_id(tweet_url)
            run_analysis(fetch_tweets(tweet_id, "68acfccf96msh43988501728891ep174caejsna4f16e4418ad"))
    else:
          st.warning("🚀 Check back later! Support for this platform is coming soon.")
