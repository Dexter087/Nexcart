"""
NexCart Python API.

Run as API:
    uvicorn app.main:app --reload

Run as a command-line test:
    python -m app.main --customer_id <customer_id> --top_n 5
"""

import argparse
import json
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Query

from .recommender import get_recommendations


app = FastAPI(
    title="NexCart Recommendation API",
    description="Top-N product recommendation API for the Z2004 DBMS NexCart project.",
    version="1.0.0",
)


@app.get("/")
def root() -> Dict[str, str]:
    return {
        "project": "NexCart",
        "message": "Use /recommendations/{customer_id}?top_n=5 to get product recommendations.",
    }


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/recommendations/{customer_id}")
def recommendations(
    customer_id: str,
    top_n: int = Query(default=10, ge=1, le=50),
) -> Dict[str, Any]:
    try:
        return get_recommendations(customer_id=customer_id, top_n=top_n)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


def run_cli() -> None:
    parser = argparse.ArgumentParser(description="Get NexCart product recommendations.")
    parser.add_argument("--customer_id", required=True, help="Customer ID from the customers table")
    parser.add_argument("--top_n", type=int, default=10, help="Number of recommendations")
    args = parser.parse_args()

    result = get_recommendations(customer_id=args.customer_id, top_n=args.top_n)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    run_cli()
