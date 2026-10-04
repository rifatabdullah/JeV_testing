import os
from typing import TypedDict, Annotated
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END 
from langgraph.graph.message import add_messages 

# Loading environment variables from the .env file  

load_dotenv("config/.env") # from the <os> library 


# Open Router LLM

llm = ChatOpenAI(
    model = "openai/gpt-4o-mini",
    openai_api_key = os.getenv("OpenRouter_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    temperature=0
    
)

# Shared State / notebook for all the agents 

class AgentState(TypedDict): # from the <typing> library 
    messages: Annotated[list, add_messages]
    

## Nodes / Individual agents 
'''Each node accepts state, reads messages from it, runs the LLM, and returns a dictionary with key messages. Because of add_messages, this returned dictionary appends the new message to the state history.'''


# Node1: Researcher

def research_node(state: AgentState):
    user_topic = state["messages"][0].content 
    response = llm.invoke(f"List 2 quick key facts about: {user_topic}")
    return {"messages":[("assistant", f"[Research Notes]]\n{response.content}")]}


# Node2: Writer

def writer_node(state: AgentState):
    # Research findings from the last message in state 
    research_notes = state["messages"][-1].content 
    response = llm.invoke(f"Turn these notes into a 1-sentence post:\n{research_notes}")
    
    return {"messages": [("assistant", f"[Final Post]\n{response.content}")]}



#w Node 3 : Supervisor 

def supervisor_node(state: AgentState) -> str:
    has_research = False
    has_summary = False 
    
    # Checking each messages one by one and then passing
    
    for i in state["messages"]:
        text = i.content
        if "[Research Notes]" in text:
            has_research = True
        if "[Final Post]" in text:
            has_summary = True
        
        
    # Routing based on the boolean variables
    
    if not has_research:
        return "researcher"
    elif not has_summary:
        return "writer"
    else:
        return "FINISH"
      

# Assemble the graph
builder = StateGraph(AgentState)

# Add nodes together 


builder.add_node("researcher",research_node)
builder.add_node("writer", writer_node)

route_map = {
    "researcher":"researcher",
    "writer":"writer",
    "FINISH": END
}

builder.add_conditional_edges(START,supervisor_node,route_map)
builder.add_conditional_edges("researcher",supervisor_node,route_map)
builder.add_conditional_edges("writer",supervisor_node,route_map)



# Compile into executable Graph

graph = builder.compile()

# Execute
result = graph.invoke({"messages":[("user", "U-2 Dragon Fly")]})

for i in result["messages"]:
    print(f"\n{i.type.upper()}")
    print(i.content)