from fastapi import FastAPI, HTTPException
from .schemas import TravelQuery, TravelAdvice
from dotenv import load_dotenv
from .retriever import generate_travel_advice


tags_metadata = [
    {"name": "Health", "description": "Service status and liveness."},
    {"name": "Travel", "description": "Query seeded hotels, flights and  experiences."},
]


load_dotenv()
app = FastAPI(title="Virgin Atlantic GenAI Travel Assistant",
              version="0.1",
              description="A travel assistant that provides recommendations based on seeded data.",
              openapi_tags=tags_metadata
              )


@app.post("/travel-assistant", 
            tags=["Travel"], 
            summary="Generate grounded travel advice",
            description=(
                "Takes a free‑text query, retrieves top seed data (hotels, flights, "
                "experiences), and returns structured advice."
            ),
            response_model=TravelAdvice,
            responses={
                400: {"description": "Bad request / invalid query"},
                500: {"description": "Internal error generating advice"},
            })
def travel_assistant(query: TravelQuery):
    """The `travel_assistant` function is a POST endpoint in a FastAPI application that takes in a
`TravelQuery` object as input and returns a `TravelAdvice` object as output. 
Inside the function, it calls the `generate_travel_advice` function with the provided query to generate
travel advice based on the input data. If an HTTPException is raised during the process, it is
caught and re-raised. Additionally, if any other type of exception occurs, a generic HTTP 500
error response is raised with a message indicating a server error."""
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
    """Health check endpoint to verify the service is running."""
    return {"status": "healthy"}