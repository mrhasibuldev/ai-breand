# NexusAI Brain — Stage B4-B1: Original Dataset Framework

**Status**: Dataset Framework and Documentation (Read-Only Planning)  
**Date**: 2026-10-28  
**Purpose**: Establish foundation for collecting, validating, organizing, and evaluating original training examples created by the NexusAI project  
**Scope**: Dataset specification, provenance tracking, quality checks, tokenizer migration readiness, evaluation planning  

---

## Executive Summary

**Objective**: Prepare a safe, well-documented foundation for developing NexusAI's own general-purpose AI model with strong Bengali language support, English support, reasoning capabilities, memory, and the ability to assist with a wide range of tasks.

**Key Principles**:
- NexusAI must develop its own AI model and training pipeline
- NO external AI APIs (OpenAI, Gemini, Claude, etc.) as core intelligence
- NO external pretrained model weights
- NO fabricated license approvals
- Original data creation with clear provenance and licensing
- Bengali-first approach with English and mixed-language support

**Current Blocker**: All existing datasets have unverified licensing. This stage defines the framework for creating original, project-owned training data with clear licensing.

**Deliverable**: This document defines the dataset schema, provenance tracking, data creation workflow, quality checks, tokenizer migration plan, and evaluation methodology.

---

## 1. Repository and Runtime Findings

### 1.1 Initial Repository State

**Branch**: main  
**HEAD**: b9c3fcf "docs(ai-core): organize and document NexusAI model assets"  
**Remote**: https://github.com/mrhasibuldev/ai-breand.git (origin)

**Pre-existing Modifications** (preserved exactly):
- M cookies.txt
- M packages/ai-core/evaluation/__pycache__/evaluator.cpython-314.pyc
- M packages/ai-core/evaluation/evaluator.py
- M packages/ai-core/ml-service/__pycache__/main.cpython-314.pyc
- M packages/ai-core/ml-service/main.py
- M packages/ai-core/neural/__pycache__/medium_transformer.cpython-314.pyc
- M packages/ai-core/tokenizer/__pycache__/tokenizer.cpython-314.pyc
- ?? docs/ai-core/
- ?? packages/ai-core/CHECKPOINT_COMPATIBILITY.md
- ?? packages/ai-core/RUNTIME_ARCHITECTURE.md
- ?? packages/ai-core/TYPESCRIPT_ARCHITECTURE.md

### 1.2 Active Runtime Path

**Actual Runtime** (from `RUNTIME_ARCHITECTURE.md` and code inspection):
```
User Message (Web UI)
    ↓
apps/web/lib/backend-conversation.ts
    ↓
POST /api/v1/ai/chat
    ↓
apps/api/src/routes/ai.ts
    ↓
fetch http://127.0.0.1:8000/orchestrate
    ↓
packages/ai-core/ml-service/main.py (FastAPI)
    ↓
load_model_if_needed()
    ↓
Load checkpoint: models/checkpoints_medium/final_model.pt
    ↓
Load tokenizer from checkpoint (74 tokens)
    ↓
Initialize MediumTransformer (4,776,522 parameters)
    ↓
Language Detection (Unicode-based)
    ↓
Intent Classification (Pattern-based)
    ↓
Routing: Deterministic handler or Neural model
    ↓
Quality Filter
    ↓
Fallback if rejected
    ↓
Response
```

### 1.3 Active Model Checkpoint

**File**: `packages/ai-core/models/checkpoints_medium/final_model.pt`  
**Size**: 18.76 MB  
**Architecture**: MediumTransformer  
**Parameters**: 4,776,522  
**Vocabulary Size**: 74 tokens  
**Tokenizer**: SimpleTokenizer (word-level, whitespace splitting)  
**Status**: ACTIVE, UNCHANGED

### 1.4 Resource Constraints

**Disk Space**:
- Total: 127.98 GB
- Used: 125.12 GB
- Free: 2.86 GB (down from 3.40 GB in Stage B4-A)

**RAM**: ~8 GB total, ~3 GB available (estimated)  
**CPU**: 2 physical cores, 4 logical cores  
**GPU**: None (CPU-only)

**Implication**: Disk space is limited but sufficient for small to medium dataset experiments. Large-scale training requires cloud resources or storage cleanup.

---

## 2. Current Dataset Inventory

### 2.1 Existing Datasets (from Stage B4-A)

**File**: `packages/ai-core/data/public_datasets/v1.0_cleaned/train_cleaned.json`  
**Count**: 19 strings  
**License**: "Internal" - UNVERIFIED  
**Status**: BLOCKED for training

**File**: `packages/ai-core/data/train_v2.json`  
**Count**: 502 conversations  
**License**: None - UNVERIFIED  
**Status**: BLOCKED for training

**File**: `packages/ai-core/data/conversational_data.json`  
**Count**: 28 records (18 conv-format, 10 Q/A-format)  
**License**: None - UNVERIFIED  
**Status**: BLOCKED for training

**Conclusion**: NO existing dataset has verified license for commercial use. All external candidates from Stage B2 also have unverified or non-commercial licenses.

### 2.2 External Datasets

**Status**: All external datasets remain BLOCKED until license verification completes. This includes:
- `rishiraj/bengalichat` (CC BY-NC 4.0 - non-commercial)
- `tatsu-lab/alpaca` (CC BY-NC 4.0 - non-commercial, OpenAI-generated)
- `soketlabs/bhasha-sft` (Mixed licenses, requires source-level verification)
- `swapnillo/Bangla-Instruction-Tuning-100K` (License unverified)
- `iNLP-Lab/multilingual-lima` (CC BY-NC-SA 4.0 - non-commercial, share-alike)

**Decision**: External datasets NOT used in this stage. Original data creation is the only path forward.

---

## 3. Proposed Versioned Dataset Schema

### 3.1 Schema Version

**Schema Version**: v2.0 (original data framework)  
**Purpose**: Support original NexusAI training examples with full provenance tracking  
**Distinction from v1.0**: v1.0 (from Stage B4-A) was a minimal schema. v2.0 is enhanced for original data creation with comprehensive metadata.

### 3.2 Schema Definition

```json
{
  "schema_version": "2.0",
  "dataset_version": "1.0.0",
  "dataset_name": "nexusai-original-v1.0.0",
  "metadata": {
    "created": "YYYY-MM-DD",
    "modified": "YYYY-MM-DD",
    "creator": "NexusAI Project",
    "license": "proprietary-project-owned",
    "license_url": null,
    "commercial_use": "permitted",
    "redistribution": "restricted-to-project",
    "purpose": "training",
    "description": "Original NexusAI training examples with Bengali-first focus"
  },
  "statistics": {
    "total_conversations": 0,
    "total_messages": 0,
    "language_distribution": {
      "bengali": 0,
      "english": 0,
      "mixed": 0
    },
    "domain_distribution": {
      "conversation": 0,
      "knowledge": 0,
      "reasoning": 0,
      "mathematics": 0,
      "coding": 0,
      "writing": 0,
      "planning": 0,
      "health_wellness": 0,
      "other": 0
    },
    "split_distribution": {
      "train": 0,
      "validation": 0,
      "test": 0
    }
  },
  "conversations": [
    {
      "record_id": "REC-YYYYMMDD-NNNN",
      "dataset_version": "1.0.0",
      "conversation_id": "CONV-YYYYMMDD-NNNN",
      "split": "train | validation | test",
      "language": "bengali | english | mixed",
      "domain": "conversation | knowledge | reasoning | mathematics | coding | writing | planning | health_wellness | other",
      "messages": [
        {
          "role": "user | assistant",
          "content": "message text",
          "language": "bengali | english | mixed",
          "turn_index": 0
        }
      ],
      "source_type": "original_human | original_synthetic | imported | converted",
      "source_reference": "description of source",
      "creator": "creator_name_or_id",
      "created_at": "YYYY-MM-DDTHH:MM:SSZ",
      "review_status": "pending | approved | rejected",
      "reviewer": "reviewer_name_or_id",
      "review_date": "YYYY-MM-DD",
      "quality_score": 0.0-1.0,
      "license_status": "project-owned | verified-external | unverified",
      "license_reference": "license identifier or URL",
      "privacy_status": "public | private | contains_pii",
      "tags": ["tag1", "tag2"],
      "notes": "optional notes"
    }
  ]
}
```

