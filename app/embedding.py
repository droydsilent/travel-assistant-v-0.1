import faiss
import openai
import numpy as np
import random, os
from typing import Any, Dict, List
from services.logger_setup import get_logger
from vector_db import load_index
from data_loader import load_seed


logger = get_logger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMB_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")


def flatten_seed_data(seed_data: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    items = []
    for category, records in seed_data.items():
        if category == "hotels":
            for r in records:
                room_price = random.randint(40, 500)
                text = f"name: {r.get('hotel_name','')} - city: {r.get('city','')} - price_per_night: {r.get('room_price',str(room_price))} - rating: {r.get('rating','')} - amenities: {r.get('amenities','')}"
                items.append({
                    "id": r["hotel_id"],
                    "category": category,
                    "text": text
                })
        elif category == "flights":
            for r in records:
                flight_price = random.randint(150, 1500)
                text = f"airline: {r.get('operating_airline','')} - from_airport: {r.get('city_depart','')} - to_airport: {r.get('city_arrive','')} - duration: {r.get('flight_duration','')} - date: {r.get('depart_date','')} - price: {r.get('price', str(flight_price))}"
                items.append({
                    "id": r["flight_id"],
                    "category": category,
                    "text": text
                })
        elif category == "experiences":
            for r in records:
                text = f"name: {r.get('title','')} - city: {r.get('city','')} - price: {r.get('base_price','')} - duration: {r.get('duration_hours','')} - tags: {r.get('tags','')}"
                items.append({
                    "id": r["experience_id"],
                    "category": category,
                    "text": text
                })

        return items


def batch_embedding(flattened_items: List[Dict[str, Any]]):
    BATCH_SIZE = 99  # can tune up to ~100 depending on token size
    count = 0
    embeddings = []
    for i in range(0, len(flattened_items), BATCH_SIZE):
        
        batch_texts = [it["text"] for it in flattened_items[i:i+BATCH_SIZE]]
        response = openai.embeddings.create(
            model=EMB_MODEL,
            input=batch_texts
        )
        for r in response.data:
            embeddings.append(r.embedding)
        
        count =+ 1
        print(f'Api Call Count: {count}')

    return embeddings


index = load_index()
if index.ntotal == 0:
    logger.info("Index is empty.")

    logger.info("Seed data pre-processing")
    seed_data = load_seed()

    logger.info("Seed data Flattenning")
    flattened_data = flatten_seed_data(seed_data)

    logger.info("Embeddings creation - openai batch api calls")
    embeddings = batch_embedding(flattened_data)

    logger.info("Seed data Embeddings")
    dimension = len(embeddings[0])
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings, dtype="float32"))

    logger.info(f"Stored {index.ntotal} travel items in vector DB")