# app/main.py
from fastapi import FastAPI, HTTPException
from schemas import TravelQuery, TravelAdvice
from dotenv import load_dotenv
from retriever import generate_travel_advice

load_dotenv()
app = FastAPI(title="Virgin Atlantic GenAI Travel Assistant")

@app.post("/travel-assistant", response_model=TravelAdvice)
def travel_assistant(query: TravelQuery):
    try:
        return generate_travel_advice(query)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")

@app.get("/")
def read_root():
    return {"message": "Travel Assistant API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}