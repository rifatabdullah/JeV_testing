# Defining the target Structure 

import os
from pydantic import BaseModel, Field
from openai import OpenAI
from pydantic import ValidationError
from dotenv import load_dotenv

load_dotenv("config/.env")

class CharacterSheet(BaseModel):
    name: str = Field(description="The full name of the character")
    character_class: str = Field(description="RPG class, e.g. Rogue, Wizard, Warrior")
    level: int = Field(ge=1, le=100, description="Level between 1 and 100")
    abilities: list[str] = Field(description="List of 3 primary special abilities")
    
    
## Request Structured Output


client = OpenAI(
    base_url= "https://openrouter.ai/api/v1",
    api_key=os.getenv ("OpenRouter_API_KEY")
)

prompt =  "Create a level 5 elven rogue named Lyra with stealth-based moves."

try:
    #Asking the api to format the response into our Pydantic model 
    
    completion = client.beta.chat.completions.parse(
        model = "gpt-4o-mini",
        messages=[
            {"role":"system","content": "You are a helpful assistant that generates character sheets."},
            {"role":"user","content":prompt}
        ],
        response_format=CharacterSheet    
    )
    
# Extract the validated Pydantic object
    character: CharacterSheet = completion.choices[0].message.parsed

    # Access fields directly with auto-completion & type safety
    print(f"Name: {character.name}")
    print(f"Class: {character.character_class} (Level {character.level})")
    print(f"Abilities: {', '.join(character.abilities)}")

except ValidationError as e:
    # Handles cases where data failed Pydantic's internal validation
    print("AI output did not conform to the schema:")
    print(e)

except Exception as e:
    # Handles API connection issues, missing keys, or network failures
    print(f"An unexpected error occurred: {e}")