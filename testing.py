import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Loading env variables from .env
load_dotenv()


# LLM via OpenRouter
llm = ChatOpenAI(
    model = "openai/gpt-4o-mini",
    openai_api_key = os.getenv("OpenRouter_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    temperature=0
    
)

# Testing 

response = llm.invoke("Hi! Confirm Connection in 5 words.")
print("Response: ")
print(response.content)