#!/usr/bin/env python3
"""
Combine pilot and expansion datasets into a single review dataset
"""

import json
from pathlib import Path
from datetime import datetime, timezone


def combine_datasets():
    """Combine pilot and expansion datasets"""
    base_path = Path("packages/ai-core/data/pilots/b4-b2-p1")
    
    # Load pilot dataset
    with open(base_path / "pilot_dataset.json", 'r', encoding='utf-8') as f:
        pilot_data = json.load(f)
    
    # Load expansion dataset
    with open(base_path / "pilot_dataset_expansion_drafts.json", 'r', encoding='utf-8') as f:
        expansion_data = json.load(f)
    
    pilot_count = len(pilot_data['conversations'])
    expansion_count = len(expansion_data['conversations'])
    
    print(f"Pilot conversations: {pilot_count}")
    print(f"Expansion conversations (actual): {expansion_count}")
    print(f"Expansion conversations (claimed in stats): {expansion_data['statistics']['total_conversations']}")
    
    # Update statistics to match actual count
    expansion_data['statistics']['total_conversations'] = expansion_count
    
    # Combine conversations
    combined_conversations = pilot_data['conversations'] + expansion_data['conversations']
    
    # Create combined metadata
    combined_metadata = {
        "schema_version": "2.0",
        "dataset_version": "0.3.0-review",
        "dataset_name": "nexusai-pilot-b4-b2-p1-combined",
        "created": datetime.now(timezone.utc).isoformat(),
        "modified": datetime.now(timezone.utc).isoformat(),
        "creator": "NexusAI Project",
        "license": "proprietary-project-owned",
        "license_url": None,
        "commercial_use": "permitted",
        "redistribution": "restricted-to-project",
        "purpose": "training",
        "description": "Combined pilot and expansion datasets for human review - 100 conversations total"
    }
    
    # Create combined statistics
    combined_stats = {
        "total_conversations": len(combined_conversations),
        "total_messages": sum(len(c.get('messages', [])) for c in combined_conversations),
        "language_distribution": {
            "bengali": pilot_data['statistics']['language_distribution']['bengali'] + 
                       expansion_data['statistics']['language_distribution']['bengali'],
            "english": pilot_data['statistics']['language_distribution']['english'] + 
                      expansion_data['statistics']['language_distribution']['english'],
            "mixed": pilot_data['statistics']['language_distribution']['mixed'] + 
                    expansion_data['statistics']['language_distribution']['mixed'],
            "unknown": 0
        },
        "domain_distribution": {},
        "split_distribution": {
            "train": 0,
            "validation": 0,
            "test": 0,
            "pending": len(combined_conversations)
        }
    }
    
    # Combine domain distributions
    for domain in pilot_data['statistics']['domain_distribution']:
        combined_stats['domain_distribution'][domain] = (
            pilot_data['statistics']['domain_distribution'].get(domain, 0) +
            expansion_data['statistics']['domain_distribution'].get(domain, 0)
        )
    
    # Create combined dataset
    combined_dataset = {
        "schema_version": "2.0",
        "dataset_version": "0.3.0-review",
        "dataset_name": "nexusai-pilot-b4-b2-p1-combined",
        "metadata": combined_metadata,
        "statistics": combined_stats,
        "conversations": combined_conversations
    }
    
    # Save combined dataset
    output_path = base_path / "combined_for_review.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(combined_dataset, f, indent=2, ensure_ascii=False)
    
    print(f"Combined dataset saved to: {output_path}")
    print(f"Total conversations: {len(combined_conversations)}")
    print(f"Language distribution: {combined_stats['language_distribution']}")
    print(f"Domain distribution: {combined_stats['domain_distribution']}")


if __name__ == "__main__":
    combine_datasets()
