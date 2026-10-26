# NexusAI Knowledge Base Guide

## Overview
NexusAI এর নলেজ বেসে সাধারণ জ্ঞানের ডেটা সফলভাবে যোগ করা হয়েছে। এখন আপনার AI বিভিন্ন বিষয়ের উত্তর দিতে সক্ষম।

## Current Knowledge Base

### Topics Covered:
1. **Science** - বিজ্ঞানের সংজ্ঞা ও শাখাসমূহ
2. **Mathematics** - গণিতের মৌলিক ধারণা
3. **Computer Science** - কম্পিউটার বিজ্ঞানের অধ্যয়ন
4. **Physics** - পদার্থবিজ্ঞানের মূল বিষয়সমূহ
5. **Chemistry** - রসায়ন বিজ্ঞান
6. **Biology** - জীববিজ্ঞান
7. **History** - ইতিহাস অধ্যয়ন
8. **Philosophy** - দর্শন ও দার্শনিক প্রশ্ন
9. **Economics** - অর্থনীতি
10. **Geography** - ভূগোল

## Sample Questions Your AI Can Answer

### Science & Mathematics
- "What is science?"
- "Tell me about the branches of science"
- "What is mathematics?"
- "Explain the study of physics"
- "What does chemistry study?"
- "Tell me about biology"

### Computer Science
- "What is computer science?"
- "Explain programming language theory"
- "What are algorithms and data structures?"
- "Tell me about computer architecture"

### Social Sciences
- "What is economics?"
- "Explain microeconomics vs macroeconomics"
- "What is history?"
- "How do historians study the past?"
- "What is philosophy?"
- "What are philosophical questions?"

### Geography
- "What is geography?"
- "What is physical geography?"
- "What is human geography?"

## How to Add More Data

### Method 1: Direct Text Ingestion
ফাইল `packages/ai-core/knowledge/raw/ingest_sample_data.py` এ নতুন ডেটা যোগ করুন:

```python
{
    "text": "Your content here...",
    "source": "https://your-source.com",
    "source_type": "web",
    "metadata": {
        "topic": "Your Topic",
        "category": "General Knowledge",
        "trust_level": "TIER_2"
    }
}
```

তারপর রান করুন:
```bash
cd packages/ai-core/knowledge/raw
python ingest_sample_data.py
```

### Method 2: File Upload
আপনার কাছে যদি ফাইল থাকে:

```python
from pipeline.ingestion_pipeline import KnowledgeIngestionPipeline

pipeline = KnowledgeIngestionPipeline()
result = await pipeline.ingest_from_file(
    file_path="path/to/your/file.txt",
    source="your-source",
    source_type="user_uploaded"
)
```

### Method 3: Web Scraping
Wikipedia বা অন্য ওয়েবসাইট থেকে ডেটা স্ক্র্যাপ করতে:

```bash
cd packages/ai-core/knowledge/raw
python simple_web_scraper.py
```

**Note:** Wikipedia rate limiting করতে পারে, তাই ধীরে ধীরে স্ক্র্যাপ করুন।

## Testing the Knowledge Base

টেস্ট করতে রান করুন:
```bash
cd packages/ai-core/knowledge/raw
python test_knowledge.py
```

## Knowledge Statistics

- **Total Documents:** 20
- **Total Chunks:** 24
- **Topics:** 10 major categories
- **Languages:** English (প্রধান), Bengali (স্বাস্থ্য সম্পর্কিত)

## Suggested Topics to Add

আপনি নিচের বিষয়গুলো যোগ করতে পারেন:

1. **Programming Languages** - Python, JavaScript, etc.
2. **World History** - নির্দিষ্ট ঘটনা ও সময়কাল
3. **Technology** - AI, Machine Learning, etc.
4. **Health & Medicine** - স্বাস্থ্য সম্পর্কিত তথ্য
5. **Culture & Arts** - সংস্কৃতি ও শিল্প
6. **Environment** - পরিবেশ ও জলবায়ু
7. **Sports** - খেলাধুলা সম্পর্কিত তথ্য
8. **Business** - ব্যবসা ও উদ্যোগ

## File Locations

- **Raw Data:** `packages/ai-core/knowledge/raw/`
- **Cleaned Data:** `packages/ai-core/knowledge/cleaned/`
- **Pipeline:** `packages/ai-core/knowledge/pipeline/`
- **Retrieval System:** `packages/ai-core/knowledge/store/`

## Next Steps

1. আরও ডেটা যোগ করুন আপনার প্রয়োজন অনুযায়ী
2. Retrieval system টেস্ট করুন
3. AI মডেলের সাথে ইন্টিগ্রেট করুন
4. ব্যবহারকারী ইন্টারফেস থেকে কুইরি করুন

## Support

যেকোনো সমস্যা হলে চেক করুন:
- ডেটা সঠিকভাবে ইনজেস্ট হয়েছে কিনা
- ফাইল পাথ সঠিক কিনা
- Python dependencies ইনস্টল আছে কিনা
