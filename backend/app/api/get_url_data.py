import os
import re
import aiohttp
import asyncio
import requests
from urllib.parse import urlparse, urljoin
from datetime import date
from fastapi import FastAPI, HTTPException, Query
from bs4 import BeautifulSoup
from pydantic import BaseModel, HttpUrl, validator
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# app = FastAPI(title="Web Crawler API with Exception Handling")

# Custom exceptions
class CrawlerError(Exception):
    """Base exception for crawler errors"""
    pass

class InvalidURLError(CrawlerError):
    """Raised when URL is invalid or malformed"""
    pass

class HTTPError(CrawlerError):
    """Raised when HTTP request fails"""
    pass

class NetworkError(CrawlerError):
    """Raised when network connection fails"""
    pass

# Response models
class ErrorResponse(BaseModel):
    error: str
    message: str
    status_code: int

def validate_url(url: str) -> str:
    """Validate URL format and accessibility"""
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise InvalidURLError(f"Invalid URL format: {url}. URL must include protocol (http/https) and domain.")
        
        if parsed.scheme not in ['http', 'https']:
            raise InvalidURLError(f"Unsupported URL scheme: {parsed.scheme}. Only http and https are supported.")
        
        return url
    except Exception as e:
        raise InvalidURLError(f"URL validation failed: {str(e)}")

def clean_html(html, skip_footer_header=True):
    try:
        soup = BeautifulSoup(html, 'html.parser')
        if skip_footer_header:
            for unwanted in soup(['header', 'footer', 'nav', 'aside', 'script', 'style']):
                unwanted.decompose()
        return str(soup)
    except Exception as e:
        logger.error(f"Error cleaning HTML: {e}")
        raise CrawlerError(f"Failed to clean HTML content: {str(e)}")

def get_main_content(html, skip_footer_header=True):
    try:
        soup = BeautifulSoup(html, 'html.parser')
        if skip_footer_header:
            main_content_selectors = [
                'main', '[role="main"]', '.main-content', '.content',
                '.post-content', '.article-content', '#main', '#content'
            ]
            for selector in main_content_selectors:
                main_element = soup.select_one(selector)
                if main_element:
                    return main_element.get_text(separator='\n', strip=True)

            for unwanted in soup(['header', 'footer', 'nav', 'aside', 'script', 'style']):
                unwanted.decompose()

        body = soup.find('body')
        if body:
            return body.get_text(separator='\n', strip=True)
        return soup.get_text(separator='\n', strip=True)
    except Exception as e:
        logger.error(f"Error extracting main content: {e}")
        raise CrawlerError(f"Failed to extract main content: {str(e)}")

async def fetch(session, url):
    """Fetch URL with proper error handling"""
    try:
        # Validate URL before making request
        validate_url(url)
        
        async with session.get(url, timeout=20) as response:
            # Check for HTTP errors
            if response.status == 200:
                return await response.text(errors="ignore")
            elif response.status == 404:
                raise HTTPError(f"URL not found (404): {url}")
            elif response.status == 403:
                raise HTTPError(f"Access forbidden (403): {url}")
            elif response.status == 500:
                raise HTTPError(f"Server error (500): {url}")
            elif response.status >= 400:
                raise HTTPError(f"HTTP error {response.status}: {url}")
            else:
                raise HTTPError(f"Unexpected HTTP status {response.status}: {url}")
                
    except aiohttp.ClientConnectorError as e:
        raise NetworkError(f"Connection failed for {url}: {str(e)}")
    except aiohttp.ServerTimeoutError:
        raise NetworkError(f"Request timeout for {url}")
    except aiohttp.ClientError as e:
        raise NetworkError(f"Client error for {url}: {str(e)}")
    except InvalidURLError:
        raise  # Re-raise URL validation errors
    except HTTPError:
        raise  # Re-raise HTTP errors
    except Exception as e:
        raise CrawlerError(f"Unexpected error fetching {url}: {str(e)}")

