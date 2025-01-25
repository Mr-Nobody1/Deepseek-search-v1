# Kazakhstan Legal Query System

A FastAPI application that provides legal answers based on Kazakhstan's legal framework using Google Search and Deepseek AI.

## Features

- Legal document search via Google Custom Search API
- Web content scraping from .kz domains
- AI-powered legal analysis using Deepseek's API
- REST API endpoint for querying

## Prerequisites

- Python 3.9+
- Google Custom Search Engine ID
- Google API Key
- Deepseek API Key

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

1. Create `.env` file:
```env
GOOGLE_API_KEY=your_google_api_key
CSE_ID=your_custom_search_engine_id
DEEPSEEK_API_KEY=your_deepseek_api_key
```

2. Install dependencies:
```bash
pip install fastapi uvicorn python-dotenv requests beautifulsoup4
```

## Usage

### Running the API
```bash
uvicorn main:app --reload
```

### Making Queries (Example)
```python
import requests

response = requests.post(
    "http://localhost:8000/ask",
    json={"query": "What are the penalties for tax evasion?"}
)

print(response.json()["response"])
```

## API Endpoint

`POST /ask`
- Request body: `{"query": "your_legal_question"}`
- Returns: JSON with legal analysis

## Environment Variables
| Variable | Description |
|----------|-------------|
| `GOOGLE_API_KEY` | Google Cloud API key |
| `CSE_ID` | Custom Search Engine ID |
| `DEEPSEEK_API_KEY` | Deepseek API access key |
