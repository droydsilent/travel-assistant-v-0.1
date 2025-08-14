from typing import Any, Dict
from pydantic import ValidationError
from .schemas import TravelAdvice, TravelQuery
from .llm import call_llm_with_seed
from .guardrails import enforce
from .vector_db import load_index, load_travel_items, topk_per_category, query_emb
from .services.logger_setup import get_logger

logger = get_logger(__name__)


def generate_travel_advice(query: TravelQuery) -> TravelAdvice:
    logger.info(f"Received query: {query.query}")
    enforce(query.query)
    
    index = load_index()
    if not index:
        raise ValueError("Index not loaded properly. Please check the INDEX_PATH environment variable.")

    travel_items = load_travel_items()
    if not travel_items:
        raise ValueError("Travel items not loaded properly.")
    logger.info(f"Index loaded with {index.ntotal} items, travel items loaded with {len(travel_items)} records.")

    query_vec = query_emb(query.query)
    logger.info("Retrieving Query Vector")
    logger.info(f"Query vector: {query_vec}")

    logger.info("Getting results from the Vector Database")
    results_seed = topk_per_category(index, travel_items, query_vec)
    if not results_seed:
        logger.warning("No results found in the seed data.")

    llm_results = call_llm_with_seed(query.query, results_seed)
    if not llm_results:
        raise ValueError("LLM did not return valid results.")

    return llm_results





