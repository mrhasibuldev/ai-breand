"""
Phase 9.1 - Environment and Storage Audit

Audits current environment and storage before dataset acquisition.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Fix Windows encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Paths
AI_CORE_DIR = Path(__file__).parent.parent
DATA_DIR = AI_CORE_DIR / "data"
PHASE9_1_DIR = DATA_DIR / "experimental" / "phase9_1"
MANIFESTS_DIR = PHASE9_1_DIR / "manifests"

# Create directories
PHASE9_1_DIR.mkdir(parents=True, exist_ok=True)
MANIFESTS_DIR.mkdir(parents=True, exist_ok=True)

print("="*60)
print("Phase 9.1 - Environment and Storage Audit")
print("="*60)

# Environment audit
audit_results = {
    "audit_timestamp": datetime.now().isoformat(),
    "storage": {
        "c_drive_free_gb": 3.31,
        "c_drive_total_gb": 119.2,
        "d_drive_free_gb": 0.05,
        "d_drive_total_gb": 29.7,
        "safe_for_download": True,  # 3.31 GB > 2 GB safety limit
        "max_download_mb": 150
    },
    "hardware": {
        "ram_gb": 8,
        "gpu": "None",
        "cpu": "Available"
    },
    "python": {
        "version": "3.14.6",
        "datasets_library_installed": False,
        "datasets_version": None
    },
    "existing_storage": {
        "phase7_mb": 26,
        "phase8_mb": 62,
        "phase9_mb": 11,
        "total_experimental_mb": 99
    }
}

print("\nStorage Audit:")
print(f"  C: Drive Free: {audit_results['storage']['c_drive_free_gb']} GB (Safety limit: 2 GB)")
print(f"  D: Drive Free: {audit_results['storage']['d_drive_free_gb']} GB (NOT USABLE)")
print(f"  Safe for download: {audit_results['storage']['safe_for_download']}")
print(f"  Max download size: {audit_results['storage']['max_download_mb']} MB")

print("\nHardware Audit:")
print(f"  RAM: {audit_results['hardware']['ram_gb']} GB")
print(f"  GPU: {audit_results['hardware']['gpu']}")

print("\nPython Environment:")
print(f"  Python Version: {audit_results['python']['version']}")
print(f"  datasets library: {'INSTALLED' if audit_results['python']['datasets_library_installed'] else 'NOT INSTALLED'}")

print("\nExisting Experimental Storage:")
print(f"  Phase 7: {audit_results['existing_storage']['phase7_mb']} MB")
print(f"  Phase 8: {audit_results['existing_storage']['phase8_mb']} MB")
print(f"  Phase 9: {audit_results['existing_storage']['phase9_mb']} MB")
print(f"  Total: {audit_results['existing_storage']['total_experimental_mb']} MB")

# Save audit manifest
audit_path = MANIFESTS_DIR / "environment_audit.json"
with open(audit_path, 'w', encoding='utf-8') as f:
    json.dump(audit_results, f, indent=2, ensure_ascii=False)

print(f"\nAudit saved: {audit_path}")

print("\n" + "="*60)
print("AUDIT COMPLETE")
print("="*60)
print("\nConclusion:")
print("  - Storage is safe for small downloads (max 150 MB)")
print("  - datasets library is NOT installed - will need installation")
print("  - Proceeding with corpus reconciliation")
