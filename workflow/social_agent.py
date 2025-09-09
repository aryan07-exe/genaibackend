from langchain.agents import initialize_agent, AgentType
from langchain_google_genai import ChatGoogleGenerativeAI
from services.social_tools import generate_ig_caption

# Gemini LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)

# Register tools
tools = [generate_ig_caption]

# Create ReAct Agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)

def run_social_agent(input_data: dict) -> str:
    """
    Run the social media AI agent.
    Accepts {"text": "..."} OR {"image_bytes": b"..."} OR both.
    """

    try:
        # 🟢 Step 1: Convert structured input into a natural language query
        if input_data.get("text") and input_data.get("image_bytes"):
            query = "Generate a caption using this text and the uploaded image."
        elif input_data.get("image_bytes"):
            query = "Generate a caption for the uploaded image."
        elif input_data.get("text"):
            query = f"Generate a caption using this text: {input_data['text']}"
        else:
            return "⚠️ Please provide either text, an image, or both."

        # 🟢 Step 2: Pass both query + raw input_data as context
        response = agent.run(
            f"{query}\n\nRaw input: {input_data}"
        )

        return response

    except Exception as e:
        return f"⚠️ Error: {str(e)}"