def classify_urls(base_url, html_content, skip_footer_header=True, skip_social_media=True):
    try:
        if skip_footer_header:
            html_content = clean_html(html_content, skip_footer_header=True)

        href_pattern = r'href=["\']([^"\']*)["\']'
        matches = re.findall(href_pattern, html_content, re.IGNORECASE)

        classified_urls = {
            'pdf_files': set(),
            'office_documents': set(),
            'archives': set(),
            'data_files': set(),
            'page_links': set(),
        }

        social_domains = ["linkedin.com", "facebook.com", "instagram.com", "twitter.com", "youtube.com"]

        for match in matches:
            try:
                clean_url = match.strip().replace(' ', '%20')
                if not clean_url.startswith(('http://', 'https://')):
                    clean_url = urljoin(base_url, clean_url)

                # Skip ads and social media
                if "googleads" in clean_url.lower() or "doubleclick" in clean_url.lower():
                    continue
                if skip_social_media and any(social in clean_url.lower() for social in social_domains):
                    continue

                # Validate the constructed URL
                try:
                    validate_url(clean_url)
                except InvalidURLError:
                    continue  # Skip invalid URLs but don't fail the entire process

                parsed_clean = urlparse(clean_url)
                path = (parsed_clean.path or "").lower()

                if path.endswith('.pdf'):
                    classified_urls['pdf_files'].add(clean_url)
                elif path.endswith(('.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx')):
                    classified_urls['office_documents'].add(clean_url)
                elif path.endswith(('.zip', '.rar', '.tar.gz', '.tar', '.gz')):
                    classified_urls['archives'].add(clean_url)
                elif path.endswith(('.xml', '.json', '.csv', '.txt')):
                    classified_urls['data_files'].add(clean_url)
                else:
                    last_segment = path.split('/')[-1]
                    if (not path or path.endswith('/') or not '.' in last_segment or
                            path.endswith(('.html', '.htm', '.php', '.asp', '.aspx'))):
                        classified_urls['page_links'].add(clean_url)
            except Exception as e:
                logger.warning(f"Error processing URL {match}: {e}")
                continue  # Skip problematic URLs

        return classified_urls
    except Exception as e:
        raise CrawlerError(f"Failed to classify URLs: {str(e)}")

def download_file_sync(url):
    """Download file with proper error handling"""
    try:
        validate_url(url)
        
        chunk_size = 800
        today = date.today()
        folder = f"{today.day}_{today.month}_{today.year}"
        os.makedirs(folder, exist_ok=True)
        
        file_name = url.split("/")[-1].replace("%20", "_")
        if not file_name or file_name == "/":
            file_name = f"file_{int(date.today().timestamp())}"
            
        path = os.path.join(folder, file_name)

        r = requests.get(url, stream=True, timeout=30)
        
        # Check HTTP status
        if r.status_code == 200:
            with open(path, 'wb') as fd:
                for chunk in r.iter_content(chunk_size):
                    fd.write(chunk)
            return path
        elif r.status_code == 404:
            raise HTTPError(f"File not found (404): {url}")
        elif r.status_code == 403:
            raise HTTPError(f"Access forbidden (403): {url}")
        elif r.status_code >= 400:
            raise HTTPError(f"HTTP error {r.status_code} downloading {url}")
        else:
            raise HTTPError(f"Unexpected status {r.status_code} downloading {url}")
            
    except requests.exceptions.ConnectTimeout:
        raise NetworkError(f"Connection timeout downloading {url}")
    except requests.exceptions.ReadTimeout:
        raise NetworkError(f"Read timeout downloading {url}")
    except requests.exceptions.ConnectionError as e:
        raise NetworkError(f"Connection error downloading {url}: {str(e)}")
    except requests.exceptions.RequestException as e:
        raise NetworkError(f"Request failed downloading {url}: {str(e)}")
    except OSError as e:
        raise CrawlerError(f"File system error downloading {url}: {str(e)}")
    except Exception as e:
        raise CrawlerError(f"Unexpected error downloading {url}: {str(e)}")

async def make_file_node(url, category, fetch_content, visited):
    try:
        visited.add(url)
        filepath = download_file_sync(url) if fetch_content else None
        return {
            "url": url,
            "type": category,
            "content": filepath,
            "children": []
        }
    except Exception as e:
        logger.error(f"Error creating file node for {url}: {e}")
        return {
            "url": url,
            "type": category,
            "content": None,
            "error": str(e),
            "children": []
        }