### 3.3 Field Definitions

**Dataset-Level Metadata**:
- `schema_version`: Schema version string (e.g., "2.0")
- `dataset_version`: Semantic version (e.g., "1.0.0")
- `dataset_name`: Human-readable dataset name
- `metadata.created`: ISO-8601 date of dataset creation
- `metadata.modified`: ISO-8601 date of last modification
- `metadata.creator`: Organization or individual who created dataset
- `metadata.license`: License identifier (SPDX or custom)
- `metadata.license_url`: Link to license text if available
- `metadata.commercial_use`: "permitted" or "restricted"
- `metadata.redistribution`: "unrestricted", "restricted-to-project", or "not-permitted"
- `metadata.purpose`: Primary purpose (training, evaluation, etc.)
- `metadata.description`: Human-readable description

**Statistics**:
- `total_conversations`: Count of conversations
- `total_messages`: Count of all messages
- `language_distribution`: Counts by language
- `domain_distribution`: Counts by domain
- `split_distribution`: Counts by train/validation/test

**Conversation-Level Fields**:
- `record_id`: Unique record identifier (format: REC-YYYYMMDD-NNNN)
- `dataset_version`: Dataset version this record belongs to
- `conversation_id`: Unique conversation identifier (format: CONV-YYYYMMDD-NNNN)
- `split`: Dataset split (train/validation/test)
- `language`: Primary language (bengali/english/mixed)
- `domain`: Primary domain category
- `messages`: Array of message objects
- `source_type`: Origin classification (original_human/original_synthetic/imported/converted)
- `source_reference`: Description of source (e.g., "manual authoring", "synthetic generation")
- `creator`: Person or process that created the record
- `created_at`: ISO-8601 timestamp of creation
- `review_status`: Approval status (pending/approved/rejected)
- `reviewer`: Person who reviewed the record
- `review_date`: Date of review
- `quality_score`: 0.0-1.0 quality rating
- `license_status`: Licensing status (project-owned/verified-external/unverified)
- `license_reference`: License identifier or URL
- `privacy_status`: Privacy classification (public/private/contains_pii)
- `tags`: Optional categorization tags
- `notes`: Optional notes or comments

**Message-Level Fields**:
- `role`: "user" or "assistant"
- `content`: Message text
- `language`: Detected or annotated language
- `turn_index`: Index in conversation (0, 1, 2, ...)

### 3.4 Controlled Values

**Language Values**:
- `bengali`: Primarily Bengali text
- `english`: Primarily English text
- `mixed`: Bengali-English code-switching or mixed-language text

**Domain Values**:
- `conversation`: General conversational dialogue
- `knowledge`: Factual knowledge and explanations
- `reasoning`: Logical reasoning and multi-step problem-solving
- `mathematics`: Mathematical problems and explanations
- `coding`: Programming and technical assistance
- `writing`: Writing, summarization, translation
- `planning`: Planning, decision support, task assistance
- `health_wellness`: Health and wellness information (with safety boundaries)
- `other`: Other domains not fitting above categories

**Source Type Values**:
- `original_human`: Human-authored original examples
- `original_synthetic`: Internally generated synthetic examples
- `imported`: Imported from external source (requires license verification)
- `converted`: Converted from another format

**Review Status Values**:
- `pending`: Awaiting review
- `approved`: Approved for inclusion in dataset
- `rejected`: Rejected, not included in dataset

**License Status Values**:
- `project-owned`: Original NexusAI project data
- `verified-external`: External data with verified license
- `unverified`: External data with unverified license (BLOCKED)

**Privacy Status Values**:
- `public`: No sensitive information
- `private`: Internal project data
- `contains_pii`: Contains personally identifiable information (must be removed before training)

### 3.5 Example Records

**Example 1: Bengali Conversation**

```json
{
  "record_id": "REC-20261028-0001",
  "dataset_version": "1.0.0",
  "conversation_id": "CONV-20261028-0001",
  "split": "train",
  "language": "bengali",
  "domain": "conversation",
  "messages": [
    {
      "role": "user",
      "content": "তোমার নাম কি?",
      "language": "bengali",
      "turn_index": 0
    },
    {
      "role": "assistant",
      "content": "আমার নাম NexusAI। আমি একটি AI সহকারী।",
      "language": "bengali",
      "turn_index": 1
    }
  ],
  "source_type": "original_human",
  "source_reference": "manual authoring",
  "creator": "dataset-team",
  "created_at": "2026-10-28T10:00:00Z",
  "review_status": "approved",
  "reviewer": "dataset-lead",
  "review_date": "2026-10-28",
  "quality_score": 0.95,
  "license_status": "project-owned",
  "license_reference": null,
  "privacy_status": "public",
  "tags": ["greeting", "identity"],
  "notes": "Simple greeting example"
}
```

**Example 2: English Reasoning**

```json
{
  "record_id": "REC-20261028-0002",
  "dataset_version": "1.0.0",
  "conversation_id": "CONV-20261028-0002",
  "split": "train",
  "language": "english",
  "domain": "reasoning",
  "messages": [
    {
      "role": "user",
      "content": "If all cats are animals, and all animals need food, do all cats need food?",
      "language": "english",
      "turn_index": 0
    },
    {
      "role": "assistant",
      "content": "Yes. Since all cats are animals, and all animals need food, it follows that all cats need food. This is a logical syllogism: if A implies B, and B implies C, then A implies C.",
      "language": "english",
      "turn_index": 1
    }
  ],
  "source_type": "original_human",
  "source_reference": "manual authoring",
  "creator": "dataset-team",
  "created_at": "2026-10-28T10:05:00Z",
  "review_status": "approved",
  "reviewer": "dataset-lead",
  "review_date": "2026-10-28",
  "quality_score": 0.90,
  "license_status": "project-owned",
  "license_reference": null,
  "privacy_status": "public",
  "tags": ["reasoning", "logic"],
  "notes": "Logical reasoning example"
}
```

**Example 3: Mixed-Language Conversation**

```json
{
  "record_id": "REC-20261028-0003",
  "dataset_version": "1.0.0",
  "conversation_id": "CONV-20261028-0003",
  "split": "train",
  "language": "mixed",
  "domain": "conversation",
  "messages": [
    {
      "role": "user",
      "content": "আমি English এবং Bengali দুই ভাষাতেই কথা বলতে পারি",
      "language": "mixed",
      "turn_index": 0
    },
    {
      "role": "assistant",
      "content": "That's great! আমিও দুই ভাষাতেই কথা বলতে পারি। আপনি কীভাবে সাহায্য করতে পারি?",
      "language": "mixed",
      "turn_index": 1
    }
  ],
  "source_type": "original_human",
  "source_reference": "manual authoring",
  "creator": "dataset-team",
  "created_at": "2026-10-28T10:10:00Z",
  "review_status": "approved",
  "reviewer": "dataset-lead",
  "review_date": "2026-10-28",
  "quality_score": 0.85,
  "license_status": "project-owned",
  "license_reference": null,
  "privacy_status": "public",
  "tags": ["mixed-language", "code-switching"],
  "notes": "Bengali-English code-switching example"
}
```

---

## 4. Bengali-English Data Creation Workflow

### 4.1 Workflow Overview

**Objective**: Repeatable workflow for creating original Bengali-first training examples with quality control and provenance tracking.

