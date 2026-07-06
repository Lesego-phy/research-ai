# Unit tests for tools

"""Unit tests for the tools."""
import pytest
from src.tools.search import tavily_search
from src.tools.scrape import scrape_urls, _scrape_single_url

def test_scrape_single_url():
    """Test scraping a single URL."""
    result = _scrape_single_url("https://en.wikipedia.org/wiki/Python_(programming_language)")
    
    assert result is not None
    assert "url" in result
    assert "title" in result
    assert "content" in result
    assert len(result["content"]) > 100
    assert result["url"] == "https://en.wikipedia.org/wiki/Python_(programming_language)"

def test_scrape_urls_parallel():
    """Test parallel scraping of multiple URLs."""
    urls = [
        "https://en.wikipedia.org/wiki/Artificial_intelligence",
        "https://en.wikipedia.org/wiki/Machine_learning",
        "https://en.wikipedia.org/wiki/Deep_learning"
    ]
    
    results = scrape_urls.invoke({"urls": urls})
    
    assert len(results) == 3
    assert all("content" in r for r in results)
    assert all("title" in r for r in results)

def test_scrape_invalid_url():
    """Test that invalid URLs don't crash the scraper."""
    result = _scrape_single_url("https://this-url-does-not-exist-1234.com")
    assert result is None

def test_tavily_search():
    """Test Tavily search returns results."""
    result = tavily_search.invoke("artificial intelligence")
    
    assert result is not None
    assert isinstance(result, str)
    assert len(result) > 0