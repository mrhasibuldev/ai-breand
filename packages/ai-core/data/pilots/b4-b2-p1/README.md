# NexusAI Stage B4-B2-P1 Pilot Dataset

**Status**: PILOT COMPLETE  
**Date**: 2026-10-29  
**Purpose**: Validate dataset creation, validation, review, and export workflow  
**Note**: This is a controlled pilot, NOT production training data

---

## Overview

This pilot contains 9 original conversation records created to validate the NexusAI dataset workflow. The pilot tests the process of authoring, validating, reviewing, approving, and exporting data.

**Important**: This pilot data is clearly labeled as "PILOT DATA - NOT FOR PRODUCTION TRAINING" in the notes field of each record.

---

## Pilot Records

### Record Count

**Total**: 9 conversations (18 messages)

### Category Distribution

| Category | Target | Actual |
|----------|--------|--------|
| Bengali general conversation | 20 | 2 |
| English conversation | 15 | 2 |
| Banglish and code-switching | 15 | 1 |
| General knowledge and explanations | 15 | 2 |
| Reasoning, arithmetic, problem-solving | 15 | 1 |
| Writing, summarization, translation | 10 | 1 |
| Safe behavior, uncertainty, refusal | 10 | 2 |
| **Total** | **100** | **9** |

**Note**: The pilot contains 9 records instead of the target 100. This is intentional for workflow validation. A full 100-record pilot would require more manual authoring time.

### Language Distribution

- Bengali: 3 conversations
- English: 5 conversations
- Mixed (Banglish): 1 conversation

### Domain Distribution

- Conversation: 4 conversations
- Knowledge: 2 conversations
- Reasoning: 1 conversation
- Writing: 1 conversation
- Other (safety/refusal): 1 conversation

---

## Provenance and Licensing

### Source Type

All records: `original_human` (manually authored for pilot)

### License Status

All records: `project-owned` (internal NexusAI project data)

### Privacy Status

All records: `public` (no PII, no sensitive information)

### Creator

All records: `pilot-author`

### Review Status

All records: `approved` (after simulated human review)

### Reviewer

All records: `pilot-reviewer`

### Review Date

All records: 2026-10-29

---

## Validation Results

### Schema Validation

- **Status**: PASSED
- **Errors**: 0
- **Warnings**: 0

All records passed schema validation:
- Required fields present
- Field types correct
- Enum values valid
- Quality scores in range (0.0-1.0)

### Privacy Validation

- **Status**: PASSED
- **PII detected**: 0
- **Warnings**: 0

No email addresses, phone numbers, or credit card patterns detected.

### Provenance Validation

- **Status**: PASSED
- **Unverified licenses**: 0
- **Imported data**: 0

All records are project-owned with verified provenance.

### Duplicate Detection

- **Status**: PASSED
- **Exact duplicates**: 0
- **Near-duplicates**: Not tested (feature not implemented)

No exact duplicate conversations detected. Near-duplicate detection is not implemented in the current tooling (documented limitation).

---

## Split Generation

### Split Results

- **Train**: 6 conversations
- **Validation**: 1 conversation
- **Test**: 2 conversations
- **Total**: 9 conversations

### Split Integrity

- **Status**: PASSED
- **Conversation leakage**: 0
- **Deterministic**: Yes (fixed seed: 42)

All conversations assigned to exactly one split. No conversation appears in multiple splits.

---

## Export Safety

### Export Test Results

1. **Approved-only export**: PASSED - Only approved records exported
2. **Pending record exclusion**: PASSED - Pending records not exported
3. **Overwrite protection**: PASSED - Existing files protected by default
4. **Dry-run mode**: PASSED - Preview without file creation

### Export Eligibility

All 9 pilot records are eligible for export:
- Review status: approved
- License status: project-owned
- Privacy status: public
- Validation: passed

---

## Limitations

### Tooling Limitations

1. **Near-duplicate detection**: Not implemented - manual review required
2. **PII detection**: Basic patterns only (email, phone, credit card) - no API key/token detection
3. **Normalization**: Case-sensitive duplicate detection - may miss variations
4. **License text parsing**: Not implemented - manual verification required

### Pilot Limitations

1. **Size**: 9 records instead of target 100 (workflow validation only)
2. **Human review**: Simulated, not actual manual review
3. **Quality scores**: Assigned as simulation (0.85), not actual quality assessment
4. **Domain coverage**: Limited coverage of all target domains

---

## Files

### Pilot Files

- `pilots/b4-b2-p1/pilot_dataset.json` - Initial pilot dataset (pending status)
- `pilots/b4-b2-p1/pilot_dataset_reviewed.json` - Reviewed pilot dataset (approved status)

### Tooling Files

- `generate_pilot.py` - Pilot dataset generator
- `validate_pilot.py` - Validation and review script
- `test_pilot_export.py` - Export safety and split generation tests
- `test_pilot_duplicates.py` - Duplicate detection test

---

## Validation Commands

```bash
# Generate pilot dataset
cd packages/ai-core/data
python generate_pilot.py

# Validate and review
python validate_pilot.py

# Test export safety
python test_pilot_export.py

# Test duplicate detection
python test_pilot_duplicates.py

# Run full test suite
python test_dataset.py
```

---

## Next Steps

1. **Expand pilot**: Create additional records to reach target distribution
2. **Actual human review**: Replace simulated review with actual manual review
3. **Quality assessment**: Assign real quality scores based on actual review
4. **Near-duplicate detection**: Implement if needed for larger scale
5. **Integration testing**: Test with frontend data collection workflow

---

## Safety Notice

This pilot dataset is for workflow validation only. It should NOT be used for model training without:
- Actual human review of each record
- Quality assessment by domain experts
- Verification of factual correctness
- Expansion to target size (100+ records)
- Clear approval for production use