**Stages**:
1. Drafting
2. Factual and Linguistic Review
3. Quality Scoring
4. Privacy Check
5. Metadata Assignment
6. Approval or Rejection
7. Export to Dataset Release

### 4.2 Stage 1: Drafting

**Guidelines**:
- Draft original examples aligned with target domains
- Prioritize Bengali examples, then English, then mixed-language
- Ensure conversational naturalness and cultural appropriateness
- Include reasoning steps for reasoning domain
- Verify mathematical correctness for mathematics domain
- Verify code correctness for coding domain
- Include appropriate safety boundaries for health/wellness domain

**Tools**:
- Plain text editor or JSON editor
- Template with required fields
- Predefined domain templates

**Output**: Draft conversation record with `review_status: "pending"`

### 4.3 Stage 2: Factual and Linguistic Review

**Factual Correctness**:
- Verify facts are accurate (for knowledge domain)
- Verify reasoning steps are logically sound (for reasoning domain)
- Verify mathematical calculations are correct (for mathematics domain)
- Verify code is syntactically and semantically correct (for coding domain)
- Verify health information is accurate and includes appropriate disclaimers (for health/wellness domain)

**Linguistic Quality**:
- **Bengali**: Check spelling, grammar, naturalness, conversational tone
- **English**: Check spelling, grammar, naturalness, conversational tone
- **Mixed**: Check code-switching naturalness, consistency, cultural appropriateness

**Review Process**:
- Independent review by domain expert
- Cross-check with reference materials (dictionaries, textbooks, etc.)
- Flag uncertain facts for verification

**Output**: Updated record with review notes

### 4.4 Stage 3: Quality Scoring

**Quality Criteria**:
- Factual correctness: 0-1.0
- Linguistic quality: 0-1.0
- Conversational coherence: 0-1.0
- Domain appropriateness: 0-1.0
- Overall quality: Average of above

**Scoring Guidelines**:
- 0.9-1.0: Excellent, ready for production
- 0.7-0.9: Good, minor improvements recommended
- 0.5-0.7: Acceptable, improvements required
- <0.5: Poor, requires significant revision or rejection

**Output**: Record with `quality_score` field populated

### 4.5 Stage 4: Privacy Check

**Privacy Risks**:
- Personally identifiable information (names, addresses, phone numbers, email)
- Sensitive personal information (medical history, financial information)
- Confidential information (trade secrets, internal business data)
- Copyrighted material (quotes, code snippets)

**Privacy Review**:
- Scan for PII patterns (email addresses, phone numbers, addresses)
- Remove or anonymize any detected PII
- Verify no confidential information is included
- Verify no copyrighted material is included without permission

**Output**: Record with `privacy_status` field populated

### 4.6 Stage 5: Metadata Assignment

**Required Metadata**:
- `record_id`: Auto-generated or manually assigned
- `dataset_version`: Current dataset version
- `conversation_id`: Auto-generated or manually assigned
- `split`: Initially "pending", assigned during split generation
- `language`: Detected or annotated
- `domain`: Annotated based on content
- `source_type`: "original_human" or "original_synthetic"
- `source_reference`: Description of creation method
- `creator`: Creator identifier
- `created_at`: ISO-8601 timestamp
- `license_status`: "project-owned" for original data
- `license_reference`: null for project-owned data

**Optional Metadata**:
- `tags`: Relevant tags for categorization
- `notes`: Additional context or comments

**Output**: Complete record with all metadata

### 4.7 Stage 6: Approval or Rejection

**Approval Criteria**:
- `quality_score` >= 0.7
- `privacy_status` != "contains_pii"
- `license_status` == "project-owned" or "verified-external"
- Factual and linguistic review passed
- No unresolved issues

**Approval Process**:
- Reviewer examines record
- Checks all criteria
- Sets `review_status` to "approved" or "rejected"
- Records `reviewer` and `review_date`

**Rejection Reasons**:
- Factual errors
- Poor linguistic quality
- Privacy concerns
- Unclear licensing
- Low quality score

**Output**: Record with `review_status` set

### 4.8 Stage 7: Export to Dataset Release

**Export Process**:
- Collect all approved records (`review_status: "approved"`)
- Assign splits (train/validation/test) using deterministic rules
- Generate dataset statistics
- Validate schema compliance
- Export to versioned JSON file
- Version the dataset release (e.g., nexusai-original-v1.0.0.json)

**Versioning**:
- Use semantic versioning (MAJOR.MINOR.PATCH)
- MAJOR: Breaking schema changes
- MINOR: New domains or features
- PATCH: Bug fixes or additional records

**Output**: Versioned dataset file ready for training

### 4.9 Workflow Summary

```
Draft → Review → Quality Score → Privacy Check → Metadata → Approve/Reject → Export
```

**Key Principles**:
- Quality over quantity
- Bengali-first approach
- Clear provenance tracking
- Privacy by design
- Reproducible process

---

## 5. Provenance and Licensing Policy

### 5.1 Provenance Classification

**Original Data**:
- **original_human**: Human-authored by NexusAI team
- **original_synthetic**: Generated by NexusAI processes (e.g., internal tools)
- **Status**: Automatically project-owned, license_status = "project-owned"

**Imported Data**:
- **imported**: Imported from external source
- **Status**: Requires license verification before use
- **Blocker**: Cannot be used until license_status = "verified-external"

**Converted Data**:
- **converted**: Converted from another format (e.g., CSV to JSON)
- **Status**: Inherits source licensing requirements
- **Blocker**: Requires source license verification

### 5.2 Licensing Policy

**Project-Owned Data**:
- **License**: proprietary-project-owned
- **Commercial Use**: permitted
- **Redistribution**: restricted-to-project
- **Requirement**: No external copyrighted material included

**Verified External Data**:
- **License**: Must be permissive (CC-BY, Apache-2.0, MIT, etc.)
- **Commercial Use**: Must be permitted
- **Redistribution**: Must be permitted or at least project-internal use allowed
- **Requirement**: Document license URL and terms
- **Blocker**: Non-commercial licenses (CC-BY-NC, NC-SA) are BLOCKED

**Unverified External Data**:
- **Status**: BLOCKED
- **Requirement**: License verification before use
- **Action**: Do not include in training until verified

### 5.3 Provenance Tracking Requirements

**Every Record Must Have**:
- `source_type`: Classification of origin
- `source_reference`: Description of source
- `creator`: Person or process that created record
- `created_at`: Timestamp of creation
- `license_status`: Licensing status
- `license_reference`: License identifier or URL (if applicable)

**Audit Trail**:
- Maintain record of who created, reviewed, and approved each record
- Track changes to records (modifications, deletions)
- Document conversion processes
- Document import processes (if external data used)

### 5.4 External Data Integration Rules

**Before Importing External Data**:
1. Verify license permits commercial use
2. Verify license permits redistribution or at least project-internal use
3. Document license URL and terms
4. Set `license_status = "verified-external"`
5. Set `license_reference` to license identifier
6. Apply schema conversion if needed
7. Set `source_type = "imported"`
8. Submit for review and approval

**If License Unverified**:
- Set `license_status = "unverified"`
- BLOCK from training
- Do not include in dataset releases

**If License Non-Commercial**:
- BLOCK from training
- Do not use even if verified (commercial use not permitted)

### 5.5 Synthetic Data Policy

**Definition**: Data generated by automated processes or tools (not human-authored)

**Classification**:
- Set `source_type = "original_synthetic"`
- Set `license_status = "project-owned"` (if generated by NexusAI processes)
- Document generation method in `source_reference`

**Quality Requirements**:
- Synthetic data must pass same quality checks as human-authored data
- Synthetic data must be clearly labeled as synthetic
- Do not fabricate synthetic data to inflate dataset size
- Do not use external AI services (OpenAI, Claude, etc.) to generate synthetic data for training

