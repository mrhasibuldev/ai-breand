#!/usr/bin/env python3
"""
NexusAI Human Review CLI

Command-line interface for reviewing dataset conversations.
Provides a safe, auditable workflow for human review without requiring web UI.
"""

import json
import hashlib
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class ReviewDecision:
    """Review decision data"""
    record_id: str
    decision: str  # "approved", "rejected", "needs_revision"
    reviewer_id: str
    review_timestamp: str
    content_hash: str
    notes: Optional[str] = None
    review_schema_version: str = "1.0"


class HumanReviewCLI:
    """Human review command-line interface"""
    
    def __init__(self, dataset_path: str, review_output_path: str):
        self.dataset_path = Path(dataset_path)
        self.review_output_path = Path(review_output_path)
        self.conversations: List[Dict[str, Any]] = []
        self.review_decisions: Dict[str, ReviewDecision] = {}
        self.current_index = 0
        self.filter_status = "pending"  # pending, approved, rejected, needs_revision, all
        
        # Load dataset
        self.load_dataset()
        
        # Load existing reviews
        self.load_reviews()
    
    def load_dataset(self):
        """Load conversations from dataset file"""
        print(f"Loading dataset from {self.dataset_path}...")
        
        with open(self.dataset_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.conversations = data.get('conversations', [])
        self.metadata = data.get('metadata', {})
        
        print(f"Loaded {len(self.conversations)} conversations")
        print(f"Dataset: {self.metadata.get('dataset_name', 'unknown')}")
        print(f"Version: {self.metadata.get('dataset_version', 'unknown')}")
        print()
    
    def load_reviews(self):
        """Load existing review decisions"""
        if not self.review_output_path.exists():
            print("No existing review file found. Starting fresh.")
            print()
            return
        
        with open(self.review_output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for decision_data in data.get('decisions', []):
            decision = ReviewDecision(**decision_data)
            self.review_decisions[decision.record_id] = decision
        
        print(f"Loaded {len(self.review_decisions)} existing review decisions")
        print()
    
    def compute_content_hash(self, conversation: Dict[str, Any]) -> str:
        """Compute SHA256 hash of conversation content"""
        # Hash only the actual conversation data, not metadata
        content_str = json.dumps(conversation, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(content_str.encode('utf-8')).hexdigest()
    
    def get_review_status(self, record_id: str) -> str:
        """Get review status for a record"""
        if record_id not in self.review_decisions:
            return "pending"
        return self.review_decisions[record_id].decision
    
    def get_filtered_conversations(self) -> List[Dict[str, Any]]:
        """Get conversations based on current filter"""
        if self.filter_status == "all":
            return self.conversations
        
        filtered = []
        for conv in self.conversations:
            status = self.get_review_status(conv['record_id'])
            if status == self.filter_status:
                filtered.append(conv)
        
        return filtered
    
    def display_conversation(self, conversation: Dict[str, Any]):
        """Display a conversation for review"""
        print("=" * 80)
        print(f"RECORD ID: {conversation['record_id']}")
        print(f"Conversation ID: {conversation['conversation_id']}")
        print(f"Language: {conversation.get('language', 'unknown')}")
        print(f"Domain: {conversation.get('domain', 'unknown')}")
        print(f"Source: {conversation.get('source_type', 'unknown')}")
        print()
        
        # Display messages
        messages = conversation.get('messages', [])
        for msg in messages:
            role = msg['role'].upper()
            lang = msg.get('language', 'unknown')
            content = msg['content']
            print(f"[{role} ({lang})]")
            print(f"{content}")
            print()
        
        # Display metadata
        print("-" * 80)
        print("METADATA:")
        print(f"Provenance: {conversation.get('provenance', 'unknown')}")
        print(f"License: {conversation.get('license_status', 'unknown')}")
        print(f"Privacy: {conversation.get('privacy_status', 'unknown')}")
        print(f"Duplicate check: {conversation.get('duplicate_check', 'not_checked')}")
        print(f"Quality score: {conversation.get('quality_score', 'not_scored')}")
        print()
        
        # Display current review status
        record_id = conversation['record_id']
        if record_id in self.review_decisions:
            decision = self.review_decisions[record_id]
            print(f"CURRENT STATUS: {decision.decision.upper()}")
            print(f"Reviewed by: {decision.reviewer_id}")
            print(f"Reviewed at: {decision.review_timestamp}")
            if decision.notes:
                print(f"Notes: {decision.notes}")
        else:
            print("CURRENT STATUS: PENDING")
        
        print("=" * 80)
        print()
    
    def display_progress(self):
        """Display review progress"""
        total = len(self.conversations)
        pending = sum(1 for c in self.conversations if self.get_review_status(c['record_id']) == 'pending')
        approved = sum(1 for c in self.conversations if self.get_review_status(c['record_id']) == 'approved')
        rejected = sum(1 for c in self.conversations if self.get_review_status(c['record_id']) == 'rejected')
        needs_revision = sum(1 for c in self.conversations if self.get_review_status(c['record_id']) == 'needs_revision')
        
        print(f"Progress: {approved} approved | {rejected} rejected | {needs_revision} needs revision | {pending} pending (total: {total})")
        print()
    
    def approve(self, notes: str = None, interactive: bool = True):
        """Approve current conversation"""
        conv = self.get_filtered_conversations()[self.current_index]
        record_id = conv['record_id']
        
        # Quality checks before approval
        if not self.run_quality_gates(conv, interactive):
            print("Quality gates failed. Cannot approve.")
            return
        
        # Create review decision
        content_hash = self.compute_content_hash(conv)
        decision = ReviewDecision(
            record_id=record_id,
            decision="approved",
            reviewer_id="project-owner",  # In production, this would be authenticated
            review_timestamp=datetime.now(timezone.utc).isoformat(),
            content_hash=content_hash,
            notes=notes
        )
        
        self.review_decisions[record_id] = decision
        self.save_reviews()
        print(f"[APPROVED] {record_id}")
        print()
    
    def reject(self, notes: str = None):
        """Reject current conversation"""
        conv = self.get_filtered_conversations()[self.current_index]
        record_id = conv['record_id']
        
        content_hash = self.compute_content_hash(conv)
        decision = ReviewDecision(
            record_id=record_id,
            decision="rejected",
            reviewer_id="project-owner",
            review_timestamp=datetime.now(timezone.utc).isoformat(),
            content_hash=content_hash,
            notes=notes
        )
        
        self.review_decisions[record_id] = decision
        self.save_reviews()
        print(f"[REJECTED] {record_id}")
        print()
    
    def needs_revision(self, notes: str = None):
        """Mark current conversation as needing revision"""
        conv = self.get_filtered_conversations()[self.current_index]
        record_id = conv['record_id']
        
        content_hash = self.compute_content_hash(conv)
        decision = ReviewDecision(
            record_id=record_id,
            decision="needs_revision",
            reviewer_id="project-owner",
            review_timestamp=datetime.now(timezone.utc).isoformat(),
            content_hash=content_hash,
            notes=notes
        )
        
        self.review_decisions[record_id] = decision
        self.save_reviews()
        print(f"[NEEDS REVISION] {record_id}")
        print()
    
    def run_quality_gates(self, conversation: Dict[str, Any], interactive: bool = True) -> bool:
        """Run quality checks before approval"""
        print("Running quality gates...")
        
        # Check 1: Required fields
        required_fields = ['record_id', 'conversation_id', 'messages', 'language', 'domain']
        for field in required_fields:
            if field not in conversation or not conversation[field]:
                print(f"[FAIL] Missing required field: {field}")
                return False
        
        # Check 2: Messages exist
        messages = conversation.get('messages', [])
        if not messages or len(messages) < 2:
            print("[FAIL] Conversation must have at least 2 messages (user + assistant)")
            return False
        
        # Check 3: Valid license
        license_status = conversation.get('license_status')
        if license_status not in ['project-owned', 'verified-external']:
            print(f"[WARN] License status not verified: {license_status}")
            if interactive:
                response = input("Continue anyway? (y/n): ")
                if response.lower() != 'y':
                    return False
            else:
                print("[SKIP] Non-interactive mode: auto-failing unverified license")
                return False
        
        # Check 4: No PII
        privacy_status = conversation.get('privacy_status')
        if privacy_status == 'contains_pii':
            print("[FAIL] Contains PII - cannot approve")
            return False
        
        # Check 5: Duplicate check
        duplicate_check = conversation.get('duplicate_check')
        if duplicate_check == 'is_duplicate':
            print("[FAIL] Marked as duplicate - cannot approve")
            return False
        
        # Check 6: Bengali/Banglish marker
        language = conversation.get('language')
        if language in ['bengali', 'mixed']:
            print("[WARN] Bengali or mixed-language conversation")
            print("  Ensure native or highly proficient language review was performed")
            if interactive:
                response = input("Confirm language review was performed? (y/n): ")
                if response.lower() != 'y':
                    return False
            else:
                print("[SKIP] Non-interactive mode: auto-failing Bengali review check")
                return False
        
        print("[PASS] All quality gates passed")
        return True
    
    def save_reviews(self):
        """Save review decisions to file"""
        output = {
            "schema_version": "1.0",
            "review_metadata": {
                "created": datetime.now(timezone.utc).isoformat(),
                "dataset_source": str(self.dataset_path),
                "reviewer_mode": "project-owner"  # Document limitation
            },
            "decisions": [asdict(d) for d in self.review_decisions.values()]
        }
        
        with open(self.review_output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
    
    def show_menu(self):
        """Display main menu"""
        filtered = self.get_filtered_conversations()
        
        if not filtered:
            print(f"No conversations with status: {self.filter_status}")
            print()
            self.change_filter()
            return
        
        conv = filtered[self.current_index]
        
        print(f"Reviewing: {self.current_index + 1} / {len(filtered)} (filter: {self.filter_status})")
        print()
        
        self.display_conversation(conv)
        self.display_progress()
        
        print("ACTIONS:")
        print("  [a] Approve")
        print("  [r] Reject")
        print("  [n] Needs Revision")
        print("  [p] Previous")
        print("  [next] Next")
        print("  [f] Change filter")
        print("  [s] Search by ID")
        print("  [q] Quit")
        print()
    
    def change_filter(self):
        """Change filter status"""
        print("Current filter:", self.filter_status)
        print("Available filters: pending, approved, rejected, needs_revision, all")
        print()
        
        choice = input("Enter filter: ").strip().lower()
        
        valid_filters = ['pending', 'approved', 'rejected', 'needs_revision', 'all']
        if choice in valid_filters:
            self.filter_status = choice
            self.current_index = 0
            print(f"Filter changed to: {self.filter_status}")
        else:
            print("Invalid filter")
        
        print()
    
    def search_by_id(self):
        """Search conversation by record ID"""
        search_id = input("Enter record ID (or partial): ").strip()
        
        for i, conv in enumerate(self.conversations):
            if search_id in conv['record_id']:
                self.filter_status = "all"
                self.current_index = i
                print(f"Found: {conv['record_id']}")
                print()
                return
        
        print("Not found")
        print()
    
    def run(self):
        """Run the review CLI"""
        print("NEXUSAI HUMAN REVIEW CLI")
        print("=" * 80)
        print()
        
        while True:
            self.show_menu()
            
            choice = input("Action: ").strip().lower()
            
            if choice == 'a':
                notes = input("Notes (optional, press Enter to skip): ").strip() or None
                self.approve(notes)
                self.next()
            elif choice == 'r':
                notes = input("Notes (optional, press Enter to skip): ").strip() or None
                self.reject(notes)
                self.next()
            elif choice == 'n':
                notes = input("Notes (optional, press Enter to skip): ").strip() or None
                self.needs_revision(notes)
                self.next()
            elif choice == 'p':
                self.previous()
            elif choice == 'next':
                self.next()
            elif choice == 'f':
                self.change_filter()
            elif choice == 's':
                self.search_by_id()
            elif choice == 'q':
                print("Saving reviews...")
                self.save_reviews()
                print("Goodbye!")
                break
            else:
                print("Invalid action")
                print()
    
    def next(self):
        """Move to next conversation"""
        filtered = self.get_filtered_conversations()
        if self.current_index < len(filtered) - 1:
            self.current_index += 1
        else:
            print("End of list")
            print()
    
    def previous(self):
        """Move to previous conversation"""
        if self.current_index > 0:
            self.current_index -= 1
        else:
            print("Start of list")
            print()


def main():
    """Main entry point"""
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python human_review_cli.py <dataset_path> <review_output_path>")
        print()
        print("Example:")
        print("  python human_review_cli.py \\")
        print("    packages/ai-core/data/pilots/b4-b2-p1/pilot_dataset_expansion_drafts.json \\")
        print("    packages/ai-core/data/pilots/b4-b2-p1/human_review_decisions.json")
        sys.exit(1)
    
    dataset_path = sys.argv[1]
    review_output_path = sys.argv[2]
    
    cli = HumanReviewCLI(dataset_path, review_output_path)
    cli.run()


if __name__ == "__main__":
    main()
