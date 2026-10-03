import os 
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool 
from langgraph.prebuilt import create_react_agent

load_dotenv()

# OpenRouter LLM

llm = ChatOpenAI(
    model = "openai/gpt-4o-mini",
    openai_api_key = os.getenv("OpenRouter_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    temperature=0
)

# Custom Tools 
@tool
def multiply(a:int, b:int) -> int:
    """Multiplies two integers together."""
    return a*b

@tool
def add(a:int, b:int) -> int:
    """Adds two integers together."""
    return a + b 

tools = [multiply, add]

# ReAct Agent executor 
agent = create_react_agent(llm,tools)

# Invoke Agent

inputs = {"messages": [("user","What is 12 multiplied by 5, and then add 10 to the result?")]} 


response = agent.invoke(inputs)

print("\nFinal Answers")
print(response["messages"][-1].content)