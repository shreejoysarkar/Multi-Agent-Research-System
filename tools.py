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

    return results

print(web_search.invoke("Latest news about AI"))
