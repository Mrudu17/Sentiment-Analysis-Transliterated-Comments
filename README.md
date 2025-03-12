# 🌟 **Sentiment Analysis of Transliterated Social Media Comments** 🌟

## 🧑‍💻 **Developed by:**
- **S.K. Mruduvani**  |  [GitHub Profile](https://github.com/Mrudu17) | [LinkedIn Profile](https://www.linkedin.com/in/s-k-mruduvani)
- **Kataru Shreya**  |  [GitHub Profile](https://github.com/KataruShreya) | [LinkedIn Profile](https://www.linkedin.com/in/shreyakataru)

---

## 📜 **Project Overview**

Welcome to **Sentiment Analysis of Transliterated Social Media Comments**! This project dives into analyzing the sentiment of social media comments, specifically from **YouTube** and **Twitter** (X), using **Natural Language Processing (NLP)** techniques. The goal is to assess the overall mood (positive, negative, or neutral) of user comments on various platforms and provide insightful analysis for content creators and marketers.

---

## 🚀 **How It Works**

### 1. **Platform Selection:**
- You can choose to analyze comments from **YouTube**, **Twitter**, or **Instagram** (coming soon). Simply click on the platform of your choice.

### 2. **Input Your URL:**
- For **YouTube**: Paste the URL of a YouTube video to fetch the latest comments.
- For **Twitter**: Paste the URL of a tweet to fetch the replies.

### 3. **Processing & Analysis:**
- The application will **preprocess** the comments by removing unnecessary text like URLs, emojis, and handles, while keeping non-ASCII characters (such as Telugu).
- **Sentiment Analysis** will then classify each comment as either **positive**, **negative**, or **neutral**.
- **Translation**: If comments are not in English, they will be automatically **transliterated and translated** to English for analysis.

### 4. **Results:**
- The app will present a **detailed analysis** of the comments, along with a **pie chart** showing the sentiment distribution.
- You can download the results in **CSV** format for further analysis.

---

## 🔧 **Technologies Used**
- **Python** (Core Language)
- **Streamlit** (Interactive Web Interface)
- **Google YouTube API** (Fetching YouTube comments)
- **Twitter API** (Fetching tweets)
- **TextBlob** (Sentiment Analysis)
- **Googletrans** (Translation)
- **Matplotlib** (Data Visualization)

---

## 🌍 **Features**

### 🎯 **Sentiment Analysis**:
Using the **TextBlob** library, the sentiment of each comment is analyzed. The polarity of the text determines if it's **positive**, **negative**, or **neutral**.

### 🌐 **Multilingual Handling**:
Supports multiple languages and retains non-ASCII characters like **Telugu** while removing unwanted characters (e.g., emojis).

### 📊 **Data Visualization**:
A **pie chart** visualizes the sentiment distribution, showing you how people feel overall about the content.

### 📥 **Downloadable Results**:
Once the analysis is complete, the results can be downloaded in a **CSV** format to further study or integrate into other applications.

---

## 📈 **Use Case Scenarios**

- **Content Creators**: Get insights into how your audience is reacting to your YouTube videos or Twitter posts.
- **Marketing Teams**: Monitor customer feedback on social media, and identify the overall sentiment toward your brand.
- **Researchers**: Analyze public opinion on specific topics by collecting comments from social media.

---

## 🔑 **Setup & Installation**

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Mrudu17/Sentiment-Analysis-Social-Media-Comments.git
   cd Sentiment-Analysis-Social-Media-Comments

