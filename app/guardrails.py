from fastapi import HTTPException


# insipred by chatgpt
BANNED = {"visa", "immigration advice", "illegal", "fraud"}

def enforce(query: str) -> None:
    q = query.lower()
    if any(b in q for b in BANNED):
        raise HTTPException(status_code=400, detail="Query not allowed. Please ask a travel planning question.")