from langchain_core.tools import tool
import requests
from bs4 import BeautifulSoup
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI


def scrape_hashtags(keyword: str, max_tags: int = 15):
    """Scrape hashtags from best-hashtags.com"""
    try:
        url = f"https://best-hashtags.com/hashtag/{requests.utils.requote_uri(keyword)}/"
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)

        if response.status_code != 200:
            return ["#trending", "#viral", "#explore"]

        soup = BeautifulSoup(response.text, "html.parser")
        tag_box = soup.find("div", {"class": "tag-box"})

        if not tag_box:
            return ["#creative", "#socialmedia"]

        hashtags = tag_box.text.strip().split()
        return hashtags[:max_tags]

    except Exception:
        return ["#instagood", "#explorepage", "#viral"]


@tool
def generate_caption_and_hashtags(image_url: str = None, text: str = None) -> str:
    """Generate a catchy caption and trending hashtags for social media posts using optional image + description."""

    if not image_url and not text:
        return "❌ Please provide at least an image or some description."

    # Prompt for LLM
    prompt = ChatPromptTemplate.from_template("""
    You are a professional social media manager.
    Write a short, catchy caption for Instagram using the given inputs.

    Image URL: {image_url}
    Description: {text}

    Rules:
    - Keep under 25 words
    - Add 1–2 emojis that match the vibe
    - Make it engaging and audience-friendly
    """)

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)
    messages = prompt.format_messages(image_url=image_url or "None", text=text or "")
    caption = llm.invoke(messages).content

    # Pick keyword for hashtags (from text if present, else fallback)
    keyword = (text.split()[0] if text else "trending").lower()
    hashtags = scrape_hashtags(keyword)

    return f"✨ Caption: {caption}\n🏷 Hashtags: {' '.join(hashtags)}"


@tool
def enhance_post(text: str) -> str:
    """Make a user’s social media text more catchy and engaging."""
    return f"✨ {text} ✨ — Support local artisans! #SupportLocal"

@tool
def write_product_description(product_name: str, details: str) -> str:
    """Write an SEO-friendly product description for marketplaces."""
    return f"{product_name}: {details}. Eco-friendly, handcrafted with care."

@tool
def content_planner(theme: str) -> str:
    """Suggest a weekly posting plan for a given theme."""
    return f"Plan:\nMon - Behind the scenes\nWed - Product Highlight\nFri - Customer Story\nSun - Festival Special"
