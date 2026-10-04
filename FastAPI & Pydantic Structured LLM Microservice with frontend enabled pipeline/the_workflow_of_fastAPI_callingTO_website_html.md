[ User types prompt in HTML UI ]
             │
             ▼
[ JavaScript sends HTTP POST request ]
   fetch("http://127.0.0.1:8000/generate_character", {
       method: "POST",
       body: JSON.stringify({ prompt: "Create a level 5 elven rogue named Lyra." })
   })
             │
             ▼
[ FastAPI Endpoint: /generate_character ]
   1. Validates input with `PromptRequest`
   2. Calls OpenRouter LLM (`gpt-4o-mini`)
   3. Parses output into `CharacterSheet` Pydantic model
   4. Sends back JSON: {"name": "Lyra", "character_class": "Rogue", "level": 5, "abilities": [...]}
             │
             ▼
[ JavaScript receives JSON response ]
   1. Updates DOM elements (`cardName.textContent = data.name`)
   2. Renders the interactive character card UI visually!