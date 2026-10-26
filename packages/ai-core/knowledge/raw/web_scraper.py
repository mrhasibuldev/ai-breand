"""
Web Scraper for General Knowledge

This script scrapes general knowledge data from various web sources
and ingests it into the NexusAI knowledge pipeline.
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from pathlib import Path
import sys
import json
import hashlib
from datetime import datetime
import uuid

# Add parent directory to path to import pipeline
sys.path.insert(0, str(Path(__file__).parent.parent / "pipeline"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from ingestion_pipeline import KnowledgeIngestionPipeline


class WebScraper:
    """Web scraper for collecting general knowledge data."""

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def scrape_wikipedia_article(self, url: str) -> Optional[str]:
        """
        Scrape a Wikipedia article.

        Args:
            url: Wikipedia article URL

        Returns:
            Article text or None if failed
        """
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    print(f"Failed to fetch {url}: {response.status}")
                    return None

                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')

                # Find main content
                content_div = soup.find('div', {'id': 'mw-content-text'})
                if not content_div:
                    print(f"No content found for {url}")
                    return None

                # Remove unwanted elements
                for tag in content_div.find_all(['script', 'style', 'sup', 'nav', 'table']):
                    tag.decompose()

                # Extract text
                text = content_div.get_text(separator='\n', strip=True)

                # Clean up whitespace
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                cleaned_text = '\n'.join(lines)

                return cleaned_text

        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None

    async def scrape_simple_facts(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Scrape multiple URLs for facts.

        Args:
            urls: List of URLs to scrape

        Returns:
            List of scraped documents
        """
        documents = []

        for url in urls:
            print(f"Scraping: {url}")
            text = await self.scrape_wikipedia_article(url)

            if text and len(text) > 100:  # Minimum length filter
                documents.append({
                    "text": text,
                    "source": url,
                    "source_type": "web",
                    "metadata": {
                        "collected_by": "web_scraper",
                        "trust_level": "TIER_2"
                    }
                })
                print(f"Successfully scraped {len(text)} characters")

        return documents


# Sample Wikipedia articles for general knowledge
SAMPLE_ARTICLES = [
    "https://en.wikipedia.org/wiki/Science",
    "https://en.wikipedia.org/wiki/History",
    "https://en.wikipedia.org/wiki/Mathematics",
    "https://en.wikipedia.org/wiki/Computer_science",
    "https://en.wikipedia.org/wiki/Physics",
    "https://en.wikipedia.org/wiki/Chemistry",
    "https://en.wikipedia.org/wiki/Biology",
    "https://en.wikipedia.org/wiki/Philosophy",
    "https://en.wikipedia.org/wiki/Economics",
    "https://en.wikipedia.org/wiki/Geography",
]


async def main():
    """Main function to scrape and ingest data."""
    print("=== Web Scraper for General Knowledge ===\n")

    # Initialize pipeline
    print("Initializing knowledge pipeline...")
    current_dir = Path(__file__).parent.parent
    pipeline = KnowledgeIngestionPipeline(
        raw_data_dir=str(current_dir / "raw"),
        cleaned_data_dir=str(current_dir / "cleaned")
    )

    # Scrape data
    print("\nStarting web scraping...")
    async with WebScraper() as scraper:
        documents = await scraper.scrape_simple_facts(SAMPLE_ARTICLES)

    print(f"\nScraped {len(documents)} documents")

    if not documents:
        print("No documents scraped. Exiting.")
        return

    # Ingest data
    print("\nIngesting documents into knowledge pipeline...")
    results = await pipeline.ingest_batch(documents)

    # Report results
    successful = sum(1 for r in results if r.success)
    failed = len(results) - successful

    print(f"\n=== Ingestion Results ===")
    print(f"Total: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")

    if failed > 0:
        print("\nFailed documents:")
        for result in results:
            if not result.success:
                print(f"  - {result.error}")

    print("\n=== Summary ===")
    total_chunks = sum(r.chunk_count for r in results if r.success)
    avg_time = sum(r.processing_time_ms for r in results) / len(results)
    print(f"Total chunks created: {total_chunks}")
    print(f"Average processing time: {avg_time:.2f}ms")

    print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())
