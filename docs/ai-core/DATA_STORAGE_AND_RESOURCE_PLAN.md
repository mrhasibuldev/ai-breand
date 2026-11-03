# DATA_STORAGE_AND_RESOURCE_PLAN

**Date**: 2026-10-31  
**Task**: Storage and Resource Planning  
**Plan Type**: STORAGE ARCHITECTURE  
**Status**: PLAN COMPLETE — EXTERNAL STORAGE REQUIRED

---

## Executive Summary

The current storage capacity (2.9 GB free on C:, 50 MB on D:) is insufficient for large-scale dataset collection. This plan provides three options for addressing the storage constraint.

**Critical Finding**: External storage (1-2 TB) is required for full dataset foundation.

---

## Current Storage Status

### Available Space
- **C: Drive**: 3.05 GB free (119 GB total)
- **D: Drive**: 50 MB free (29.7 GB total) — ESSENTIALLY FULL

### Current Data Usage
- **Data Directory**: 0.8 MB (867.8 KB)
- **Current 80 conversations**: 109.6 KB

### Storage Constraints
- Cannot download datasets > 2 GB
- Cannot store multiple dataset versions
- Cannot keep raw + processed + backups

---

## Dataset Size Estimates

### Individual Datasets

| Dataset | Compressed | Extracted | Processed | Backup | Total |
|---------|-----------|-----------|-----------|--------|-------|
| helpful_instructions | 59 MB | 60 MB | 70 MB | 70 MB | 140 MB |
| Gab100MFinetune | 831 MB | 850 MB | 1 GB | 1 GB | 2 GB |
| B-CORE-bengali-corpus | 20.8 GB | 52 GB | 60 GB | 60 GB | 120 GB |
| bnnews | 755 MB | 755 MB | 800 MB | 800 MB | 1.6 GB |
| GSM8K | 2.71 MB | 3 MB | 5 MB | 5 MB | 10 MB |
| Olympiad Math | 43.6 MB | 45 MB | 50 MB | 50 MB | 100 MB |

### Full Dataset Foundation Estimates

**Phase 1 Target** (17,000 conversations):
- Raw data: ~40 MB
- Processed: ~50 MB
- Backup: ~50 MB
- **Total**: ~140 MB ✅ fits

**Phase 2 Target** (35,000 conversations):
- Raw data: ~100 MB
- Processed: ~150 MB
- Backup: ~150 MB
- **Total**: ~400 MB ✅ fits

**Phase 3 Target** (60,000 conversations):
- Raw data: ~200 MB
- Processed: ~300 MB
- Backup: ~300 MB
- **Total**: ~800 MB ✅ fits

**With Large Public Datasets**:
- B-CORE: 120 GB ❌
- The Stack: 6 TB ❌
- StarCoder: 783 GB ❌

---

## Option A: Current Computer (Minimal)

### What Can Be Done
- Original data creation only
- Small verified datasets (< 1 GB)
- Incremental download-process-delete workflow

### Feasible Dataset Collection
- helpful_instructions (59 MB) ✅
- GSM8K (2.71 MB) ✅
- Olympiad Math (43.6 MB) ✅
- Universal-Chat-SFT (unknown, likely small) ✅
- DialoguesEN-22k (unknown, likely small) ✅
- Original data creation (40 MB) ✅

**Total**: ~150-200 MB

### Limitations
- Cannot use large Bengali datasets (B-CORE: 52 GB)
- Cannot use code datasets (The Stack: 6 TB)
- Cannot keep multiple versions
- Cannot keep raw + processed + backups
- Limited to ~2-3 GB total

### Strategy
1. Clean up C: drive (remove unnecessary files)
2. Download only small verified datasets
3. Process and delete raw data immediately
4. Keep only processed data
5. Manual backup to external drive if available

### Pros
- No additional cost
- Immediate action possible
- Can build initial foundation

### Cons
- Severely limited long-term
- Cannot use high-value large datasets
- No version history
- Risk of data loss

---

## Option B: External Storage (Recommended)

### 1 TB External Drive

**Capacity Breakdown**:
- Raw data: 200 GB
- Processed data: 300 GB
- Backups: 300 GB
- System overhead: 100 GB
- Free space: 100 GB
- **Total**: 1 TB

**Feasible Dataset Collection**:
- All Option A datasets ✅
- B-CORE-bengali-corpus (52 GB) ✅
- bnnews (755 MB) ✅
- Multiple dataset versions ✅
- Raw + processed + backups ✅

**Estimated Timeline**: 12-18 months to fill

### 2 TB External Drive

**Capacity Breakdown**:
- Raw data: 500 GB
- Processed data: 700 GB
- Backups: 700 GB
- System overhead: 100 GB
- Free space: 0 GB
- **Total**: 2 TB

**Feasible Dataset Collection**:
- All 1 TB datasets ✅
- Medium code datasets (if needed) ✅
- Multiple major versions ✅
- Full version history ✅

