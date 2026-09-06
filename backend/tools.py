"""
Custom LangChain tools for Tavily web search and HTML page scraping.
"""

import os
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain.tools import tool
from tavily import TavilyClient

# Load environment configuration
env_root = Path(__file__).resolve().parent.parent / ".env"
if env_root.exists():
    load_dotenv(dotenv_path=env_root)
else:
    load_dotenv()

tavily_api_key = os.getenv("TAVILY_API_KEY") or "placeholder-key-for-init"

# Initialize Tavily search client
tavily = TavilyClient(api_key=tavily_api_key)


@tool
def web_search(query: str) -> str:
    """
    Searches the web using Tavily and returns top titles, URLs, and snippet summaries.
    """
    if not os.getenv("TAVILY_API_KEY"):
        return "Search Error: TAVILY_API_KEY is not configured in .env."

    try:
        results = tavily.search(query=query, max_results=5)
        out = []

        for r in results.get("results", []):
            out.append(
                f"Title: {r.get('title', '')}\nURL: {r.get('url', '')}\nSnippet: {r.get('content', '')[:300]}\n"
            )

        return "\n----\n".join(out)
    except Exception as e:
        return f"Search execution error: {str(e)}"


@tool
def scrape_url(url: str) -> str:
    """
    Scrapes and extracts clean readable text from a URL.
    Strips out scripts, navigation elements, footers, and styles to minimize context bloat.
    """
    try:
        resp = requests.get(
            url,
            timeout=8,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        soup = BeautifulSoup(resp.text, "html.parser")

        # Decompose non-body boilerplate elements
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        # Extract text and cap length to preserve LLM token window
        return soup.get_text(separator=" ", strip=True)[:3000]
    except Exception as e:
        return f"Could not scrape URL: {str(e)}"
