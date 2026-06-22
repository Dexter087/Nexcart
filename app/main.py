"""FastAPI and CLI interface for NexCart recommendations.

The Streamlit dashboard is the main demo interface, but this file is kept to
satisfy the Track B requirement of a Python API returning top-N recommendations.

CLI:
    python -m app.main --customer_id <customer_id> --top_n 5

API:
    uvicorn app.main:app --reload
    http://127.0.0.1:8000/recommendations/<customer_id>?top_n=5
"""

from __future__ import annotations

import argparse
from typing import Any

from fastapi import FastAPI, HTTPException, Query

from app.recommender import get_recommendations

app = FastAPI(title="NexCart Recommendation API", version="1.0")


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "NexCart Recommendation API is running."}


@app.get("/recommendations/{customer_id}")
def recommendations(customer_id: str, top_n: int = Query(5, ge=1, le=20)) -> dict[str, Any]:
    try:
        recs, strategy = get_recommendations(customer_id, top_n)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {
        "customer_id": customer_id,
        "top_n": top_n,
        "strategy": strategy,
        "recommendations": recs.to_dict(orient="records"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Get NexCart product recommendations.")
    parser.add_argument("--customer_id", required=True, help="Customer ID to recommend for")
    parser.add_argument("--top_n", type=int, default=5, help="Number of recommendations")
    args = parser.parse_args()

    recs, strategy = get_recommendations(args.customer_id, args.top_n)
    print(strategy)
    print(recs.to_string(index=False))


if __name__ == "__main__":
    main()
