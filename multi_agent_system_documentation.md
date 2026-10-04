# 🤖 LangGraph Multi-Agent System Documentation

This document provides a complete guide and architectural reference for building multi-agent AI systems using **LangGraph**, **Pydantic**, and **OpenRouter (GPT-4o-mini)**.

---

## 🗺️ 1. Architecture Structure Map

The following diagram illustrates how execution state flows dynamically through the multi-agent graph:

```text
               ┌──────────┐
               │  START   │
               └────┬─────┘
                    │
                    ▼
          ┌───────────────────┐
          │ Supervisor Router │ ◄────────────────┐
          └─────────┬─────────┘                  │
                    │                            │
      ┌─────────────┼─────────────┐              │
      │             │             │              │
      ▼             ▼             ▼              │
┌───────────┐ ┌───────────┐ ┌───────────┐        │
│Researcher │ │  Writer   │ │   END     │        │
└─────┬─────┘ └─────┬─────┘ └───────────┘        │
      │             │                            │
      └─────────────┴────────────────────────────┘
         (Appends message & routes back)
```

### Execution Flow 🔄

1. **Entry Point:** Execution begins at `START`, which routes directly to the `Supervisor Router`.
2. **Dynamic Decision:** The Supervisor inspects the `AgentState` history and decides which worker should act next (`"researcher"`, `"writer"`, or `"FINISH"`).
3. **Worker Execution:** The selected worker node executes its task, appends its result to `AgentState["messages"]`, and hands control back to the `Supervisor Router`.
4. **Completion:** When all worker tasks are satisfied, the Supervisor returns `"FINISH"`, terminating the execution at `END`.

---

## 📚 2. Core Concepts & Theory

| Concept | Description | Code Signature / Marker |
| :--- | :--- | :--- |
| **Shared State** 💾 | The shared memory notebook passed between all nodes during execution. | `class AgentState(TypedDict):` |
| **Reducer Function** ➕ | Prevents state overwriting by instructing LangGraph to append new outputs to existing history. | `Annotated[list, add_messages]` |
| **Worker Nodes** 🧩 | Independent functions that perform a single specialized task and return state updates. | `def researcher_node(state):` |
| **Conditional Edges** 🔀 | Dynamic graph edges that direct control flow based on state evaluation. | `builder.add_conditional_edges()` |
| **Route Map** 🗺️ | A dictionary lookup translating decision strings from the router to physical graph node names. | `{"researcher": "researcher", ...}` |
| **Structured Output** 🎯 | Forces the LLM to output responses adhering strictly to a Pydantic schema. | `llm.with_structured_output()` |

---

## 🔀 3. Routing Logic Evolution

### Stage A: Hardcoded Logic (Tag Matching)
* **Mechanism:** Iterates over `state["messages"]` looking for hardcoded string tags (e.g., `"[Research Notes]"`).
* **Pros:** Simple, deterministic, and clear for basic 2-node linear graphs.
* **Cons:** Fragile. Fails if text formatting changes slightly or if scaled to many agents with overlapping responsibilities.

### Stage B: LLM-Powered Supervisor (Structured Output)
* **Mechanism:** Uses `gpt-4o-mini` with a Pydantic `BaseModel` containing `Literal` field choices to choose the next node.
* **Pros:** Highly flexible, scalable, resilient to formatting variations, and capable of intelligent task planning.
* **Cons:** Requires precise system prompts and additional API tokens for supervisor decisions.

---

## 💻 4. Complete Code Implementation

```python
import os
from typing import TypedDict, Annotated, Literal
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

# 1. Environment Setup
load_dotenv()

# 2. Initialize OpenRouter LLM 🧠
llm = ChatOpenAI(
    model="openai/gpt-4o-mini",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    temperature=0
)

# 3. Shared State Definition 💾
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

# 4. Worker Nodes 🧩
def researcher_node(state: AgentState):
    user_topic = state["messages"][0].content
    response = llm.invoke(f"List 2 quick key facts about: {user_topic}")
    return {"messages": [("assistant", f"Research Facts:\n{response.content}")]}

def writer_node(state: AgentState):
    research_notes = state["messages"][-1].content
    response = llm.invoke(f"Turn these facts into a short post:\n{research_notes}")
    return {"messages": [("assistant", f"Final Draft:\n{response.content}")]}

# 5. Pydantic Schema for LLM Supervisor Decision 🛡️️
class RouterDecision(BaseModel):
    next_node: Literal["researcher", "writer", "FINISH"] = Field(
        description="Select 'researcher' to gather facts, 'writer' to write the summary, or 'FINISH' when complete."
    )

structured_llm = llm.with_structured_output(RouterDecision)

# 6. Dynamic Supervisor Node 🧑‍💼
def supervisor_router(state: AgentState) -> str:
    system_prompt = (
        "You are a supervisor directing a workflow.\n"
        "- Choose 'researcher' if research has not been gathered yet.\n"
        "- Choose 'writer' if research is present but no summary/draft exists.\n"
        "- Choose 'FINISH' if both research and draft are completed."
    )
    
    prompt = [("system", system_prompt)] + state["messages"]
    decision = structured_llm.invoke(prompt)
    
    return decision.next_node

# 7. Assemble the Graph 🎼
builder = StateGraph(AgentState)

# Add Worker Nodes
builder.add_node("researcher", researcher_node)
builder.add_node("writer", writer_node)

# Map decision values to node names
route_map = {
    "researcher": "researcher",
    "writer": "writer",
    "FINISH": END
}

# Attach conditional edges
builder.add_conditional_edges(START, supervisor_router, route_map)
builder.add_conditional_edges("researcher", supervisor_router, route_map)
builder.add_conditional_edges("writer", supervisor_router, route_map)

# 8. Compile and Execute Graph 🚀
graph = builder.compile()

if __name__ == "__main__":
    result = graph.invoke({"messages": [("user", "U-2 Spyplane")]})

    for msg in result["messages"]:
        print(f"\n--- {msg.type.upper()} ---")
        print(msg.content)
```