import json
import urllib3
from elasticsearch import Elasticsearch, helpers
import os
from dotenv import load_dotenv

load_dotenv()
INDEX_NAME = os.environ["INDEX_NAME"]
# Initialize Elasticsearch client with SSL certificate verification disabled
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
es = Elasticsearch(
    [os.environ["ELASTICSEARCH_HOST"]],
    basic_auth=(os.environ["ELASTICSEARCH_USERNAME"], os.environ["ELASTICSEARCH_PASSWORD"]),
    verify_certs=False
)

# Function to create the index with appropriate mappings
def create_index():
    if not es.indices.exists(index=INDEX_NAME):
        index_body = {
            "settings": {
                "analysis": {
                    "analyzer": {
                        "standard_analyzer": {
                            "type": "standard"
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "word": {"type": "text", "analyzer": "standard_analyzer"},
                    "definition": {"type": "text", "analyzer": "standard_analyzer"},
                    "synonyms": {"type": "text"},
                    "autocomplete": {"type": "completion"}  # Added for autocomplete
                }
            }
        }
        es.indices.create(index=INDEX_NAME, body=index_body)
        print(f"Index '{INDEX_NAME}' created.")

# Function to load data into Elasticsearch
def load_data(filename="dictionary.json"):
    with open(filename, "r") as file:
        data = json.load(file)

    actions = []
    for word, definition in data.items():
        actions.append({
            "_index": INDEX_NAME,
            "_source": {
                "word": word,
                "definition": definition,
                "synonyms": [],
                "autocomplete": {"input": [word]}  # Added for autocomplete
            }
        })

        # Bulk index in batches of 5000
        if len(actions) == 5000:
            helpers.bulk(es, actions)
            actions = []

    # Index any remaining actions
    if actions:
        helpers.bulk(es, actions)

    print("Data loaded into Elasticsearch.")

if __name__ == "__main__":
    create_index()
    load_data()
