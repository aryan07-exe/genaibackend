from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
import requests
import random

# Gemini LLM (multimodal)
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)


def scrape_hashtags(query: str) -> list[str]:
    """Scrape trending hashtags for a query using all-hashtag.com"""
    try:
        url = "https://www.all-hashtag.com/library/contents/ajax/hashtag-generator.php"
        params = {"keyword": query, "filter": "top"}
        res = requests.post(url, data=params, timeout=10)
        res.raise_for_status()
        hashtags = res.text.strip().split()
        return random.sample(hashtags, min(10, len(hashtags)))
    except Exception:
        return ["#trending", "#viral", "#instagood"]


@tool("generate_ig_caption")
def generate_ig_caption(input_data: dict) -> str:
    """
    Create a trendy Instagram caption + hashtags.
    
    Accepts:
    - {"text": "..."}
    - {"image_bytes": b"..."}   # raw bytes if uploaded from device
    - {"text": "...", "image_bytes": b"..."}  # both together
    """

    query_parts = []

    # 🔹 If image uploaded → ask Gemini to describe it
    if input_data.get("image_bytes"):
        img_bytes = input_data["image_bytes"]

        response = llm.invoke([
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this image in one catchy sentence for social media captioning."},
                    {"type": "image", "image": img_bytes}
                ]
            }
        ])
        image_desc = response.content if isinstance(response.content, str) else str(response.content)
        query_parts.append(image_desc)

    # 🔹 If text provided → include it
    if input_data.get("text"):
        query_parts.append(input_data["text"])

    # 🔹 If nothing provided
    if not query_parts:
        return "⚠️ Please provide either text, an image, or both."

    # Combine inputs
    query = " - ".join(query_parts)

    # 🔹 Hashtags
    hashtags = scrape_hashtags(query)
    caption = f"✨ {query.capitalize()} ✨\n\n" + " ".join(hashtags)
    return caption