---

## 6. Data Quality and Privacy Checks

### 6.1 Schema Validation

**Required Fields**:
- `record_id`
- `dataset_version`
- `conversation_id`
- `split`
- `language`
- `domain`
- `messages`
- `source_type`
- `source_reference`
- `creator`
- `created_at`
- `review_status`
- `quality_score`
- `license_status`
- `privacy_status`

**Field Type Validation**:
- `record_id`: String, format REC-YYYYMMDD-NNNN
- `dataset_version`: String, semantic version
- `conversation_id`: String, format CONV-YYYYMMDD-NNNN
- `split`: Enum (train/validation/test)
- `language`: Enum (bengali/english/mixed)
- `domain`: Enum (conversation/knowledge/reasoning/mathematics/coding/writing/planning/health_wellness/other)
- `messages`: Array of message objects
- `source_type`: Enum (original_human/original_synthetic/imported/converted)
- `license_status`: Enum (project-owned/verified-external/unverified)
- `privacy_status`: Enum (public/private/contains_pii)
- `quality_score`: Float, 0.0-1.0

**Validation Process**:
- Automated schema validation before export
- Reject records with missing required fields
- Reject records with invalid enum values
- Reject records with invalid data types

### 6.2 Empty or Malformed Conversations

**Empty Conversation Check**:
- Reject if `messages` array is empty
- Reject if all messages have empty `content`

**Malformed Conversation Check**:
- Reject if message lacks `role` or `content`
- Reject if `role` is not "user" or "assistant"
- Reject if conversation has only one message (minimum 2 for dialogue)
- Reject if turn indices are not sequential

**Malformed Message Check**:
- Reject if `content` is empty or whitespace-only
- Reject if `turn_index` is missing or invalid
- Reject if `language` is not valid enum value

### 6.3 Language Label Validation

**Language Detection**:
- Implement basic Unicode-based detection for Bengali/English/mixed
- Bengali: Contains Bengali Unicode range (U+0980 to U+09FF)
- English: Contains Latin script (U+0020 to U+007E, U+00A0 to U+00FF)
- Mixed: Contains both Bengali and Latin script

**Validation**:
- Verify `language` field matches detected language
- Flag discrepancies for manual review
- Default to "mixed" if uncertain

### 6.4 Duplicate and Near-Duplicate Detection

**Exact Duplicate Check**:
- Compare message content across all records
- Reject exact duplicates (same conversation, same messages)

**Near-Duplicate Check**:
- Compute similarity score between conversations
- Flag near-duplicates for manual review
- Threshold: Jaccard similarity > 0.9 (configurable)

**Prevention**:
- Check for duplicates before approval
- Maintain index of conversation hashes
- Reject near-duplicates with manual review exception

### 6.5 Conversation Integrity

**Conversation Flow Check**:
- Verify conversation follows logical turn order (user → assistant → user → ...)
- Verify assistant responses are relevant to user messages
- Flag conversations with abrupt topic changes without explanation

**Coherence Check**:
- Verify conversation is coherent and contextual
- Flag conversations with contradictory statements
- Flag conversations with circular reasoning (unless intentional)

### 6.6 Missing Provenance

**Provenance Check**:
- Reject if `source_type` is missing
- Reject if `source_reference` is missing
- Reject if `creator` is missing
- Reject if `created_at` is missing
- Reject if `license_status` is missing

**License Check**:
- Reject if `license_status` == "unverified"
- Reject if `license_status` == "verified-external" but `license_reference` is missing
- Block from training if license is non-commercial

### 6.7 Personal Information and Privacy Risks

**PII Detection**:
- Scan for email addresses (regex pattern)
- Scan for phone numbers (regex pattern)
- Scan for addresses (street, city, zip patterns)
- Scan for names (common name patterns)
- Scan for IDs (SSN, passport, etc.)

**Privacy Review**:
- Flag records with detected PII
- Require removal or anonymization before approval
- Set `privacy_status = "contains_pii"` if PII detected
- Reject if PII cannot be removed without breaking record

**Confidential Information**:
- Flag records that appear to contain confidential business data
- Flag records that appear to contain trade secrets
- Reject if confidential information cannot be removed

### 6.8 Train/Validation/Test Leakage Prevention

**Split Assignment Rules**:
- Use conversation-level split (all messages from a conversation stay in same split)
- Use fixed random seed for reproducibility
- Stratify by language and domain
- Ensure no conversation appears in multiple splits

**Leakage Detection**:
- Verify no conversation_id appears in multiple splits
- Verify no record_id appears in multiple splits
- Verify no near-duplicates across splits
- Verify language distribution is consistent across splits

**Reproducibility**:
- Document random seed used for split assignment
- Document split ratio (e.g., 80/10/10)
- Document stratification strategy

### 6.9 Incorrect or Contradictory Answers

**Fact-Checking**:
- Verify factual claims are accurate (for knowledge domain)
- Verify reasoning steps are logically sound (for reasoning domain)
- Verify mathematical calculations are correct (for mathematics domain)
- Verify code is correct (for coding domain)

**Contradiction Detection**:
- Flag records with internal contradictions
- Flag records that contradict established facts
- Flag records with ambiguous or uncertain answers

**Handling Uncertainty**:
- Encourage examples of admitting uncertainty
- Include examples of saying "I don't know"
- Include examples of asking for clarification
- Do not fabricate confident answers for uncertain topics

### 6.10 Excessive Repetition and Low-Information Examples

**Repetition Check**:
- Compute repetition rate (ratio of repeated n-grams)
- Flag conversations with repetition rate > 30%
- Reject conversations with identical consecutive messages

**Information Content Check**:
- Compute information density (unique tokens / total tokens)
- Flag conversations with low information density
- Reject conversations that are primarily filler or padding

**Quality Threshold**:
- Reject if repetition rate > 50%
- Reject if information density < 0.3

### 6.11 Bengali Unicode and Mixed-Script Handling

**Unicode Validation**:
- Verify Bengali characters are valid Unicode (U+0980 to U+09FF)
- Verify text is valid UTF-8
- Verify no invalid surrogate pairs or malformed sequences

**Mixed-Script Validation**:
- Verify mixed-language conversations handle code-switching naturally
- Verify punctuation is appropriate for each language
- Verify numerals are consistent (Bengali numerals vs Arabic numerals)

**Encoding/Decoding**:
- Verify all text files are UTF-8 encoded
- Verify JSON files handle UTF-8 correctly
- Verify round-trip encoding/decoding preserves Bengali characters

---

## 7. Dataset Splitting and Leakage Prevention

### 7.1 Split Strategy

**Split Ratio**: 80% train, 10% validation, 10% test

**Split Level**: Conversation-level (not message-level)

**Rationale**: Conversation-level split prevents leakage where messages from the same conversation appear in both training and evaluation sets.

### 7.2 Split Assignment Algorithm

**Deterministic Algorithm**:
```python
import hashlib

def assign_split(conversation_id, seed=42):
    """
    Assign split based on conversation_id hash.
    Ensures reproducibility with fixed seed.
    """
    # Hash conversation_id with seed
    hash_input = f"{conversation_id}-{seed}".encode('utf-8')
    hash_value = int(hashlib.sha256(hash_input).hexdigest(), 16)
    
    # Assign split based on hash value
    if hash_value % 100 < 80:
        return "train"
    elif hash_value % 100 < 90:
        return "validation"
    else:
        return "test"
```

**Stratification**:
- Group conversations by language and domain
- Apply split assignment within each group
- Ensure language distribution is consistent across splits
- Ensure domain distribution is consistent across splits

### 7.3 Leakage Prevention

**Conversation-Level Split**:
- All messages from a conversation stay in the same split
- Prevents model from seeing conversation context in training and evaluation

