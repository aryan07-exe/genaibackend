from langchain_core.tools import tool

@tool
def generate_caption_and_hashtags(image_url: str = None, text: str = None) -> str:
    """Generate a catchy caption and hashtags for social media."""
    return "Caption: Handmade pottery 🏺✨\n#Handmade #Pottery #Artisan"

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
