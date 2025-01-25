import os
import requests
from fastapi import FastAPI
from pydantic import BaseModel
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

class QueryRequest(BaseModel):
    query: str

SYSTEM_PROMPT = """You are a legal expert specializing in Kazakhstan law. 
Base your answers strictly on the Republic of Kazakhstan's legal framework. 
If information is unavailable, state that clearly."""

def google_search(query):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": os.getenv("GOOGLE_API_KEY"),
        "cx": os.getenv("CSE_ID"),
        "q": query + " site:.kz filetype:pdf OR filetype:html",
        "lr": "lang_kk",
        "num": 5  # Get top 5 relevant results
    }
    response = requests.get(url, params=params)
    return [item["link"] for item in response.json().get("items", [])]

def scrape_content(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Prioritize legal content sections
        for tag in ['article', 'div.legal-content', 'main', 'body']:
            content = soup.select_one(tag)
            if content:
                return content.get_text(separator='\n', strip=True)[:5000]  # Limit content
        
        return soup.get_text()[:5000]
    except:
        return ""

def get_deepseek_response(context, query):
    headers = {
        "Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}",
        "Content-Type": "application/json"
    }
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
    ]
    
    data = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": 0.3
    }
    
    try:
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=15
        )
        
        # Check for HTTP errors
        response.raise_for_status()
        
        response_json = response.json()
        
        # Debug: Print full API response
        print("DeepSeek API Response:", response_json)
        
        if "choices" in response_json and len(response_json["choices"]) > 0:
            return response_json["choices"][0]["message"]["content"]
            
        return "Error: No valid response from the AI model"
        
    except requests.exceptions.RequestException as e:
        print(f"API Request Error: {str(e)}")
        return f"API Error: {str(e)}"
    except KeyError as e:
        print(f"Key Error in API Response: {str(e)}")
        print(f"Full Response: {response_json}")
        return "Error: Unexpected API response format"

@app.post("/ask")
async def legal_query(request: QueryRequest):
    # Step 1: Search for legal documents
    search_results = google_search(f"Kazakhstan law {request.query}")
    
    # Step 2: Scrape and aggregate content
    context = ""
    for url in search_results[:3]:  # Use top 3 results
        context += scrape_content(url) + "\n\n"
    
    # Step 3: Get AI response
    response = get_deepseek_response(context, request.query)
    
    return {"response": response}

# To run: uvicorn main:app --reload