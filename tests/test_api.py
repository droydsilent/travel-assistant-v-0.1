import pytest
from fastapi.testclient import TestClient
from app.main import app
from app import retriever, schemas

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

def test_health(client):
    """Basic health endpoint should return healthy status."""
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("status") == "healthy"

def test_travel_assistant_contract(client, monkeypatch):
    """
    The /travel-assistant endpoint should return a TravelAdvice-shaped JSON.
    We stub out the generator to avoid live LLM calls in CI.
    """

    def fake_generate(_q: schemas.TravelQuery) -> schemas.TravelAdvice:
        return schemas.TravelAdvice(
            destination="Tokyo",
            reason="Top food scene in September using seed data.",
            budget="Moderate",
            tips=["Eat sushi", "Use Suica", "Stay near JR lines"]
        )

    # Patch via module reference (preferred app code: `from app import retriever` then `retriever.generate_travel_advice(...)`)
    monkeypatch.setattr(retriever, "generate_travel_advice", fake_generate, raising=True)

    # If your route imported the function directly (e.g., `from app.retriever import generate_travel_advice`),
    # also patch that symbol on the app.main module so the stub takes effect.
    import app.main as main_module
    if hasattr(main_module, "generate_travel_advice"):
        monkeypatch.setattr(main_module, "generate_travel_advice", fake_generate, raising=True)

    resp = client.post("/travel-assistant", json={"query": "Solo foodie trip to Asia in September"})
    assert resp.status_code == 200

    # Validate shape by parsing into the Pydantic model
    data = resp.json()
    advice = schemas.TravelAdvice(**data)

    assert advice.destination == "Tokyo"
    assert advice.budget in {"Low", "Moderate", "High"}
    assert isinstance(advice.tips, list) and len(advice.tips) == 3