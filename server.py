from fastapi import FastAPI, HTTPException, Query
from elasticsearch import Elasticsearch
from pydantic import BaseModel
from typing import List
import urllib3
import os
from dotenv import load_dotenv

load_dotenv()
INDEX_NAME = os.environ["INDEX_NAME"]

# Initialize Elasticsearch client with authentication
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
es = Elasticsearch(
    [os.environ["ELASTICSEARCH_HOST"]],
    basic_auth=(os.environ["ELASTICSEARCH_USERNAME"], os.environ["ELASTICSEARCH_PASSWORD"]),
    verify_certs=False
)

# FastAPI app
app = FastAPI()

@app.get("/search")
def search_word(query: str):
    search_body = {
        "query": {
            "match": {
                "word": query
            }
        }
    }
    res = es.search(index=INDEX_NAME, body=search_body)

    if res["hits"]["hits"]:
        result = res["hits"]["hits"][0]["_source"]
        return {"word": result["word"], "definition": result["definition"], "synonyms": result.get("synonyms", [])}

    return {"word": query, "definition": "Not found", "synonyms": []}

@app.get("/autocomplete")
def autocomplete_word(query: str, k: int = Query(5, ge=1)):
    """
    Autocomplete endpoint to suggest words based on a given prefix.
    Returns up to 'k' suggestions.
    """
    search_body = {
        "suggest": {
            "word-suggest": {
                "prefix": query,
                "completion": {
                    "field": "autocomplete",
                    "size": k
                }
            }
        }
    }

    res = es.search(index=INDEX_NAME, body=search_body)

    suggestions = res.get("suggest", {}).get("word-suggest", [])[0].get("options", [])
    words = [sugg["_source"]["word"] for sugg in suggestions]

    return {"query": query, "suggestions": words}
