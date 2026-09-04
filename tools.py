"""
Custom research tools for search and web scraping.
"""

import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain.tools import tool
from tavily import TavilyClient

# Load environment configuration
load_dotenv()

# Initialize Tavily search client with API key from environment
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


@tool
def web_search(query: str) -> str:
    """
    Search the web for recent and reliable information on a topic.
    Returns structured results containing titles, URLs, and text snippets.
    """
    results = tavily.search(query=query, max_results=5)
    out = []

    for r in results.get("results", []):
        out.append(
            f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:300]}\n"
        )

    return "\n----\n".join(out)


@tool
def scrape_url(url: str) -> str:
    """
    Scrapes and extracts clean readable text from a target URL for in-depth analysis.
    Strips out navigation bars, scripts, styles, and footers.
    """
    try:
        resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        soup = BeautifulSoup(resp.text, "html.parser")

        # Remove non-content elements to avoid noise in the context window
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        # Extract text and limit length to keep token usage optimal
        return soup.get_text(separator=" ", strip=True)[:3000]
    except Exception as e:
        return f"Could not scrape URL: {str(e)}"
