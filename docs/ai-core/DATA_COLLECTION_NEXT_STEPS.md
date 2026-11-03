# DATA_COLLECTION_NEXT_STEPS

**Date**: 2026-10-31  
**Task**: Next Steps for Data Collection  
**Plan Type**: ACTION PLAN  
**Status**: ACTION PLAN READY

---

## Executive Summary

Based on the data source discovery and storage analysis, this document defines the immediate next steps for building NexusAI's dataset foundation.

**Critical Path**: Address storage constraint → License verification → Download verified datasets → Original data creation

---

## Immediate Actions (This Week)

### 1. Storage Preparation

**Action**: Clean up C: drive to maximize free space

**Steps**:
1. Run disk cleanup utility
2. Remove temporary files
3. Clear browser cache
4. Uninstall unused programs
5. Move non-essential files to D: drive (if space allows)

**Target**: Free up additional 500 MB on C: drive

**Status**: READY TO EXECUTE

### 2. Directory Structure Creation

**Action**: Create dataset directory structure

**Steps**:
1. Create `packages/ai-core/data/sources/raw/`
2. Create `packages/ai-core/data/sources/manifests/`
3. Create `packages/ai-core/data/normalized/`
4. Create `packages/ai-core/data/cleaned/`
5. Create `packages/ai-core/data/reviewed/`
6. Create `packages/ai-core/data/exports/`
7. Create `packages/ai-core/data/backups/`
8. Create `packages/ai-core/data/reports/`

**Status**: READY TO EXECUTE

### 3. License Verification Priority 1

**Action**: Verify licenses for high-priority datasets

**Datasets**:
1. helpful_instructions (Apache 2.0) — already clear
2. Gab100MFinetune (MIT) — already clear
3. DialoguesEN-22k-Instructional (MIT) — already clear
4. Universal-Chat-SFT-Dataset (CC BY 4.0) — already clear

**Additional Verification Needed**:
- Check for attribution requirements
- Check for modification restrictions
- Check for redistribution restrictions
- Document findings

**Status**: READY TO EXECUTE

---

## Short-term Actions (1-2 Months)

### 4. Download Verified Datasets

**Action**: Download Priority 1 datasets

**Datasets**:
1. helpful_instructions (59 MB)
2. GSM8K (2.71 MB)
3. Olympiad Math (43.6 MB)
4. Universal-Chat-SFT-Dataset (unknown size)
5. DialoguesEN-22k-Instructional (unknown size)

**Total Estimated Size**: ~150-200 MB

**Steps**:
1. Download to `sources/raw/`
2. Calculate checksums
3. Store manifests
4. Verify integrity

**Status**: BLOCKED — requires directory structure + storage cleanup

### 5. Dataset Conversion and Validation

**Action**: Convert datasets to NexusAI schema

**Steps**:
1. Inspect source schema
2. Write conversion script
3. Convert to NexusAI schema v2.0
4. Validate schema compliance
5. Store in `normalized/`

**Status**: BLOCKED — requires dataset download

### 6. Human Review of Current 80 Conversations

**Action**: Execute human review workflow on existing data

**Steps**:
1. Run `human_review_cli.py`
2. Review all 80 conversations
3. Approve, reject, or needs revision
4. Document decisions
5. Move approved to `reviewed/approved/`

**Status**: READY TO EXECUTE

### 7. Original Bengali Data Creation

**Action**: Begin creating 5,000 Bengali conversations

**Steps**:
1. Recruit native Bengali speakers
2. Provide authoring guidelines
3. Author 5,000 conversations
4. Validate grammar and spelling
5. Cultural review
6. Schema compliance
7. Human review
8. Approval

**Status**: READY TO EXECUTE

### 8. Original Banglish Data Creation

**Action**: Begin creating 2,000 Banglish conversations

**Steps**:
1. Recruit Banglish speakers
2. Provide authoring guidelines
3. Author 2,000 conversations
4. Validate code-switching patterns
5. Schema compliance
6. Human review
7. Approval

**Status**: READY TO EXECUTE

---

## Medium-term Actions (2-6 Months)

### 9. External Storage Acquisition

**Action**: Purchase 1 TB external drive

**Steps**:
1. Research options (1 TB USB 3.0 external HDD/SSD)
2. Purchase (~$50-100)
3. Format drive
4. Move data directory to external drive
5. Update storage configuration

**Status**: BLOCKED — requires budget approval

### 10. License Verification for Bengali Datasets

**Action**: Verify licenses for Bengali datasets

**Datasets**:
1. B-CORE-bengali-corpus
2. bnnews
3. bangla-llm-data
4. xnli_bn
5. BanglaNMT

**Steps**:
1. Review dataset documentation
2. Check license files
3. Contact authors if unclear
4. Document findings
5. Update registry

**Status**: READY TO EXECUTE

### 11. Download Medium-sized Datasets

**Action**: Download datasets after external storage available

**Datasets**:
1. bnnews (755 MB)
2. Gab100MFinetune (831 MB)
3. B-CORE-bengali-corpus (52 GB) — if license verified

**Status**: BLOCKED — requires external storage

### 12. Original English Data Creation

