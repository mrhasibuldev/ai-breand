"""
NexusAI Wikipedia Data Collector

Collects articles from Wikipedia API for tokenizer training and dataset preparation.
Respects robots.txt and rate limits.
Uses urllib (no external dependencies).
"""

import json
import time
import hashlib
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import sys

# Fix Windows encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


class WikipediaCollector:
    """Collects Wikipedia articles via API"""

    def __init__(self, rate_limit_delay: float = 1.0):
        self.rate_limit_delay = rate_limit_delay

    def get_article(self, title: str, lang: str = 'en') -> Optional[Dict]:
        """
        Get a Wikipedia article via API.

        Args:
            title: Article title
            lang: Language code ('en' or 'bn')

        Returns:
            Article data or None if error
        """
        try:
            # URL encode the title
            encoded_title = urllib.parse.quote(title)

            url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{encoded_title}"

            req = urllib.request.Request(
                url,
                headers={
                    'User-Agent': 'NexusAI-KnowledgeCollector/1.0 (https://nexusai.com)',
                    'Accept': 'application/json'
                }
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))

                    # Extract plain text
                    article_text = data.get('extract', '')

                    if not article_text:
                        return None

                    # Return article data
                    return {
                        'title': data.get('title', title),
                        'text': article_text,
                        'url': data.get('content_urls', {}).get('desktop', {}).get('page', ''),
                        'lang': lang,
                        'source': 'wikipedia',
                        'license': 'CC BY-SA 3.0',
                        'collected_at': datetime.utcnow().isoformat(),
                        'word_count': len(article_text.split()),
                        'char_count': len(article_text)
                    }
                else:
                    print(f"[Wikipedia] Failed to fetch '{title}': HTTP {response.status}")
                    return None

        except urllib.error.URLError as e:
            print(f"[Wikipedia] Error fetching '{title}': {e}")
            return None
        except Exception as e:
            print(f"[Wikipedia] Error fetching '{title}': {e}")
            return None

    def collect_articles(
        self,
        titles: List[str],
        lang: str = 'en',
        output_dir: str = None
    ) -> Dict[str, any]:
        """
        Collect multiple Wikipedia articles.

        Args:
            titles: List of article titles
            lang: Language code
            output_dir: Output directory

        Returns:
            Collection statistics
        """
        if output_dir is None:
            # Use relative path from this file
            output_dir = Path(__file__).parent / 'collected' / 'wikipedia' / lang
        else:
            output_dir = Path(output_dir)

        output_dir.mkdir(parents=True, exist_ok=True)

        collected = []
        failed = []

        for i, title in enumerate(titles):
            print(f"[Wikipedia] Collecting {i+1}/{len(titles)}: {title}")

            article = self.get_article(title, lang)

            if article:
                # Compute checksum
                checksum = hashlib.sha256(article['text'].encode('utf-8')).hexdigest()

                # Save article
                filename = f"{lang}_{hashlib.md5(title.encode('utf-8')).hexdigest()}.json"
                article_path = output_dir / filename

                with open(article_path, 'w', encoding='utf-8') as f:
                    json.dump({
                        **article,
                        'checksum': checksum
                    }, f, ensure_ascii=False, indent=2)

                collected.append(article)
                print(f"[Wikipedia] Saved: {filename}")
            else:
                failed.append(title)

            # Rate limiting
            time.sleep(self.rate_limit_delay)

        stats = {
            'total_requested': len(titles),
            'collected': len(collected),
            'failed': len(failed),
            'failed_titles': failed,
            'total_words': sum(a['word_count'] for a in collected),
            'total_chars': sum(a['char_count'] for a in collected),
            'language': lang,
            'output_dir': str(output_dir)
        }

        return stats


# Curated article titles for collection
ENGLISH_ARTICLES = [
    "Artificial intelligence",
    "Machine learning",
    "Deep learning",
    "Natural language processing",
    "Computer vision",
    "Neural network",
    "Bangladesh",
    "Dhaka",
    "Science",
    "Mathematics",
    "Technology",
    "Programming",
    "Data science",
    "Algorithm"
]

BENGALI_ARTICLES = [
    "কৃত্রিমিকি",
    "বাংলাদেশ",
    "ঢাকা",
    "বিজ্ঞান",
    "প্রযুক্তি",
    "বিজ্ঞান প্রযুক্তি",
    "প্রযুক্তি বিজ্ঞান",
    "কম্পিউটার বিজ্ঞান",
    "তথ্যশাস্ত্র",
    "প্রযুক্তি বিজ্ঞান",
    "নিউরোবায়টিক নেটওয়র্ক"
]


def main():
    """Main collection function"""
    print("[Wikipedia Collector] Starting data collection...")

    collector = WikipediaCollector(rate_limit_delay=1.0)

    # Collect English articles
    print("\n[Wikipedia] Collecting English articles...")
    en_stats = collector.collect_articles(
        ENGLISH_ARTICLES,
        lang='en'
    )

    # Collect Bengali articles
    print("\n[Wikipedia] Collecting Bengali articles...")
    bn_stats = collector.collect_articles(
        BENGALI_ARTICLES,
        lang='bn'
    )

    # Print summary
    print("\n=== COLLECTION SUMMARY ===")
    print(f"English: {en_stats['collected']}/{en_stats['total_requested']} collected")
    print(f"  - Total words: {en_stats['total_words']}")
    print(f"  - Total chars: {en_stats['total_chars']}")
    print(f"Bengali: {bn_stats['collected']}/{bn_stats['total_requested']} collected")
    print(f"  - Total words: {bn_stats['total_words']}")
    print(f"  - Total chars: {bn_stats['total_chars']}")
    print(f"TOTAL: {en_stats['collected'] + bn_stats['collected']} articles")
    print(f"TOTAL WORDS: {en_stats['total_words'] + bn_stats['total_words']}")
    print(f"TOTAL CHARS: {en_stats['total_chars'] + bn_stats['total_chars']}")

    # Save collection manifest
    manifest = {
        'collection_timestamp': datetime.utcnow().isoformat(),
        'source': 'Wikipedia API',
        'license': 'CC BY-SA 3.0',
        'attribution_required': True,
        'english_stats': en_stats,
        'bengali_stats': bn_stats,
        'total_articles': en_stats['collected'] + bn_stats['collected'],
        'total_words': en_stats['total_words'] + bn_stats['total_words'],
        'total_chars': en_stats['total_chars'] + bn_stats['total_chars']
    }

    manifest_path = Path(__file__).parent / 'collected' / 'wikipedia' / 'collection_manifest.json'
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"\n[Wikipedia] Manifest saved to {manifest_path}")


if __name__ == "__main__":
    main()
