# BeautifulSoup Web Scraper Tool

# src/tools/scrape.py
import requests
from bs4 import BeautifulSoup
from typing import List
from langchain_core.tools import tool
from concurrent.futures import ThreadPoolExecutor, as_completed

# Common tags to remove before extracting text (ads, scripts, navbars)
TAGS_TO_REMOVE = ['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe']


# 🆕 NEW: Helper function for parallel execution
# This is what each thread will execute
def _scrape_single_url(url: str) -> dict:
    """
    Internal helper: Scrapes a single URL.
    Returns a dict with url, title, and content, or None if failed.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove unwanted tags
        for tag in soup(TAGS_TO_REMOVE):
            tag.decompose()
            
        # Extract title
        title = soup.title.string if soup.title else "No Title"
        
        # Extract text and clean it up
        text = soup.get_text(separator=' ', strip=True)
        # Remove excessive whitespace
        content = ' '.join(text.split())
        
        # Limit content length to avoid blowing up the LLM context window (approx 4000 tokens)
        if len(content) > 15000:
            content = content[:15000] + "... [Content truncated]"
            
        return {
            "url": url,
            "title": title.strip(),
            "content": content
        }
        
    except Exception as e:
        print(f"⚠️ Error scraping {url}: {e}")
        return None

@tool
def scrape_urls(urls: List[str]) -> List[dict]:
    """
    Scrapes the main text content from a list of URLs in PARALLEL.
    Use this to get the full article text from search result links.
    
    Args:
        urls: A list of URL strings to scrape.
        
    Returns:
        A list of dictionaries containing 'url', 'title', and 'content'.
    """
    if not urls:
        return []
    
    print(f" [Scraper] Scraping {len(urls)} URLs in parallel...")
    
    scraped_data = []
    

    # PARALLEL EXECUTION: Use ThreadPoolExecutor
    # max_workers=5 means it scrapes up to 5 URLs simultaneously
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        # Submit all scraping tasks to the executor
        # Each URL gets its own thread
        future_to_url = {executor.submit(_scrape_single_url, url): url for url in urls}
        
        # Collect results as they complete (not necessarily in order)
        for future in as_completed(future_to_url):
            result = future.result()
            if result:  # Only add successful scrapes
                scraped_data.append(result)
    
    
    print(f" [Scraper] Successfully scraped {len(scraped_data)} URLs")
    return scraped_data