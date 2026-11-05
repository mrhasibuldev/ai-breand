"""
Phase 9 - Dataset Discovery and License Verification

Discovers and verifies suitable Bengali and English datasets for expansion.
"""

import json
from pathlib import Path
from datetime import datetime

# Paths
AI_CORE_DIR = Path(__file__).parent.parent
DATA_DIR = AI_CORE_DIR / "data"
PHASE9_DIR = DATA_DIR / "experimental" / "phase9"
MANIFESTS_DIR = PHASE9_DIR / "manifests"

# Create directories
PHASE9_DIR.mkdir(parents=True, exist_ok=True)
MANIFESTS_DIR.mkdir(parents=True, exist_ok=True)

print("="*60)
print("Phase 9 - Dataset Discovery and License Verification")
print("="*60)

# Dataset candidates based on web search
dataset_candidates = [
    # Bengali Datasets
    {
        "name": "bengali_chat_conv",
        "source": "Hugging Face",
        "url": "https://huggingface.co/datasets/spedrox-sac/bengali_chat_conv",
        "language": "Bengali",
        "type": "Conversation/QA",
        "estimated_size": "323 KB",
        "estimated_records": 1074,
        "license": "UNKNOWN",
        "license_url": None,
        "commercial_use": "UNKNOWN",
        "notes": "License not specified in search results. Must verify before use."
    },
    {
        "name": "bengali_sft_v1",
        "source": "Hugging Face",
        "url": "https://huggingface.co/datasets/worldjit/bengali-sft-v1",
        "language": "Bengali",
        "type": "Instruction-following",
        "estimated_size": "UNKNOWN",
        "estimated_records": "UNKNOWN",
        "license": "UNKNOWN",
        "license_url": None,
        "commercial_use": "UNKNOWN",
        "notes": "License not specified in search results. Must verify before use."
    },
    {
        "name": "Bangla_NLP_Dataset",
        "source": "GitHub",
        "url": "https://github.com/Foysal87/Bangla-NLP-Dataset",
        "language": "Bengali",
        "type": "NER, POS, Wiki articles",
        "estimated_size": "UNKNOWN",
        "estimated_records": "UNKNOWN",
        "license": "MIT",
        "license_url": "https://opensource.org/licenses/MIT",
        "commercial_use": "APPROVED",
        "notes": "MIT License approved for commercial use. Contains multiple dataset types."
    },
    {
        "name": "B_CORE_bengali_corpus",
        "source": "Hugging Face",
        "url": "https://huggingface.co/datasets/nahid-hub/B-CORE-bengali-corpus",
        "language": "Bengali",
        "type": "Pretraining corpus",
        "estimated_size": "52 GB (20.8 GB compressed)",
        "estimated_records": 16500000,
        "license": "CC BY 4.0",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "commercial_use": "CONDITIONAL",
        "notes": "CC BY 4.0 - commercial use with attribution. TOO LARGE for current storage (3.31 GB free)."
    },
    {
        "name": "KrishokChat",
        "source": "Hugging Face",
        "url": "https://huggingface.co/datasets/RaiyanKhaan/KrishokChat",
        "language": "Bengali",
        "type": "Agricultural Q&A",
        "estimated_size": "UNKNOWN",
        "estimated_records": 85979,
        "license": "UNKNOWN",
        "license_url": None,
        "commercial_use": "UNKNOWN",
        "notes": "License not specified in search results. Must verify before use."
    },

    # English Datasets
    {
        "name": "InstructionFineTuning_smallDataset",
        "source": "Hugging Face",
        "url": "https://huggingface.co/datasets/Manas2001/InstructionFineTuning-smallDataset",
        "language": "English",
        "type": "Instruction-following",
        "estimated_size": "UNKNOWN",
        "estimated_records": "UNKNOWN",
        "license": "UNKNOWN",
        "license_url": None,
        "commercial_use": "UNKNOWN",
        "notes": "License not specified in search results. Must verify before use."
    },
    {
        "name": "instruct_v3",
        "source": "Hugging Face",
        "url": "https://huggingface.co/datasets/mosaicml/instruct-v3",
        "language": "English",
        "type": "Instruction-following (aggregate)",
        "estimated_size": "UNKNOWN",
        "estimated_records": "UNKNOWN",
        "license": "CC BY-SA 3.0",
        "license_url": "https://creativecommons.org/licenses/by-sa/3.0/",
        "commercial_use": "CONDITIONAL",
        "notes": "CC BY-SA 3.0 - commercial use with attribution and share-alike."
    },
    {
        "name": "Daring_Anteater",
        "source": "Hugging Face",
        "url": "https://huggingface.co/datasets/nvidia/Daring-Anteater",
        "language": "English",
        "type": "Instruction-following",
        "estimated_size": "UNKNOWN",
        "estimated_records": "UNKNOWN",
        "license": "CC BY 4.0",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "commercial_use": "CONDITIONAL",
        "notes": "CC BY 4.0 - commercial use with attribution. Contains synthetic data."
    },

    # Mixed/Indic Datasets
    {
        "name": "Bhasha_SFT",
        "source": "Soket AI Labs",
        "url": "https://soket.ai/blogs/bhasha_sft",
        "language": "Hindi, Gujarati, Bengali, English",
        "type": "Instruction-following",
        "estimated_size": "UNKNOWN",
        "estimated_records": 13000000,
        "license": "CC-BY-4.0, Apache-2.0, MIT",
        "license_url": None,
        "commercial_use": "CONDITIONAL",
        "notes": "Mixed licenses - need to verify which parts are under which license. 13M pairs - verify size."
    },
    {
        "name": "Indic_Glossaries",
        "source": "AI4Bharat",
        "url": "https://github.com/AI4Bharat/Indic-Glossaries",
        "language": "Multiple Indic languages",
        "type": "Glossary/Translation",
        "estimated_size": "UNKNOWN",
        "estimated_records": 102855,  # English-Bengali pairs
        "license": "CC BY 4.0",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "commercial_use": "CONDITIONAL",
        "notes": "CC BY 4.0 - commercial use with attribution. 102,855 English-Bengali pairs."
    },

    # Excluded Datasets
    {
        "name": "banglanmt",
        "source": "GitHub",
        "url": "https://github.com/csebuetnlp/banglanmt",
        "language": "Bengali-English",
        "type": "Machine Translation",
        "estimated_size": "UNKNOWN",
        "estimated_records": 2750000,
        "license": "CC BY-NC-SA 4.0",
        "license_url": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
        "commercial_use": "REJECTED",
        "notes": "CC BY-NC-SA 4.0 - NON-COMMERCIAL ONLY. Excluded from commercial training."
    },
    {
        "name": "GPT-4-LLM",
        "source": "GitHub",
        "url": "https://github.com/Instruction-Tuning-with-GPT-4/GPT-4-LLM",
        "language": "English, Chinese",
        "type": "Instruction-following",
        "estimated_size": "UNKNOWN",
        "estimated_records": 52000,
        "license": "CC BY NC 4.0",
        "license_url": "https://creativecommons.org/licenses/by-nc/4.0/",
        "commercial_use": "REJECTED",
        "notes": "CC BY NC 4.0 - NON-COMMERCIAL ONLY. Excluded from commercial training."
    },
    {
        "name": "hinglish_instruct_dataset",
        "source": "Hugging Face",
        "url": "https://huggingface.co/datasets/Sujalvc/hinglish-instruct-dataset",
        "language": "Hinglish (Romanized Hindi-English)",
        "type": "Instruction-following",
        "estimated_size": "UNKNOWN",
        "estimated_records": 10378,
        "license": "CC BY-NC-SA 4.0",
        "license_url": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
        "commercial_use": "REJECTED",
        "notes": "CC BY-NC-SA 4.0 - NON-COMMERCIAL ONLY. Excluded from commercial training."
    },
]

