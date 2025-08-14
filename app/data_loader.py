import json
from pathlib import Path
from typing import Any, Dict, List

BASE = Path(__file__).resolve().parent
print(f'Base: {BASE}')
SEED = BASE / "seed"

def load_seed() -> Dict[str, List[Dict[str, Any]]]:
    files = {
        "hotels": "hotel_catalogue",
        "flights": "flight_catalogue",
        "experiences": "experiences_catalogue",
    }

    result = {}
    for key, filename in files.items():
        file_path = SEED / f"{filename}.json"
        if file_path.exists():
            with file_path.open("r", encoding="utf-8") as f:
                result[key] = json.load(f)
        else:
            result[key] = []

    print(f'Json loader results: {result}')
    return result