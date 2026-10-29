# NexusAI Dataset Collection Tooling

**Stage**: B4-B2: Original Data Collection Implementation  
**Date**: 2026-10-29  
**Purpose**: Infrastructure for collecting, validating, and exporting original NexusAI training data

---

## Overview

This directory contains the dataset collection tooling for NexusAI's original Bengali-first training data. The tooling implements:

- **Schema v2.0**: Versioned dataset schema with comprehensive metadata
- **Validation**: Automated quality, privacy, and provenance checks
- **Processing**: Deterministic train/validation/test splitting without leakage
- **Export**: Safe export of approved records only
- **Testing**: Comprehensive test suite

---

## Files

### Core Implementation

- **`dataset_schema.py`**: Dataset schema definitions (v2.0)
  - `Dataset`: Complete dataset with metadata, statistics, conversations
  - `ConversationRecord`: Single conversation with full metadata
  - `Message`: Individual message in a conversation
  - Enums: `Language`, `Domain`, `SourceType`, `ReviewStatus`, `LicenseStatus`, `PrivacyStatus`, `Split`

- **`dataset_validator.py`**: Validation and quality checks
  - `DatasetValidator`: Validates records and datasets
  - Schema validation (required fields, types, enum values)
  - Quality validation (empty content, conversation flow)
  - Privacy validation (PII detection patterns)
  - Provenance validation (license status checks)
  - Duplicate detection (exact and near-duplicate)

- **`dataset_processor.py`**: Dataset processing and export
  - `DatasetProcessor`: Processes datasets for training
  - Record approval/rejection workflow
  - Deterministic split generation (conversation-level)
  - Approved-only export with overwrite protection
  - Quality report generation
  - Unverified record blocking

### Testing

- **`test_fixtures.py`**: Test fixtures for validation
  - Valid test records (Bengali, English, mixed)
  - Invalid test records (empty messages, unverified license, PII)
  - **IMPORTANT**: All fixtures are labeled as "TEST FIXTURE - DO NOT USE FOR TRAINING"

- **`test_dataset.py`**: Comprehensive test suite
  - 16 tests covering schema, validation, and processing
  - All tests passing

---

## Usage

### Creating a Dataset

```python
from dataset_schema import Dataset
from dataset_processor import DatasetProcessor

processor = DatasetProcessor(random_seed=42)
dataset = processor.create_dataset("nexusai-original", "1.0.0")
```

### Adding Records

```python
from dataset_schema import ConversationRecord, Message, Language, Domain, SourceType, ReviewStatus, LicenseStatus, PrivacyStatus

record = ConversationRecord(
    record_id="REC-20261029-0001",
    dataset_version="1.0.0",
    conversation_id="CONV-20261029-0001",
    split=Split.PENDING,
    language=Language.BENGALI,
    domain=Domain.CONVERSATION,
    messages=[
        Message(role="user", content="তোমার নাম কি?", language=Language.BENGALI, turn_index=0),
        Message(role="assistant", content="আমার নাম NexusAI।", language=Language.BENGALI, turn_index=1)
    ],
    source_type=SourceType.ORIGINAL_HUMAN,
    source_reference="manual authoring",
    creator="dataset-team",
    created_at="2026-10-29T10:00:00Z",
    review_status=ReviewStatus.PENDING,
    quality_score=0.0,
    license_status=LicenseStatus.PROJECT_OWNED,
    privacy_status=PrivacyStatus.PUBLIC
)

result = processor.add_record(dataset, record)
if result.is_valid:
    print("Record added successfully")
else:
    print(f"Validation failed: {result.to_dict()}")
```

### Approval Workflow

```python
# Approve a record
approved = processor.approve_record(record, reviewer="dataset-lead")

# Reject a record
rejected = processor.reject_record(record, reviewer="dataset-lead", reason="Quality too low")
```

### Generating Splits

```python
# Only approved records are split
result = processor.generate_splits(dataset, train_ratio=0.8, val_ratio=0.1, test_ratio=0.1)

# Verify split integrity
integrity_result = processor.validate_split_integrity(dataset)
```

### Exporting Approved Records

```python
# Dry run (no file created)
result = processor.export_approved(dataset, "output.json", dry_run=True)

# Actual export (with overwrite protection)
result = processor.export_approved(dataset, "output.json", dry_run=False, overwrite_protection=True)
```

### Quality Report

```python
report = processor.generate_quality_report(dataset)
print(json.dumps(report, indent=2))
```

---

## Schema v2.0 Fields

### Conversation-Level Metadata

- `record_id`: Unique record identifier (format: REC-YYYYMMDD-NNNN)
- `dataset_version`: Dataset version this record belongs to
- `conversation_id`: Unique conversation identifier (format: CONV-YYYYMMDD-NNNN)
- `split`: Dataset split (train/validation/test/pending)
- `language`: Primary language (bengali/english/mixed/unknown)
- `domain`: Primary domain (conversation/knowledge/reasoning/mathematics/coding/writing/planning/health_wellness/other)
- `messages`: Array of message objects
- `source_type`: Origin (original_human/original_synthetic/imported/converted)
- `source_reference`: Description of source
- `creator`: Person or process that created record
- `created_at`: ISO-8601 timestamp
- `review_status`: Approval status (pending/approved/rejected)
- `reviewer`: Person who reviewed the record
- `review_date`: Date of review
- `quality_score`: 0.0-1.0 quality rating
- `license_status`: Licensing status (project-owned/verified-external/unverified)
- `license_reference`: License identifier or URL
- `privacy_status`: Privacy classification (public/private/contains_pii)
- `tags`: Optional categorization tags
- `notes`: Optional notes