**Action**: Create 5,000 English conversations

**Steps**: Same as Bengali creation

**Status**: READY TO EXECUTE

---

## Long-term Actions (6+ Months)

### 13. Large Dataset Collection

**Action**: Download and process large datasets

**Datasets**:
- B-CORE-bengali-corpus (52 GB)
- Other large datasets if needed

**Status**: BLOCKED — requires external storage + license verification

### 14. Cloud Backup Implementation

**Action**: Implement cloud backup for critical data

**Steps**:
1. Select cloud provider
2. Set up account
3. Configure backup tool
4. Test backup and restore
5. Schedule regular backups

**Status**: BLOCKED — requires external storage + budget

### 15. User Feedback Collection

**Action**: Implement user feedback collection system

**Steps**:
1. Design feedback UI
2. Implement feedback API
3. Add consent mechanism
4. Test with real users
5. Integrate with review workflow

**Status**: BLOCKED — requires application development

---

## Critical Path

### Week 1
1. Clean up C: drive
2. Create directory structure
3. Review current 80 conversations
4. Begin original data creation (Bengali + Banglish)

### Week 2-4
1. Download verified small datasets
2. Convert and validate
3. Continue original data creation
4. License verification for medium datasets

### Month 2-3
1. Acquire external storage
2. Download medium datasets
3. Continue original data creation
4. Implement versioning

### Month 4-6
1. Download large datasets (if license verified)
2. Complete original data creation targets
3. Implement cloud backup
4. Comprehensive data quality analysis

---

## Dependencies and Blockers

### Blockers
1. **Storage Constraint**: Blocks large dataset downloads
   - **Resolution**: External storage required

2. **License Verification**: Blocks 43 of 58 datasets
   - **Resolution**: Legal review required

3. **Banglish Data Gap**: No high-quality public datasets
   - **Resolution**: Original data creation required

4. **Native Speaker Availability**: Limits original data creation speed
   - **Resolution**: Gradual collection, prioritize quality

### Dependencies
- Directory structure creation depends on storage cleanup
- Dataset download depends on directory structure
- Data conversion depends on dataset download
- Human review depends on data conversion
- Large dataset download depends on external storage

---

## Risk Mitigation

### Risk 1: Storage Constraint Persists
**Mitigation**: Proceed with original data creation (small footprint), defer large datasets

### Risk 2: License Verification Fails
**Mitigation**: Primary reliance on original data creation

### Risk 3: Insufficient Native Speakers
**Mitigation**: Gradual collection, extend timeline if needed

### Risk 4: Budget Not Approved for External Storage
**Mitigation**: Use Option A (current storage) as fallback, accept limitations

---

## Success Criteria

### Phase 1 (1 month)
- ✅ Directory structure created
- ✅ Current 80 conversations reviewed
- ✅ 1,000 original Bengali conversations created
- ✅ 500 original Banglish conversations created
- ✅ 3 verified datasets downloaded

### Phase 2 (3 months)
- ✅ External storage acquired
- ✅ 5,000 original Bengali conversations created
- ✅ 2,000 original Banglish conversations created
- ✅ 5,000 original English conversations created
- ✅ 10 verified datasets downloaded

### Phase 3 (6 months)
- ✅ 20,000 total conversations created/downloaded
- ✅ All datasets reviewed and approved
- ✅ Versioning implemented
- ✅ Backup system operational

---

## Resource Requirements

### Time
- Phase 1: 40 hours (cleanup, structure, review, creation)
- Phase 2: 80 hours (storage, downloads, creation)
- Phase 3: 120 hours (large datasets, backup, analysis)

### Personnel
- 1 Data Engineer (full-time)
- 1 Native Bengali Speaker (part-time)
- 1 Native Banglish Speaker (part-time)
- 1 Reviewer (part-time)

### Budget
- External storage: $50-100
- Cloud backup: $0-10/month (optional)
- Data creation compensation: TBD

---

## Monitoring and Reporting

### Weekly Reports
- Storage usage
- Dataset downloads
- Original data creation progress
- Human review status
- Blockers and issues

### Monthly Reports
- Total dataset size
- Language distribution
- Domain coverage
- Quality metrics
- Risks and mitigations

---

## Decision Points

### Decision 1: External Storage Purchase
**When**: Week 2-4
**Decision Point**: Proceed with 1 TB external drive?
**Options**: Yes, No, Wait

### Decision 2: Bengali Dataset License
**When**: Month 2
**Decision Point**: Use B-CORE-bengali-corpus if license verified?
**Options**: Yes, No, Partial

### Decision 3: Cloud Backup
**When**: Month 4-6
**Decision Point**: Implement cloud backup?
**Options**: Yes, No, Later

---

## Next Steps Summary

**This Week**:
1. Clean up C: drive
2. Create directory structure
3. Review current 80 conversations
4. Begin original data creation

**This Month**:
1. Download verified small datasets
2. Convert and validate
3. Continue original data creation
4. License verification

**Next 3 Months**:
1. Acquire external storage
2. Download medium datasets
3. Complete Phase 1 targets
4. Implement versioning

---

**Action Plan Created**: 2026-10-31  
**Status**: ACTION PLAN READY
