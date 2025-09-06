from typing import TypedDict
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from services.social_tool import (
    generate_caption_and_hashtags,
    enhance_post,
    write_product_description,
    content_planner,
)
from langgraph.graph import MessagesState

class AgentState(MessagesState):
    remaining_steps: int

SYSTEM_PROMPT = """
You are an AI assistant helping artisans grow their social media presence.
You can use tools to:
1. Generate captions & hashtags
2. Enhance posts
3. Write product descriptions
4. Suggest content plans
Decide the best tool based on user input.
"""

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7,
    convert_system_message_to_human=True
)

tools = [generate_caption_and_hashtags, enhance_post, write_product_description, content_planner]
llm_with_tools = llm.bind_tools(tools)

social_media_workflow = create_react_agent(
    model=llm_with_tools,
    tools=tools,
    state_schema=AgentState,
    prompt=SYSTEM_PROMPT
)