**Estimated Timeline**: 24-36 months to fill

### Recommended Action
**Start with 1 TB external drive**:
- Sufficient for current needs
- Lower cost
- Can upgrade to 2 TB later if needed

### Pros
- Enables large dataset collection
- Version history possible
- Backup protection
- Future-proof
- Lower risk of data loss

### Cons
- Additional cost (~$50-100)
- Requires hardware purchase
- Transfer time for large datasets

---

## Option C: Future Expandable Storage (Long-term)

### Cloud Storage Architecture

**Design Principles**:
- Hybrid local + cloud
- Local cache for frequently used data
- Cloud for archive and backup
- Streaming from cloud for large datasets

**Cloud Providers**:
- Google Drive (15 GB free, paid tiers)
- Dropbox (2 GB free, paid tiers)
- AWS S3 (pay-as-you-go)
- Microsoft OneDrive (5 GB free, paid tiers)

**Storage Strategy**:
1. **Local**: Current working dataset (200-500 GB)
2. **Cloud Archive**: Older versions, raw data, backups
3. **Streaming**: Load from cloud as needed (for TB-scale datasets)

### Pros
- Scalable to unlimited size
- Accessible from anywhere
- Built-in redundancy
- Version history
- Collaboration support

### Cons
- Ongoing cost
- Internet dependency
- Transfer time
- Privacy concerns (data on third-party servers)
- Bandwidth requirements

### Recommendation
**Implement only after local storage is established**:
- Start with external drive (Option B)
- Add cloud backup later
- Keep primary data local for performance

---

## Recommended Strategy

### Immediate (No Cost)
1. Clean up C: drive to maximize free space
2. Download small verified datasets (Option A)
3. Begin original data creation
4. Implement incremental download-process-delete

### Short-term (Recommended)
1. Purchase 1 TB external drive (~$50-100)
2. Move data directory to external drive
3. Download medium-sized datasets (bnnews, etc.)
4. Implement versioning and backups

### Long-term
1. Upgrade to 2 TB if needed
2. Add cloud backup for critical data
3. Consider cloud streaming for TB-scale datasets

---

## Directory Structure Design

### Recommended Structure

```
packages/ai-core/data/
├── sources/              # Original raw data (immutable)
│   ├── raw/
│   │   ├── public/
│   │   └── original/
│   └── manifests/
├── normalized/           # Normalized but not cleaned
├── cleaned/              # Cleaned and validated
├── reviewed/             # Human-reviewed
│   ├── approved/
│   ├── rejected/
│   └── needs_revision/
├── exports/              # Training-ready exports
├── backups/              # Backups by version
├── reports/              # Analysis reports
├── schemas/              # Schema definitions
└── tools/                # Processing tools
```

### Versioning Strategy

**Semantic Versioning**:
- v1.0.0: Initial dataset
- v1.1.0: Addition of new data
- v2.0.0: Major restructure or new data type

**Storage per Version**:
- Keep raw data for current version only
- Archive raw data for previous versions
- Keep processed data for last 3 versions
- Keep metadata for all versions

---

## Backup Strategy

### Local Backup
- External drive primary backup
- Incremental backups (daily/weekly)
- Full backup before major changes

### Cloud Backup (Future)
- Critical data only
- Encrypted storage
- Version history

### Recovery Plan
- Documented backup procedures
- Regular backup verification
- Recovery drill (restore test)

---

## Data Lifecycle

### Acquisition Phase
1. Download to sources/raw/
2. Calculate checksum
3. Store manifest
4. Keep immutable

### Processing Phase
1. Copy to normalized/
2. Normalize text
3. Validate schema
4. Move to cleaned/

### Review Phase
1. Copy to reviewed/
2. Human review
3. Move to approved/ or rejected/
4. Update status

### Export Phase
1. Export to exports/
2. Version tag
3. Create backup
4. Archive old versions

---

## Implementation Steps

### Phase 1: Current Storage (Immediate)
1. Clean up C: drive
2. Create directory structure
3. Download helpful_instructions (59 MB)
4. Test pipeline

### Phase 2: External Storage (1-2 months)
1. Purchase 1 TB external drive
2. Move data directory
3. Download bnnews (755 MB)
4. Implement versioning

### Phase 3: Expansion (3-6 months)
1. Acquire B-CORE if license verified
2. Implement full pipeline
3. Add cloud backup
4. Scale as needed

---

## Storage Planning Summary

| Option | Capacity | Cost | Feasibility | Recommendation |
|--------|----------|------|-------------|----------------|
| A: Current | 2-3 GB | $0 | Limited | Short-term only |
| B: 1 TB External | 1 TB | $50-100 | Good | RECOMMENDED |
| B: 2 TB External | 2 TB | $80-150 | Excellent | Future |
| C: Cloud | Unlimited | Ongoing | Good | Long-term |

---

**Plan Created**: 2026-10-31  
**Status**: PLAN COMPLETE — EXTERNAL STORAGE REQUIRED