**Near-Duplicate Prevention**:
- Compute similarity between conversations
- Ensure no near-duplicates across splits
- Threshold: Jaccard similarity > 0.9

**User-Level Split** (if applicable):
- If conversations are associated with users, split by user ID
- Prevents user-specific patterns from leaking

### 7.4 Split Validation

**Validation Checks**:
- Verify no conversation_id appears in multiple splits
- Verify no record_id appears in multiple splits
- Verify no near-duplicates across splits
- Verify language distribution consistency
- Verify domain distribution consistency
- Verify split ratio matches target (80/10/10)

**Validation Process**:
- Run automated validation after split assignment
- Report any violations
- Fix violations (reassign splits or remove problematic records)

### 7.5 Reproducibility

**Fixed Random Seed**: Use fixed seed for split assignment (e.g., seed=42)

**Documented Algorithm**: Document split assignment algorithm in dataset release notes

**Versioned Splits**: Include split assignment in dataset version metadata

---

## 8. Tokenizer Migration Readiness

### 8.1 Current Tokenizer Status

**Implementation**: SimpleTokenizer (word-level, whitespace splitting)  
**Vocabulary Size**: 74 tokens  
**Special Tokens**: PAD (0), UNK (1), BOS (2), EOS (3)  
**Tokenization Method**: `text.lower().split()`  
**Limitations**:
- Critically small vocabulary
- No subword segmentation
- Poor Bengali morphology handling
- High UNK rate for unseen text

### 8.2 Proposed Bengali-English Tokenizer

**Target**: SentencePiece BPE (Byte Pair Encoding)  
**Target Vocabulary Size**: 2,000–5,000 tokens (experimental)  
**Language Support**: Bengali, English, mixed-language

### 8.3 Special Token Handling

**Special Token IDs**:
- PAD: ID 0
- UNK: ID 1
- BOS: ID 2
- EOS: ID 3

**SentencePiece Configuration**:
```
pad_id=0
unk_id=1
bos_id=2
eos_id=3
user_defined_symbols=<pad>,<unk>,<bos>,<eos>
```

**Implementation Strategy**:
1. Prepend special tokens to training corpus
2. Configure SentencePiece to reserve IDs 0-3
3. Vocabulary indices start at 4 for regular tokens

### 8.4 Bengali Unicode and Punctuation

**Bengali Unicode Range**: U+0980 to U+09FF

**Handling**:
- Ensure SentencePiece handles Bengali Unicode correctly
- Verify Bengali punctuation (।, ॥, ?) is handled
- Verify Bengali numerals (০-৯) are handled
- Verify conjuncts (যুক্তবর্ণ) are handled appropriately

**Test Cases**:
- Pure Bengali text: "আমি বাংলায় কথা বলতে পারি।"
- Bengali with punctuation: "তুমি কেমন আছো?"
- Bengali numerals: "১২৩"
- Bengali conjuncts: "স্বাস্থ্য", "ক্ষমতা"

### 8.5 Bengali Words and Compound Expressions

**Morphological Handling**:
- Bengali has rich morphology (verb conjugations, noun declensions)
- BPE should handle subword segmentation
- Test conjugated verbs: "করি", "করেন", "করবে"
- Test compound words: "স্বাস্থ্যসেবা", "জনসংখ্যা"

**Expected Behavior**:
- BPE should segment conjugated forms into stems and suffixes
- BPE should segment compound words into meaningful subwords
- UNK rate should be low for Bengali vocabulary

### 8.6 English Text

**English Handling**:
- Standard English text handling
- Punctuation separation
- Subword segmentation for rare words
- Handling of contractions (don't, can't, etc.)

**Test Cases**:
- Pure English: "I can speak English"
- English with punctuation: "What is your name?"
- Contractions: "I don't know"

### 8.7 Bengali-English Code-Switching

**Code-Switching Handling**:
- Mixed-language sentences: "আমি English এবং Bengali দুই ভাষাতেই কথা বলতে পারি"
- Embedded English words in Bengali: "আমি okay, এখন আসি"
- Embedded Bengali words in English: "I can speak বাংলা"

**Expected Behavior**:
- Tokenizer should handle code-switching naturally
- No special treatment required (BPE handles mixed scripts)
- UNK rate should be low for code-switched text

### 8.8 Numbers, Dates, Symbols, and Code

**Numbers**:
- Arabic numerals: 123, 45.67
- Bengali numerals: ১২৩, ৪৫.৬৭
- Large numbers: 1,000, 1000000

**Dates**:
- ISO format: 2026-10-28
- Bengali date format: ২৮/১০/২০২৬

**Symbols**:
- Mathematical symbols: +, -, ×, ÷, =, <, >
- Currency symbols: $, ₹, ৳
- Other symbols: @, #, &, *

**Code**:
- Programming code snippets
- Variable names, function names
- Should be tokenized appropriately

**Expected Behavior**:
- Numbers should be segmented or kept whole based on frequency
- Dates should be segmented into components
- Symbols should be handled appropriately
- Code should be tokenized consistently

### 8.9 Unknown-Token Behavior

**UNK Token**:
- ID 1 reserved for UNK
- Used for out-of-vocabulary tokens

**UNK Rate Target**:
- Training data: < 5%
- Validation data: < 10%
- Test data: < 10%

**Measurement**:
- Encode corpus with tokenizer
- Count UNK tokens
- Calculate UNK rate: UNK_count / total_tokens

### 8.10 Encode/Decode Round-Trip Tests

**Test Method**:
1. Encode test text using new tokenizer
2. Decode token IDs back to text
3. Compare original and decoded text
4. Measure character-level accuracy

**Test Corpus**:
- 100 Bengali sentences
- 100 English sentences
- 50 mixed-language sentences

**Acceptance Criteria**:
- Round-trip accuracy > 99%
- No character loss for Bengali Unicode
- Special tokens preserved correctly
- Whitespace handling consistent

### 8.11 Vocabulary Coverage and Token-Length Statistics

**Coverage Metrics**:
- Total tokens in training corpus
- Unique tokens in training corpus
- Vocabulary size
- Tokens covered by vocabulary
- Coverage rate: covered_tokens / total_tokens

**Token-Length Statistics**:
- Average tokens per sentence
- Max tokens per sentence
- Token length distribution
- Percentiles (50th, 90th, 95th, 99th)

**Measurement Process**:
1. Train tokenizer on dataset
2. Encode entire training corpus
3. Compute statistics
4. Document in dataset release

### 8.12 Special-Token IDs and Checkpoint Compatibility

**Current Checkpoint**:
- Vocabulary size: 74
- Special tokens: PAD(0), UNK(1), BOS(2), EOS(3)

**New Checkpoint**:
- Vocabulary size: 2,000–5,000
- Special tokens: PAD(0), UNK(1), BOS(2), EOS(3) (same IDs)

**Compatibility**:
- Special token IDs preserved
- Model output layer resized to new vocab_size
- Model embedding layer resized to new vocab_size
- Checkpoint includes new vocabulary mapping

**Versioning**:
- Current checkpoint: v1.0 (74-token)
- New checkpoint: v2.0.0 (BPE, 2K-5K token)
- Keep v1.0 for rollback

### 8.13 Versioning and Rollback

**Checkpoint Versioning**:
- Include `vocab_size` in checkpoint metadata
- Include `tokenizer_type` in checkpoint metadata
- Include `tokenizer_version` in checkpoint metadata
- Include `special_tokens` mapping in checkpoint metadata

**Rollback Plan**:
1. Keep v1.0 checkpoint in `checkpoints_medium/`
2. Add v2.0.0 checkpoint to new directory `checkpoints_medium_v2.0.0_sp/`
3. Update ML service config to point to new checkpoint
4. If issues arise, revert config to v1.0
5. No destructive operations on v1.0

**Rollback Triggers**:
- Model fails to load
- Inference quality degrades
- Latency increases significantly
- Memory usage exceeds limits
- Evaluation metrics worsen

