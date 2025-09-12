# tools/story_generator.py

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

def get_story_chain():
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.85,   # thoda creative
        max_output_tokens=1000
    )

    prompt = PromptTemplate(
        input_variables=["history", "user_input"],
        template=(
            "You are a skilled creative storyteller helping Indian artisans share their craft stories.\n"
            "You will be given the previous conversation for context and the latest user input.\n\n"
            "Conversation history:\n{history}\n\n"
            "User request:\n{user_input}\n\n"
            "Now, generate a complete, engaging, and emotionally rich story. "
            "The story should:\n"
            "- Be written in clear English and hindi.\n"
            "- Highlight the theme, characters, and setting naturally.\n"
            "- Be 2–5 paragraphs long.\n"
            "- Flow like a narrative (not bullet points).\n\n"
            "Final Story:"
        )
    )

    return LLMChain(llm=llm, prompt=prompt)
