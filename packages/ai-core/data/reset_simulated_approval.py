"""
Reset simulated approval status to pending for human review.
This script corrects the B4-B2-P1 pilot dataset to reflect that approval was simulated.
"""

import os
os.chdir(os.path.dirname(__file__))

from dataset_schema import Dataset, ReviewStatus

# Load the reviewed pilot dataset
pilot_path = os.path.join("pilots", "b4-b2-p1", "pilot_dataset_reviewed.json")
dataset = Dataset.from_json_file(pilot_path)

print("RESETTING SIMULATED APPROVAL STATUS")
print("="*60)

# Reset all records to pending status
for conv in dataset.conversations:
    print(f"[RESET] {conv.record_id}: {conv.review_status.value} -> pending")
    conv.review_status = ReviewStatus.PENDING
    conv.reviewer = None
    conv.review_date = None
    conv.quality_score = 0.0
    if conv.notes:
        conv.notes += " | SIMULATED APPROVAL RESET - Requires genuine human review"
    else:
        conv.notes = "SIMULATED APPROVAL RESET - Requires genuine human review"

dataset.update_statistics()

# Save as pending dataset
pending_path = os.path.join("pilots", "b4-b2-p1", "pilot_dataset_pending_review.json")
dataset.to_json_file(pending_path)

print(f"\nPending dataset saved to: {pending_path}")
print(f"Total records: {len(dataset.conversations)}")
print(f"All records now require genuine human review")
print("="*60)