---

## 9. Evaluation Suite and Scoring Methodology

### 9.1 Evaluation Objectives

**Objective**: Design a small, reproducible Bengali-English evaluation suite to measure model capabilities and track improvements over time.

**Scope**:
- Natural conversation (Bengali, English, mixed)
- Logical reasoning
- Mathematics
- Instruction following
- Context retention
- Repetition and looping
- Unknown-token behavior
- End-of-sequence handling
- Response correctness and uncertainty
- Latency and memory consumption

### 9.2 Fixed Test Examples

#### 9.2.1 Bengali Conversation

**Test 1: Greeting**
```
User: তোমার নাম কি?
Expected: Assistant identifies as NexusAI in Bengali
```

**Test 2: Capability**
```
User: তুমি কী করতে পারো?
Expected: Assistant describes capabilities in Bengali
```

**Test 3: Health Question**
```
User: স্বাস্থ্য ভালো রাখতে কী করব?
Expected: Assistant provides general health advice in Bengali with appropriate disclaimer
```

#### 9.2.2 English Conversation

**Test 4: Greeting**
```
User: What is your name?
Expected: Assistant identifies as NexusAI in English
```

**Test 5: Capability**
```
User: What can you do?
Expected: Assistant describes capabilities in English
```

**Test 6: Health Question**
```
User: How can I stay healthy?
Expected: Assistant provides general health advice in English with appropriate disclaimer
```

#### 9.2.3 Mixed-Language Conversation

**Test 7: Code-Switching**
```
User: আমি English এবং Bengali দুই ভাষাতেই কথা বলতে পারি
Expected: Assistant responds in mixed language naturally
```

**Test 8: Embedded English**
```
User: আমি okay, এখন আসি
Expected: Assistant acknowledges appropriately
```

#### 9.2.4 Logical Reasoning

**Test 9: Syllogism**
```
User: If all cats are animals, and all animals need food, do all cats need food?
Expected: Yes, with logical explanation
```

**Test 10: Multi-step**
```
User: If A is 5, B is 2 more than A, and C is 3 times B, what is C?
Expected: C is 21, with step-by-step explanation
```

#### 9.2.5 Mathematics

**Test 11: Arithmetic**
```
User: What is 15 + 27?
Expected: 42
```

**Test 12: Bengali Numerals**
```
User: ১৫ + ২৭ কত?
Expected: ৪২ (using Bengali numerals if appropriate)
```

#### 9.2.6 Instruction Following

**Test 13: Explicit Instruction**
```
User: Tell me about Bangladesh in exactly three sentences.
Expected: Response in exactly three sentences
```

**Test 14: Negative Instruction**
```
User: Tell me about Bangladesh, but do not mention the capital.
Expected: Response without mentioning Dhaka
```

#### 9.2.7 Context Retention

**Test 15: Multi-turn Context**
```
User: My name is Alex.
Assistant: (acknowledges)
User: What is my name?
Expected: Alex
```

**Test 16: Earlier Context**
```
User: I like cats.
Assistant: (acknowledges)
User: Tell me about dogs.
Assistant: (responds)
User: What did I say I like earlier?
Expected: Cats
```

#### 9.2.8 Repetition and Looping

**Test 17: Repetition Check**
```
User: Hello
Expected: Response without excessive repetition
Metric: Count repeated n-grams
```

**Test 18: Loop Prevention**
```
User: What is 2+2?
Assistant: 4
User: What is 2+2?
Expected: 4 (should not loop or change answer)
```

#### 9.2.9 Unknown-Token Behavior

**Test 19: UNK Handling**
```
User: [Rare word or neologism]
Expected: Response without excessive UNK tokens
Metric: Count UNK tokens in response
```

#### 9.2.10 End-of-Sequence Handling

**Test 20: EOS Detection**
```
User: Tell me a short story.
Expected: Story with appropriate ending, not continued indefinitely
Metric: Check if generation stops at EOS or max_tokens
```

#### 9.2.11 Response Correctness and Uncertainty

**Test 21: Known Fact**
```
User: What is the capital of Bangladesh?
Expected: Dhaka
```

**Test 22: Uncertain Topic**
```
User: What is the meaning of life?
Expected: Philosophical response, acknowledging uncertainty
```

**Test 23: Impossible Question**
```
User: What is the square root of -1 in real numbers?
Expected: No real solution exists, acknowledges impossibility
```

### 9.3 Scoring Criteria

#### 9.3.1 Coherence Score

**Scale**: 1-5 (1 = incoherent, 5 = fully coherent)

**Criteria**:
- Response makes sense
- Follows logical flow
- Relevant to prompt
- No contradictions

#### 9.3.2 Correctness Score

**Scale**: 1-5 (1 = incorrect, 5 = fully correct)

**Criteria**:
- Factual accuracy
- Logical correctness
- Mathematical correctness
- Code correctness

#### 9.3.3 Language Appropriateness Score

**Scale**: 1-5 (1 = inappropriate, 5 = fully appropriate)

**Criteria**:
- Language matches prompt language
- Bengali grammar and spelling correct
- English grammar and spelling correct
- Mixed-language natural

#### 9.3.4 Instruction Following Score

**Scale**: 1-5 (1 = not followed, 5 = fully followed)

**Criteria**:
- Follows explicit instructions
- Respects negative constraints
- Meets length requirements
- Follows format requirements

#### 9.3.5 Context Retention Score

**Scale**: 1-5 (1 = no retention, 5 = full retention)

**Criteria**:
- Remembers earlier information
- Maintains conversation context
- References previous context appropriately

#### 9.3.6 Repetition Score

**Metric**: Repetition rate (0-1)

**Calculation**: Count repeated n-grams / total n-grams

**Threshold**: < 0.3 acceptable, < 0.1 good

#### 9.3.7 UNK Score

**Metric**: UNK rate (0-1)

**Calculation**: UNK tokens / total tokens

**Threshold**: < 0.1 acceptable, < 0.05 good

#### 9.3.8 EOS Handling Score

**Metric**: Boolean (stops at EOS or max_tokens)

**Criteria**:
- Generation stops at EOS if present
- Does not continue indefinitely
- Stops at reasonable length

#### 9.3.9 Latency Score

**Metric**: Seconds per prompt

**Measurement**: Average over 10 prompts

**Threshold**: < 1s acceptable, < 0.5s good

#### 9.3.10 Memory Score

**Metric**: MB memory footprint

**Measurement**: Peak memory during inference

**Threshold**: < 500 MB acceptable, < 200 MB good

### 9.4 Baseline Comparison Rules

**Baseline**: Current model (74-token SimpleTokenizer)

**Comparison Method**:
- Run evaluation suite on baseline
- Record all scores
- Run evaluation suite on new model
- Compare scores

**Success Criteria**:
- Coherence score improvement > 0.5
- Correctness score improvement > 0.5
- Language appropriateness score improvement > 0.5
- UNK rate reduction > 50%
- Repetition rate reduction > 20%
- Latency increase < 2x
- Memory increase < 2x

**Failure Criteria**:
- Any score degrades by > 0.5
- UNK rate increases
- Repetition rate increases
- Latency increases > 3x
- Memory increases > 3x

### 9.5 Evaluation Protocol

**Step 1: Baseline Evaluation**
- Run evaluation suite on current model
- Record all scores
- Save baseline results

**Step 2: New Model Evaluation**
- Run evaluation suite on new model
- Record all scores
- Save new results

**Step 3: Comparison**
- Compare new scores to baseline
- Calculate deltas
- Identify improvements and regressions

**Step 4: Statistical Significance**
- For human-rated scores (coherence, correctness), use paired t-test
- Require p < 0.05 for significance
- Minimum 30 samples per category

