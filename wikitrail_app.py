import streamlit as st
import requests

# === CONFIG ===
st.set_page_config(page_title="WikiTrail — Clean Edition", layout="centered")
HF_API_KEY = "hf_my key here"

# === STYLING: Clean UI with Helvetica ===
st.markdown("""
    <style>
        html, body, [class*="css"] {
            font-family: 'Helvetica', sans-serif;
            background-color: #f8f9fa;
            color: #212529;
        }
        h1, h2, h3 {
            color: #212529;
        }
        .stTextInput>div>div>input,
        .stTextArea>div>textarea {
            background-color: #ffffff;
            color: #212529;
            border: 1px solid #ced4da;
        }
        .stButton>button {
            background-color: #343a40;
            color: white;
            border-radius: 6px;
            padding: 8px 16px;
            border: none;
        }
        .stMarkdown {
            font-size: 16px;
        }
    </style>
""", unsafe_allow_html=True)

# === APP HEADER ===
st.title("📚 WikiTrail — Summarize Smarter")

# === FUNCTION: Fetch Wikipedia article ===
def get_wikipedia_article(title, lang="en"):
    url = f"https://{lang}.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "explaintext": True,
        "redirects": 1,
        "titles": title
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        page = next(iter(data["query"]["pages"].values()))
        return page.get("extract", None)
    except Exception as e:
        return f"❌ Wikipedia Error: {e}"

# === FUNCTION: Summarize using Hugging Face ===
def summarize_text(text):
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}"
    }
    payload = {
        "inputs": text[:2000],  # Truncate safely to avoid crashing Hugging Face
        "parameters": {
            "max_length": 180,
            "min_length": 80,
            "do_sample": False
        }
    }
    try:
        response = requests.post(
            "https://api-inference.huggingface.co/models/facebook/bart-large-cnn",
            headers=headers,
            json=payload,
            timeout=40
        )
        result = response.json()
        if isinstance(result, list):
            return result[0]["summary_text"]
        elif "error" in result:
            return f"❌ Hugging Face Error: {result['error']}"
        else:
            return "⚠️ Unexpected API response."
    except Exception as e:
        return f"❌ HF Exception: {e}"

# === SIDEBAR ===
with st.sidebar:
    st.header("⚙️ Settings")
    language = st.text_input("Wikipedia Language (e.g., en, hi)", value="en")

# === MAIN SEARCH ===
topic = st.text_input("🔍 Enter a Wikipedia Topic", placeholder="E.g., World War II, Carl Jung")

if st.button("📖 Get Article & Summary"):
    if not topic.strip():
        st.warning("Please enter a topic.")
    else:
        with st.spinner("📡 Fetching article..."):
            article = get_wikipedia_article(topic.strip(), lang=language.strip())

        if not article:
            st.error("❌ No article content found.")
        elif article.startswith("❌"):
            st.error(article)
        else:
            st.subheader("📜 Wikipedia Article")
            st.text_area("Full Extract", article[:3000], height=300)

            with st.spinner("🧠 Summarizing..."):
                summary = summarize_text(article)
            st.subheader("🧠 AI Summary")
            st.markdown(f"> {summary}")
