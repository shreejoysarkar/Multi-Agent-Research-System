from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
from duckduckgo_search import DDGS
import os
from dotenv import load_dotenv
from rich import print

load_dotenv()

from config import get_settings


tavily = TavilyClient(api_key = get_settings().TAVILY_API_KEY)


@tool
def web_search(query: str) -> str:
    """Search the web for recent and reliable information. Returns Titiles, URLs and Snippets"""
    results = tavily.search(query = query, max_results = 5)
    
    out = []

    for r in results['results']:
        out.append(
            f"Title : {r['title']}\n URL: {r['url']}\n Snippet : {r['content'][:300]}\n"
        )
    return "\n".join(out)



## now creating beautiful soup tool
@tool
def web_scraper(url: str)-> str:
    """
    Extracts full article content from a given URL using BeautifulSoup
    """

    try:
        # Fetching the page content
        response = requests.get(url, timeout=8, headers = {'User-Agent': "Mozilla/5.0"})
        response.raise_for_status()

        # Parsing the page
        soup = BeautifulSoup(response.text, 'html.parser')

        # Finding the article content
        # This is a heuristic and may need adjustment based on website structure
        # Common tags: article, main, or divs with specific classes
        article = soup.find('article') or soup.find('main') or soup.find('div', class_=['article-body', 'post-content'])
        
        if not article:
            # Fallback to body if no specific article tag found
            article = soup.body
        
        if article:
            # Extract text and clean it up
            text = article.get_text(separator='\n', strip=True)[:3000]
            return text
        else:
            return "Could not extract article content."
            
    except requests.RequestException as e:
        return f"Error fetching URL: {e}"