async def crawl(session, url, depth=0, max_depth=2,
                fetch_content=True, skip_footer_header=True, skip_social_media=True, visited=None, downolad_files=False):
    if visited is None:
        visited = set()

    try:
        if depth >= max_depth or url in visited:
            return None
        visited.add(url)

        html_content = await fetch(session, url)
        content = get_main_content(html_content, skip_footer_header) if fetch_content else None

        node = {
            "url": url,
            "type": "url",
            "content": content,
            "children": []
        }

        classified_urls = classify_urls(url, html_content, skip_footer_header, skip_social_media)

        tasks = []
        for category, urls in classified_urls.items():
            for suburl in urls:
                if suburl in visited:
                    continue
                if category in ["office_documents", "pdf_files", "archives", "data_files"]:
                    if not downolad_files:
                        continue
                    tasks.append(make_file_node(suburl, category, fetch_content, visited))
                else:
                    tasks.append(crawl(
                        session, suburl, depth + 1, max_depth,
                        fetch_content, skip_footer_header, skip_social_media, visited
                    ))

        if tasks:
            children = await asyncio.gather(*tasks, return_exceptions=True)
            # Filter out exceptions and None values
            node["children"] = []
            for child in children:
                if isinstance(child, Exception):
                    logger.error(f"Error in child crawl: {child}")
                elif child is not None:
                    node["children"].append(child)

        return node
        
    except (InvalidURLError, HTTPError, NetworkError) as e:
        logger.error(f"Crawl error for {url}: {e}")
        return {
            "url": url,
            "type": "error",
            "error": str(e),
            "children": []
        }
    except Exception as e:
        logger.error(f"Unexpected error crawling {url}: {e}")
        return {
            "url": url,
            "type": "error", 
            "error": f"Unexpected error: {str(e)}",
            "children": []
        }

async def run_crawler(start_url, max_depth=2, fetch_content=True,
                      skip_footer_header=True, skip_social_media=True):
    try:
        # Validate start URL
        validate_url(start_url)
        
        visited = set()  # reset visited for every run
        async with aiohttp.ClientSession() as session:
            result = await crawl(session, start_url, 0, max_depth,
                               fetch_content, skip_footer_header, skip_social_media, visited)
            
            if result is None:
                raise CrawlerError("Crawling returned no results")
            
            return result
            
    except (InvalidURLError, HTTPError, NetworkError, CrawlerError):
        raise  # Re-raise known errors
    except Exception as e:
        raise CrawlerError(f"Unexpected error in crawler: {str(e)}")


async def crawl_urls(
    start_url: str = Query(..., description="The URL to start crawling from"),
    max_depth: int = Query(2, ge=1, le=5, description="Maximum crawl depth"),
    skip_footer_header: bool = Query(False, description="Skip header and footer content"),
    skip_social_media: bool = Query(True, description="Skip social media links")
):
    try:
        result = await run_crawler(
            start_url,
            max_depth=max_depth,
            fetch_content=False,  
            skip_footer_header=skip_footer_header,
            skip_social_media=skip_social_media
        )
        return {"status": "success", "data": result}
        
    except InvalidURLError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid URL",
                "message": str(e),
                "suggestion": "Please check the URL format. Ensure it includes http:// or https:// and a valid domain."
            }
        )
    except HTTPError as e:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "HTTP Error",
                "message": str(e),
                "suggestion": "The URL returned an HTTP error. Please check if the URL exists and is accessible."
            }
        )
    except NetworkError as e:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Network Error",
                "message": str(e),
                "suggestion": "Network connection failed. Please check your internet connection and try again."
            }
        )
    except CrawlerError as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Crawler Error",
                "message": str(e),
                "suggestion": "An error occurred during crawling. Please try again with different parameters."
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error in crawl_urls: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred",
                "suggestion": "Please try again later or contact support if the problem persists."
            }
        )

async def crawl_content(
    start_url: str = Query(..., description="The URL to start crawling from"),
    max_depth: int = Query(2, ge=1, le=5, description="Maximum crawl depth"),
    skip_footer_header: bool = Query(False, description="Skip header and footer content"),
    skip_social_media: bool = Query(True, description="Skip social media links")
):
    try:
        result = await run_crawler(
            start_url,
            max_depth=max_depth,
            fetch_content=True,  
            skip_footer_header=skip_footer_header,
            skip_social_media=skip_social_media
        )
        return {"status": "success", "data": result}
        
    except InvalidURLError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid URL",
                "message": str(e),
                "suggestion": "Please check the URL format. Ensure it includes http:// or https:// and a valid domain."
            }
        )
    except HTTPError as e:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "HTTP Error",
                "message": str(e),
                "suggestion": "The URL returned an HTTP error. Please check if the URL exists and is accessible."
            }
        )
    except NetworkError as e:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Network Error",
                "message": str(e),
                "suggestion": "Network connection failed. Please check your internet connection and try again."
            }
        )
    except CrawlerError as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Crawler Error",
                "message": str(e),
                "suggestion": "An error occurred during crawling. Please try again with different parameters."
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error in crawl_content: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred",
                "suggestion": "Please try again later or contact support if the problem persists."
            }
        )

