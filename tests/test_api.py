from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"

def test_travel_assistant_contract(monkeypatch):
    # Patch service to avoid live LLM in CI
    from app import retriever
    from app import schemas

    print(schemas.TravelAdvice)

    def fake_generate(_):
        return schemas.TravelAdvice(
            destination="Tokyo",
            reason="Top food scene in September using seed data.",
            budget="Moderate",
            tips=["Eat sushi", "Use Suica", "Stay near JR lines"]
        )

    monkeypatch.setattr(retriever, "generate_travel_advice", fake_generate)
    r = client.post("/travel-assistant", json={"query": "Solo foodie trip to Asia in September"})
    assert r.status_code == 200
    body = r.json()
    assert body["destination"] == "Tokyo"
    assert isinstance(body["tips"], list) and len(body["tips"]) == 3