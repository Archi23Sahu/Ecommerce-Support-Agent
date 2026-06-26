# api/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import traceback

load_dotenv()

from agent.agent import get_agent

app = FastAPI(title="ShopBot API")

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    reply: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        agent = get_agent()
        result = agent.invoke({"input": req.message})
        reply = result.get("output", "")

        # Clean fallback — use last tool observation
        if not reply or "iteration limit" in reply.lower() or "time limit" in reply.lower():
            steps = result.get("intermediate_steps", [])
            if steps:
                last_observation = steps[-1][1]
                # Filter out error messages from observation
                if last_observation and "Invalid Format" not in last_observation:
                    reply = f"Based on our catalog, here are some options:\n\n{last_observation}"
                else:
                    # Find last valid observation
                    for step in reversed(steps):
                        obs = step[1]
                        if obs and "Invalid Format" not in str(obs):
                            reply = f"Based on our catalog, here are some options:\n\n{obs}"
                            break
                    else:
                        reply = "I couldn't find relevant products. Try searching for 'Kindle', 'Fire tablet', or 'charger'."
            else:
                reply = "I couldn't process your request. Please try again."

        return ChatResponse(reply=reply)

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))