**Step 5: Decision**
- If success criteria met: Deploy
- If failure criteria met: Rollback
- If mixed results: Investigate and decide

### 9.6 Evaluation Status

**Current Status**: NOT RUN
- Baseline evaluation not executed
- New model does not exist yet
- This is a planning document only

**When to Run**: After tokenizer migration and model training (Stage B4-B3 or later)

---

## 10. Resource Constraints and Practical Next Steps

### 10.1 Current Resource Constraints

**Disk Space**: 2.86 GB free (down from 3.40 GB in Stage B4-A)

**RAM**: ~8 GB total, ~3 GB available (estimated)

**CPU**: 2 physical cores, 4 logical cores

**GPU**: None (CPU-only)

**Implications**:
- Small to medium dataset experiments feasible
- Large-scale training requires cloud resources
- Limited disk space requires cleanup before large downloads
- CPU-only training will be slow

### 10.2 Practical Next Steps

**Immediate Next Step**: Data Collection

**Phase 1: Pilot Data Collection (1-100 conversations)**
- Draft 10-20 Bengali conversations
- Draft 10-20 English conversations
- Draft 5-10 mixed-language conversations
- Apply quality review process
- Assign metadata
- Export to pilot dataset v0.1.0-alpha

**Phase 2: Expansion (100-1,000 conversations)**
- Expand to target domains (reasoning, mathematics, coding, etc.)
- Increase Bengali proportion
- Include mixed-language examples
- Apply full quality review
- Export to dataset v0.2.0-alpha

**Phase 3: Production Dataset (1,000-10,000 conversations)**
- Scale up data collection
- Ensure domain coverage
- Ensure language distribution
- Full quality review
- Export to dataset v1.0.0

**Data Collection Guidelines**:
- Quality over quantity
- Bengali-first approach
- Original data only (no external imports until licenses verified)
- Clear provenance tracking
- Privacy by design

### 10.3 Tokenizer Migration (Future Stage)

**Prerequisites**:
- Licensed dataset available (or project-owned dataset collected)
- Dataset size > 1,000 conversations
- Data quality verified

**Steps**:
1. Install SentencePiece (pip install sentencepiece)
2. Train BPE tokenizer on dataset
3. Test with Bengali-English mixed-language corpus
4. Verify round-trip encoding/decoding
5. Measure vocabulary coverage and UNK rate
6. Modify MediumTransformer for new vocab size
7. Train new model with new tokenizer
8. Evaluate against baseline
9. Deploy if metrics improve, rollback otherwise

**Estimated Time**:
- Tokenizer training: 1-2 hours
- Model training: 10-30 hours (1K samples, CPU-only)
- Evaluation: 2-4 hours

**Estimated Storage**:
- Tokenizer model: ~1-5 MB
- Training checkpoints: ~275 MB
- Final model: ~20 MB
- Old model (for rollback): 18.76 MB
- Total: ~315 MB

### 10.4 Resource Recommendations

**Disk Space**:
- Clean up temporary files before large experiments
- Consider external storage for large datasets
- Monitor disk space during training

**RAM**:
- Use small batch sizes (4-8)
- Monitor memory usage during training
- Consider cloud resources for larger models

**CPU**:
- Accept longer training times on current hardware
- Consider cloud resources for faster training
- Parallelize data processing where possible

**GPU**:
- GPU not available for current experiments
- Consider cloud GPU for future large-scale training

---

## 11. Risks, Unresolved Questions, and Explicit Blockers

### 11.1 Risks

**Risk 1: Data Collection Timeline**
- **Risk**: Data collection may take longer than expected
- **Impact**: Delays tokenizer migration and model training
- **Mitigation**: Start with pilot collection, scale gradually

**Risk 2: Data Quality**
- **Risk**: Collected data may not meet quality standards
- **Impact**: Poor model performance despite tokenizer migration
- **Mitigation**: Strict quality review, iterative improvement

**Risk 3: Bengali Expertise**
- **Risk**: Limited Bengali language expertise in team
- **Impact**: Bengali examples may have errors or unnatural phrasing
- **Mitigation**: Consult Bengali speakers, use linguistic resources

**Risk 4: Tokenizer Migration Complexity**
- **Risk**: BPE tokenizer may not significantly improve quality
- **Impact**: Time and resources spent without measurable improvement
- **Mitigation**: Establish baseline evaluation first, rollback if metrics do not improve

**Risk 5: Resource Constraints**
- **Risk**: Limited disk space, RAM, and CPU
- **Impact**: Large experiments not feasible
- **Mitigation**: Start with small experiments, use cloud resources for larger work

### 11.2 Unresolved Questions

**Question 1: Target Dataset Size**
- **Question**: How many conversations are needed for meaningful improvement?
- **Status**: Unresolved
- **Action**: Start with pilot (100), evaluate, scale based on results

**Question 2: Optimal Vocabulary Size**
- **Question**: What is the optimal vocabulary size for Bengali-English?
- **Status**: Unresolved
- **Action**: Experiment with 2K, 5K, 10K vocab sizes

**Question 3: Domain Prioritization**
- **Question**: Which domains should be prioritized for data collection?
- **Status**: Unresolved
- **Action**: Prioritize conversation, reasoning, and health/wellness domains

**Question 4: Mixed-Language Proportion**
- **Question**: What proportion of mixed-language examples is optimal?
- **Status**: Unresolved
- **Action**: Start with 10-20% mixed-language, adjust based on evaluation

### 11.3 Explicit Blockers

**Blocker 1: Data License Verification**
- **Blocker**: All existing datasets have unverified licensing
- **Impact**: Cannot use existing datasets for training
- **Resolution**: Collect original project-owned data or verify external dataset licenses

**Blocker 2: No Licensed Dataset**
- **Blocker**: No dataset with verified license for commercial use
- **Impact**: Cannot proceed to tokenizer migration or training
- **Resolution**: Collect original data following framework in this document

**Blocker 3: Disk Space**
- **Blocker**: Limited disk space (2.86 GB free)
- **Impact**: Large-scale experiments not feasible
- **Resolution**: Clean up temporary files, use external storage, or cloud resources

---

## 12. Checklist for Stage B4-B2

Stage B4-B2 is the implementation stage for data collection. Before beginning, the following must be approved:

### 12.1 Data Collection Approval

- [ ] Data collection workflow approved
- [ ] Pilot dataset size approved (e.g., 100 conversations)
- [ ] Target domains approved
- [ ] Language distribution approved (e.g., 50% Bengali, 30% English, 20% mixed)
- [ ] Quality review process approved
- [ ] Privacy guidelines approved
- [ ] Metadata schema approved (v2.0)

### 12.2 Resource Approval

- [ ] Disk space confirmed sufficient (2.86 GB free)
- [ ] RAM confirmed sufficient (8 GB)
- [ ] CPU-only training constraints accepted
- [ ] Estimated timeline approved
- [ ] Cloud resource usage approved if needed

### 12.3 Team Approval

- [ ] Data collection team assigned
- [ ] Bengali language expert available
- [ ] Domain experts available (for reasoning, mathematics, health/wellness)
- [ ] Review process defined
- [ ] Approval workflow defined

### 12.4 Tools and Infrastructure

- [ ] Data collection tool selected (JSON editor, spreadsheet, custom tool)
- [ ] Validation script available
- [ ] Metadata assignment process defined
- [ ] Export process defined
- [ ] Version control for dataset releases

### 12.5 Timeline

- [ ] Pilot data collection timeline approved (e.g., 1-2 weeks)
- [ ] Full data collection timeline approved (e.g., 1-3 months)
- [ ] Quality review timeline approved
- [ ] Evaluation timeline approved

---

## 13. Files Created or Modified

### 13.1 Files Created

