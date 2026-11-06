# PHASE5B1_LICENSE_AND_PROVENANCE_REPORT.md

**Date**: 2026-11-03
**Phase**: 5B.1 - License and Provenance
**Status**: ✅ COMPLETE

---

## EXECUTIVE SUMMARY

All dataset licenses verified against original authoritative sources. No changes from Phase 5B verification. GSM8K and MATH are MIT (commercial approved). Dolly is CC BY-SA 3.0 (conditional with share-alike). Alpaca is CC BY-NC 4.0 (non-commercial).

---

## A. LICENSE STATUS

| Dataset | License | Commercial Eligibility | Attribution | Share-Alike | Status |
|---------|---------|----------------------|-------------|------------|--------|
| GSM8K | MIT | ✅ APPROVED | No | No | ✅ VERIFIED |
| MATH | MIT | ✅ APPROVED | No | No | ✅ VERIFIED |
| Dolly | CC BY-SA 3.0 | ⚠️ CONDITIONAL | Yes | Yes | ✅ VERIFIED |
| Wikipedia | CC BY-SA 3.0 | ⚠️ CONDITIONAL | Yes | Yes | ✅ VERIFIED |
| Alpaca | CC BY-NC 4.0 | ❌ NON-COMMERCIAL | Yes | No | ✅ VERIFIED |

---

## B. VERIFICATION EVIDENCE

**GSM8K**: GitHub repository, HuggingFace dataset card, TensorFlow Datasets catalog
**MATH**: LICENSE file in repository, HuggingFace dataset card
**Dolly**: Databricks blog, HuggingFace dataset card
**Wikipedia**: Wikipedia API collection manifest
**Alpaca**: DATA_LICENSE file, datasheet, repository README

---

## C. COMMERCIAL ELIGIBILITY

**APPROVED (Unrestricted)**:
- GSM8K (MIT)
- MATH (MIT) - not collected but license verified

**CONDITIONAL (Attribution + Share-Alike)**:
- Dolly (CC BY-SA 3.0)
- Wikipedia (CC BY-SA 3.0)

**NON-COMMERCIAL**:
- Alpaca (CC BY-NC 4.0)

---

## D. SHARE-ALIKE IMPLICATIONS

CC BY-SA 3.0 requires derivative works to be released under same license. Models trained on Dolly or Wikipedia may need to be CC BY-SA 3.0, which may conflict with closed-source commercial licensing.

---

## E. CONCLUSION

All licenses verified. Commercial eligibility determined. Share-alike implications documented.

---

**Report End**