# Categorize datasets
commercial_approved = [d for d in dataset_candidates if d["commercial_use"] == "APPROVED"]
conditional = [d for d in dataset_candidates if d["commercial_use"] == "CONDITIONAL"]
non_commercial = [d for d in dataset_candidates if d["commercial_use"] == "REJECTED"]
unknown = [d for d in dataset_candidates if d["commercial_use"] == "UNKNOWN"]

print(f"\nTotal datasets discovered: {len(dataset_candidates)}")
print(f"Commercial-approved: {len(commercial_approved)}")
print(f"Conditional (attribution required): {len(conditional)}")
print(f"Non-commercial (rejected): {len(non_commercial)}")
print(f"Unknown license: {len(unknown)}")

# Save manifest
manifest = {
    "discovery_timestamp": datetime.now().isoformat(),
    "total_datasets": len(dataset_candidates),
    "commercial_approved": len(commercial_approved),
    "conditional": len(conditional),
    "non_commercial": len(non_commercial),
    "unknown": len(unknown),
    "datasets": dataset_candidates
}

manifest_path = MANIFESTS_DIR / "dataset_discovery_manifest.json"
with open(manifest_path, 'w', encoding='utf-8') as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)

print(f"\nManifest saved: {manifest_path}")

# Print summary
print("\n" + "="*60)
print("COMMERCIAL-APPROVED DATASETS")
print("="*60)
for d in commercial_approved:
    print(f"\nName: {d['name']}")
    print(f"Source: {d['source']}")
    print(f"Language: {d['language']}")
    print(f"Type: {d['type']}")
    print(f"License: {d['license']}")
    print(f"URL: {d['url']}")

print("\n" + "="*60)
print("CONDITIONAL-LICENSE DATASETS (Attribution Required)")
print("="*60)
for d in conditional:
    print(f"\nName: {d['name']}")
    print(f"Source: {d['source']}")
    print(f"Language: {d['language']}")
    print(f"Type: {d['type']}")
    print(f"License: {d['license']}")
    print(f"URL: {d['url']}")
    print(f"Notes: {d['notes']}")

print("\n" + "="*60)
print("NON-COMMERCIAL DATASETS (Rejected)")
print("="*60)
for d in non_commercial:
    print(f"\nName: {d['name']}")
    print(f"License: {d['license']}")
    print(f"Reason: Non-commercial only")

print("\n" + "="*60)
print("UNKNOWN-LICENSE DATASETS (Require Verification)")
print("="*60)
for d in unknown:
    print(f"\nName: {d['name']}")
    print(f"Source: {d['source']}")
    print(f"URL: {d['url']}")
    print(f"Notes: {d['notes']}")

print("\n" + "="*60)
print("DISCOVERY COMPLETE")
print("="*60)
