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
## How to Create YouTube & Twitter API from RapidAPI and Use in Streamlit

# Step 1: Create YouTube API Key from Google Cloud

1. Go to [Google Cloud Console](https://console.cloud.google.com/) and sign in.
2. Click **Select a Project** → **New Project** → Give it a name.
3. Navigate to **APIs & Services** → **Library**.
4. Search for **YouTube Data API v3** and enable it.
5. Go to **APIs & Services** → **Credentials**.
6. Click **Create Credentials** → **API Key**.
7. Copy the generated API Key.

# Step 2: Create Twitter API Key from RapidAPI

1. Go to [RapidAPI](https://rapidapi.com/) and sign in.
2. Search for **Twitter API** in the RapidAPI marketplace.
3. Select an API and subscribe to a pricing plan (free or paid).
4. Navigate to the **Endpoints** section to test API requests.
5. Copy the **API Key** from the **Header Parameters** section.

# Step 3: Create a `secrets.toml` File in Streamlit

1. Inside your Streamlit project, create a `.streamlit` folder.
2. Inside `.streamlit`, create a `secrets.toml` file.
3. Add the API keys to the `secrets.toml` file:

```toml
# .streamlit/secrets.toml
Youtube_API_Key = "Your_Youtube_API_Key"
Twitter_API_Key = "Your_Twitter_API_Key"
```

# Step 4: Clone the repository

   ```bash
   git clone https://github.com/Mrudu17/Sentiment-Analysis-Social-Media-Comments.git
   cd Sentiment-Analysis-Social-Media-Comments
```

# Step 5: Run Streamlit App
```bash
streamlit run app.py
```

---
## Now, your Streamlit app can securely access and use the YouTube and Twitter APIs!
---

## OUTPUTS
![image](https://github.com/user-attachments/assets/81175421-53b3-4998-b3bb-63554f481424)
![image](https://github.com/user-attachments/assets/232bdc64-7aa1-44e9-a2cc-65c8cec89665)
![image](https://github.com/user-attachments/assets/457ca1e2-179c-4c7c-b06e-a3b4d0ad93f9)
![image](https://github.com/user-attachments/assets/43245899-2d27-4cfd-98fe-76fed7f58129)
![image](https://github.com/user-attachments/assets/f01ce591-73c5-43b3-b570-d7f79efaacb2)