### Message-Level Fields

- `role`: "user" or "assistant"
- `content`: Message text
- `language`: Detected or annotated language
- `turn_index`: Index in conversation (0, 1, 2, ...)

---

## Validation Rules

### Automatic Rejections (Errors)

1. **Missing required fields**: Any required field missing
2. **Invalid enum values**: Language, domain, source_type, etc. not in allowed values
3. **Empty messages**: Message content is empty or whitespace-only
4. **Malformed conversation**: Wrong role sequence, missing turn indices
5. **Unverified license**: Imported data without verified license
6. **Contains PII**: Credit card patterns detected
7. **Duplicate conversations**: Exact duplicate of existing conversation

### Warnings

1. **Language label mismatch**: Annotated language doesn't match detected language
2. **Email address detected**: Possible PII
3. **Phone number detected**: Possible PII
4. **Statistics mismatch**: Dataset statistics don't match actual counts

---

## Privacy and Provenance Safeguards

### License Status Blocking

- `project-owned`: Automatically approved for use
- `verified-external`: Must have permissive license (CC-BY, Apache-2.0, MIT)
- `unverified`: BLOCKED from training
- Non-commercial licenses (CC-BY-NC): BLOCKED from training

### Privacy Status Blocking

- `public`: No restrictions
- `private`: Internal project data
- `contains_pii`: BLOCKED from training until PII removed

### PII Detection Patterns

- Email addresses: `\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b`
- Phone numbers: `\b\d{3}[-.]?\d{3}[-.]?\d{4}\b`
- Bangladesh phones: `\b\+?880\d{10}\b`
- Credit cards: `\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b`

---

## Split Generation

### Deterministic Conversation-Level Splitting

- Fixed random seed for reproducibility
- Conversation-level splitting (all messages from same conversation stay together)
- No conversation appears in multiple splits
- Default ratios: 80% train, 10% validation, 10% test
- Only approved records are split

### Integrity Validation

- Verifies no conversation appears in multiple splits
- Validates language distribution across splits
- Validates domain distribution across splits

---

## Export Safety

### Approved-Only Export

- Only records with `review_status == "approved"` are exported
- Unverified licenses are automatically blocked before export
- Records with PII are blocked

### Overwrite Protection

- Default: prevents overwriting existing files
- Can be disabled with `overwrite_protection=False`
- Dry-run mode available for preview

### Export Format

- JSON with schema v2.0 structure
- Includes metadata, statistics, and conversations
- UTF-8 encoding with `ensure_ascii=False` for Bengali support

---

## Testing

### Running Tests

```bash
cd packages/ai-core/data
python test_dataset.py
```

### Test Coverage

- Schema validation (2 tests)
- Validator checks (5 tests)
- Processor operations (9 tests)
- Total: 16 tests

### Test Results

All 16 tests passing:
- Schema: valid record, dataset creation/serialization
- Validator: valid record, empty messages, unverified license, PII detection, duplicates
- Processor: add record, reject invalid, approve/reject, split generation, export approved, dry run, overwrite protection, block unverified, quality report

---

## Integration with Existing Datasets

### Blocking Existing Datasets

All existing datasets remain BLOCKED due to unverified licensing:
- `train_v2.json` (502 conversations)
- `conversational_data.json` (28 records)
- `train_cleaned.json` (19 strings)
- All external datasets

### Conversion Path

Existing datasets can be converted to schema v2.0 format if:
1. License is verified as permissive (CC-BY, Apache-2.0, MIT)
2. License permits commercial use
3. License permits redistribution or project-internal use
4. PII is removed
5. Records pass schema validation

Until license verification completes, existing datasets remain BLOCKED.

---

## Next Steps

### Data Collection

1. Draft original examples following schema v2.0
2. Submit for review (factual, linguistic, quality)
3. Privacy review
4. Approval or rejection
5. Accumulate approved records
6. Generate splits when sufficient data collected

### Target: Pilot Dataset

- Goal: ~100 original conversations
- Composition: Bengali-first (~50%), English (~30%), mixed (~20%)
- Domains: Conversation, knowledge, reasoning, health_wellness
- Status: Infrastructure ready, real pilot data to be collected

### Future Enhancements

- Near-duplicate detection with Jaccard similarity
- Automated language detection improvement
- Coherence scoring algorithms
- Fact verification for knowledge domain
- Integration with frontend data collection UI

---

## Limitations

### Current Implementation

- No database backend (JSON-based storage)
- No automated fact verification
- No advanced near-duplicate detection
- No frontend integration
- No collaborative review workflow

### Resource Constraints

- Disk space: ~4 GB free (sufficient for small datasets)
- RAM: ~8 GB total (sufficient for processing)
- CPU: 2 physical cores (adequate for validation/processing)

### Unverified Existing Data

All existing datasets remain BLOCKED until license verification completes. This tooling does not automatically approve existing data.

---

## Safety Principles

1. **Quality over quantity**: Better to have 100 high-quality records than 10,000 low-quality records
2. **Bengali-first approach**: Prioritize Bengali examples, then English, then mixed
3. **Clear provenance**: Every record must have traceable origin
4. **Privacy by design**: PII detection and blocking
5. **License verification**: No unverified or non-commercial data
6. **Reproducible splits**: Fixed random seed for deterministic behavior
7. **Safe exports**: Overwrite protection, approved-only export
8. **Human oversight**: Automated checks flag uncertain cases for manual review
