import os 
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from openai import OpenAI
from pydantic import BaseModel, Field 

load_dotenv("config/.env")

app = FastAPI(title="RPG Character Generator")

@app.get("/")
async def serve_ui():
    return FileResponse("index.html")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from any HTML frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key = os.getenv("OpenRouter_API_KEY")
)

# 1. Pydantic Model for Incoming API Request Body
class PromptRequest(BaseModel):
    prompt: str = Field(..., example="Create a level 5 elven rogue named Lyra.")

# 2. Pydantic Model for Outgoing API Response (and LLM Structured Output)
class CharacterSheet(BaseModel):
    name: str = Field(description="The full name of the character")
    character_class: str = Field(description="RPG class, e.g. Rogue, Wizard, Warrior")
    level: int = Field(ge=1, le=100, description="Level between 1 and 100")
    abilities: list[str] = Field(description="List of 3 primary special abilities")
    
    
    
# FASTAPI Route Handler

@app.post("/generate_character", response_model=CharacterSheet)
async def generate_character_endpoint(request: PromptRequest):
    try:
        #The raw object returned by the OpenAI API function call
        completion = client.beta.chat.completions.parse( 
            
            model="openai/gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that generates character sheets.",
                },
                {"role": "user", "content": request.prompt},
            ],
            response_format=CharacterSheet,
        )

        character = completion.choices[0].message.parsed
        if not character:
            raise HTTPException(status_code=500, detail="Failed to parse LLM response.")

        return character  # FastAPI automatically serializes this Pydantic object to JSON

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))