"""
Simple Web Scraper for General Knowledge

This script scrapes general knowledge data from Wikipedia and saves it
for ingestion into the NexusAI knowledge pipeline.
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import uuid


class SimpleWebScraper:
    """Simple web scraper for collecting general knowledge data."""

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = aiohttp.ClientSession(headers=headers)
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
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
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

    def save_documents(self, documents: List[Dict[str, Any]], output_dir: str):
        """
        Save scraped documents to disk.

        Args:
            documents: List of documents to save
            output_dir: Directory to save to
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        for doc in documents:
            # Generate document ID
            doc_id = f"raw_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:12]}"
            file_path = output_path / f"{doc_id}.txt"

            # Save raw text
            file_path.write_text(doc["text"], encoding='utf-8')

            # Save metadata
            metadata = {
                "document_id": doc_id,
                "source": doc["source"],
                "source_type": doc["source_type"],
                "collected_at": datetime.now().isoformat(),
                "metadata": doc["metadata"]
            }

            metadata_path = output_path / f"{doc_id}.meta.json"
            import json
            metadata_path.write_text(json.dumps(metadata, indent=2), encoding='utf-8')

            print(f"Saved: {file_path.name}")


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
    """Main function to scrape and save data."""
    print("=== Simple Web Scraper for General Knowledge ===\n")

    # Scrape data
    print("Starting web scraping...")
    async with SimpleWebScraper() as scraper:
        documents = await scraper.scrape_simple_facts(SAMPLE_ARTICLES)

    print(f"\nScraped {len(documents)} documents")

    if not documents:
        print("No documents scraped. Exiting.")
        return

    # Save documents
    print("\nSaving documents...")
    current_dir = Path(__file__).parent
    output_dir = current_dir / "scraped"
    scraper.save_documents(documents, str(output_dir))

    print(f"\nDocuments saved to: {output_dir}")
    print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
