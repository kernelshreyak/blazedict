## Blazedict

Blazingly fast english dictionary server with word search and word-autocomplete
### Load data into Elasticsearch
```bash
python3 load_data.py
```

### Run the server
```bash
uvicorn server:app --host 0.0.0.0 --port 8001
```