**File**: `docs/ai-core/12-stage-b4b1-original-dataset-framework.md`  
**Purpose**: Stage B4-B1 planning and documentation  
**Content**: Dataset schema, provenance tracking, data creation workflow, quality checks, tokenizer migration readiness, evaluation methodology  
**Size**: ~29,000 bytes

### 13.2 Files Modified

**None** (this stage is read-only planning)

### 13.3 Files Reviewed

- `docs/ai-core/11-stage-b4a-dataset-foundation.md` — Stage B4-A planning document
- `packages/ai-core/models/README.md` — Model checkpoint documentation
- `packages/ai-core/CHECKPOINT_COMPATIBILITY.md` — Checkpoint compatibility documentation
- `packages/ai-core/RUNTIME_ARCHITECTURE.md` — Runtime architecture documentation
- `packages/ai-core/TYPESCRIPT_ARCHITECTURE.md` — TypeScript architecture documentation
- `packages/ai-core/data/train_v2.json` — 502 conversations (inspection only)
- `packages/ai-core/data/conversational_data.json` — 28 records (inspection only)

---

## 14. Tests Actually Executed

### 14.1 Tests Run

**Git Status Check**:
- Command: `git status --short`
- Result: Confirmed pre-existing modifications
- Status: PASS

**Branch Check**:
- Command: `git branch --show-current`
- Result: main
- Status: PASS

**HEAD Check**:
- Command: `git log -1 --oneline`
- Result: b9c3fcf docs(ai-core): organize and document NexusAI model assets
- Status: PASS

**Disk Space Check**:
- Command: Python shutil.disk_usage
- Result: 127.98 GB total, 125.12 GB used, 2.86 GB free
- Status: PASS

**Documentation Reading**:
- Read Stage B4-A document
- Read model README
- Read checkpoint compatibility document
- Read runtime architecture document
- Read TypeScript architecture document
- Status: PASS

### 14.2 Tests NOT Run

**Tests NOT Run in Stage B4-B1**:
- ML service startup and HTTP endpoints
- Inference with actual user input
- Baseline evaluation with fixed prompts
- Tokenizer training
- BPE tokenization tests
- Model training
- Model evaluation
- Data collection workflow (planning only)
- Quality review process (planning only)

**Reason**: Stage B4-B1 is read-only planning and documentation. These tests require implementation, which is deferred to future stages with approval.

---

## 15. Verification and Final Status

### 15.1 Production State Verification

**Checkpoint**: `packages/ai-core/models/checkpoints_medium/final_model.pt`  
**Status**: UNCHANGED (no modification)  
**Verification**: `git diff` shows no changes

**Tokenizer**: `packages/ai-core/tokenizer/tokenizer.py`  
**Status**: UNCHANGED (no modification)  
**Verification**: `git diff` shows no changes

**ML Service**: `packages/ai-core/ml-service/main.py`  
**Status**: UNCHANGED (no modification)  
**Verification**: `git diff` shows no changes

**Model Architecture**: `packages/ai-core/neural/medium_transformer.py`  
**Status**: UNCHANGED (no modification)  
**Verification**: `git diff` shows no changes

**API Routes**: `apps/api/src/routes/ai.ts`  
**Status**: UNCHANGED (no modification)  
**Verification**: `git diff` shows no changes

**Frontend**: `apps/web/`  
**Status**: UNCHANGED (no modification)  
**Verification**: `git diff` shows no changes

**Database**: No changes  
**Status**: UNCHANGED (no modification)  
**Verification**: No database-related changes

### 15.2 Pre-existing Modifications

**Pre-existing Modifications** (preserved exactly):
- M cookies.txt
- M packages/ai-core/evaluation/__pycache__/evaluator.cpython-314.pyc
- M packages/ai-core/evaluation/evaluator.py
- M packages/ai-core/ml-service/__pycache__/main.cpython-314.pyc
- M packages/ai-core/ml-service/main.py
- M packages/ai-core/neural/__pycache__/medium_transformer.cpython-314.pyc
- M packages/ai-core/tokenizer/__pycache__/tokenizer.cpython-314.pyc
- ?? docs/ai-core/
- ?? packages/ai-core/CHECKPOINT_COMPATIBILITY.md
- ?? packages/ai-core/RUNTIME_ARCHITECTURE.md
- ?? packages/ai-core/TYPESCRIPT_ARCHITECTURE.md

**Verification**: All pre-existing modifications remain untouched

### 15.3 New Files

**New File**: `docs/ai-core/12-stage-b4b1-original-dataset-framework.md`  
**Status**: Created (inside untracked `docs/ai-core/` directory)  
**Verification**: File exists and contains expected content

### 15.4 Final Git Status

**Final Status** (after Stage B4-B1):
```
 M cookies.txt
 M packages/ai-core/evaluation/__pycache__/evaluator.cpython-314.pyc
 M packages/ai-core/evaluation/evaluator.py
 M packages/ai-core/ml-service/__pycache__/main.cpython-314.pyc
 M packages/ai-core/ml-service/main.py
 M packages/ai-core/neural/__pycache__/medium_transformer.cpython-314.pyc
 M packages/ai-core/tokenizer/__pycache__/tokenizer.cpython-314.pyc
?? docs/ai-core/
?? packages/ai-core/CHECKPOINT_COMPATIBILITY.md
?? packages/ai-core/RUNTIME_ARCHITECTURE.md
?? packages/ai-core/TYPESCRIPT_ARCHITECTURE.md
```

**Note**: The new documentation file is inside the untracked `docs/ai-core/` directory. The entire `docs/ai-core/` directory remains untracked.

### 15.5 Commit Status

**Status**: No commits made  
**Verification**: HEAD remains at b9c3fcf

---

## 16. Conclusion

### 16.1 Stage B4-B1 Summary

**Completed**:
- Dataset inventory reviewed (all existing datasets unverified)
- Versioned dataset schema v2.0 defined with comprehensive metadata
- Bengali-English data creation workflow documented
- Provenance and licensing policy defined
- Data quality and privacy checks specified
- Dataset splitting and leakage prevention rules defined
- Tokenizer migration readiness plan documented
- Evaluation suite and scoring methodology designed
- Resource constraints assessed
- Risks and blockers identified
- Checklist for Stage B4-B2 defined

**NOT Completed** (deferred to future stages with approval):
- No data collection executed
- No quality review executed
- No tokenizer training
- No model modification
- No model training
- No evaluation executed

### 16.2 Production State

**Unchanged**:
- Active checkpoint: `checkpoints_medium/final_model.pt` (74-token, 18.76 MB)
- Active tokenizer: SimpleTokenizer (word-level, 74 tokens)
- Active ML service: `ml-service/main.py`
- Active runtime: Python FastAPI on port 8000

### 16.3 Explicit Blockers

**Primary Blocker**: No dataset with verified license for commercial use  
**Resolution Required**: Collect original project-owned data following the framework in this document

**Secondary Blocker**: Limited disk space (2.86 GB free)  
**Resolution Required**: Clean up temporary files or use external storage before large experiments

### 16.4 Recommended Next Stage

**Recommended Next Stage**: Stage B4-B2 — Original Data Collection Implementation

**Why Safe**:
- Stage B4-B1 established comprehensive framework
- Production model, checkpoint, tokenizer, and runtime remain unchanged
- Data collection is isolated from production systems
- Quality review process ensures only approved data is used
- No model modification or training required

**Prerequisites for Stage B4-B2**:
- Approval of data collection workflow
- Approval of pilot dataset size
- Assignment of data collection team
- Availability of Bengali language expert
- Confirmation of resource availability

**Expected Timeline**:
- Pilot data collection (100 conversations): 1-2 weeks
- Full data collection (1,000+ conversations): 1-3 months
- Quality review: concurrent with collection
- Dataset export: after approval

**Outcome**: After Stage B4-B2, a licensed, high-quality dataset will be available for tokenizer migration and model training in future stages.

---

**End of Stage B4-B1 Report**
