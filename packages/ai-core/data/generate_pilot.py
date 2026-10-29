"""
NexusAI Stage B4-B2-P1 Pilot Dataset Generator

Creates original pilot conversation records to validate the dataset workflow.
This is a controlled pilot, NOT production training data.
"""

import os
from dataset_schema import (
    ConversationRecord, Message, Language, Domain, SourceType,
    ReviewStatus, LicenseStatus, PrivacyStatus, Split
)
from dataset_processor import DatasetProcessor
from dataset_validator import DatasetValidator
from datetime import datetime


def create_bengali_conversation_1():
    """Bengali greeting"""
    return ConversationRecord(
        record_id="PILOT-B4B2P1-BENG-001",
        dataset_version="1.0.0",
        conversation_id="PILOT-CONV-BENG-001",
        split=Split.PENDING,
        language=Language.BENGALI,
        domain=Domain.CONVERSATION,
        messages=[
            Message(role="user", content="আপমাকে নাম কি?", language=Language.BENGALI, turn_index=0),
            Message(role="assistant", content="আমার নাম NexusAI। আমি একটি AI সহকারী যা আপনাকে সাহায্য করতে পারি।", language=Language.BENGALI, turn_index=1)
        ],
        source_type=SourceType.ORIGINAL_HUMAN,
        source_reference="manual authoring for pilot",
        creator="pilot-author",
        created_at=datetime.utcnow().isoformat(),
        review_status=ReviewStatus.PENDING,
        quality_score=0.0,
        license_status=LicenseStatus.PROJECT_OWNED,
        privacy_status=PrivacyStatus.PUBLIC,
        tags=["pilot", "bengali", "greeting"],
        notes="PILOT DATA - NOT FOR PRODUCTION TRAINING"
    )


def create_bengali_conversation_2():
    """Bengali capability question"""
    return ConversationRecord(
        record_id="PILOT-B4B2P1-BENG-002",
        dataset_version="1.0.0",
        conversation_id="PILOT-CONV-BENG-002",
        split=Split.PENDING,
        language=Language.BENGALI,
        domain=Domain.CONVERSATION,
        messages=[
            Message(role="user", content="তুমি কী করতে পারো?", language=Language.BENGALI, turn_index=0),
            Message(role="assistant", content="আমি কথোপকথনের মাধ্যমে সাহায্য করতে পারি, প্রশ্নের উত্তর দিতে পারি, এবং বিভিন্ন কাজে সহায্য করতে পারি।", language=Language.BENGALI, turn_index=1)
        ],
        source_type=SourceType.ORIGINAL_HUMAN,
        source_reference="manual authoring for pilot",
        creator="pilot-author",
        created_at=datetime.utcnow().isoformat(),
        review_status=ReviewStatus.PENDING,
        quality_score=0.0,
        license_status=LicenseStatus.PROJECT_OWNED,
        privacy_status=PrivacyStatus.PUBLIC,
        tags=["pilot", "bengali", "capability"],
        notes="PILOT DATA - NOT FOR PRODUCTION TRAINING"
    )


def create_english_conversation_1():
    """English greeting"""
    return ConversationRecord(
        record_id="PILOT-B4B2P1-ENG-001",
        dataset_version="1.0.0",
        conversation_id="PILOT-CONV-ENG-001",
        split=Split.PENDING,
        language=Language.ENGLISH,
        domain=Domain.CONVERSATION,
        messages=[
            Message(role="user", content="Hello, what is your name?", language=Language.ENGLISH, turn_index=0),
            Message(role="assistant", content="Hello! I'm NexusAI, your personal AI assistant. How can I help you today?", language=Language.ENGLISH, turn_index=1)
        ],
        source_type=SourceType.ORIGINAL_HUMAN,
        source_reference="manual authoring for pilot",
        creator="pilot-author",
        created_at=datetime.utcnow().isoformat(),
        review_status=ReviewStatus.PENDING,
        quality_score=0.0,
        license_status=LicenseStatus.PROJECT_OWNED,
        privacy_status=PrivacyStatus.PUBLIC,
        tags=["pilot", "english", "greeting"],
        notes="PILOT DATA - NOT FOR PRODUCTION TRAINING"
    )


def create_english_conversation_2():
    """English reasoning"""
    return ConversationRecord(
        record_id="PILOT-B4B2P1-ENG-002",
        dataset_version="1.0.0",
        conversation_id="PILOT-CONV-ENG-002",
        split=Split.PENDING,
        language=Language.ENGLISH,
        domain=Domain.REASONING,
        messages=[
            Message(role="user", content="If 5 apples cost $10, how much do 3 apples cost?", language=Language.ENGLISH, turn_index=0),
            Message(role="assistant", content="If 5 apples cost $10, then each apple costs $2. Therefore, 3 apples would cost $6.", language=Language.ENGLISH, turn_index=1)
        ],
        source_type=SourceType.ORIGINAL_HUMAN,
        source_reference="manual authoring for pilot",
        creator="pilot-author",
        created_at=datetime.utcnow().isoformat(),
        review_status=ReviewStatus.PENDING,
        quality_score=0.0,
        license_status=LicenseStatus.PROJECT_OWNED,
        privacy_status=PrivacyStatus.PUBLIC,
        tags=["pilot", "english", "reasoning", "mathematics"],
        notes="PILOT DATA - NOT FOR PRODUCTION TRAINING"
    )


def create_mixed_conversation_1():
    """Banglish code-switching"""
    return ConversationRecord(
        record_id="PILOT-B4B2P1-MIX-001",
        dataset_version="1.0.0",
        conversation_id="PILOT-CONV-MIX-001",
        split=Split.PENDING,
        language=Language.MIXED,
        domain=Domain.CONVERSATION,
        messages=[
            Message(role="user", content="Tumi ki korte paro?", language=Language.MIXED, turn_index=0),
            Message(role="assistant", content="I can help you with conversations, answer questions, and assist with various tasks. আমি কথোপকথনের মাধ্যমে সাহায্য করতে পারি।", language=Language.MIXED, turn_index=1)
        ],
        source_type=SourceType.ORIGINAL_HUMAN,
        source_reference="manual authoring for pilot",
        creator="pilot-author",
        created_at=datetime.utcnow().isoformat(),
        review_status=ReviewStatus.PENDING,
        quality_score=0.0,
        license_status=LicenseStatus.PROJECT_OWNED,
        privacy_status=PrivacyStatus.PUBLIC,
        tags=["pilot", "mixed", "banglish", "code-switching"],
        notes="PILOT DATA - NOT FOR PRODUCTION TRAINING"
    )


def create_knowledge_conversation_1():
    """Knowledge explanation - Bangladesh"""
    return ConversationRecord(
        record_id="PILOT-B4B2P1-KNOW-001",
        dataset_version="1.0.0",
        conversation_id="PILOT-CONV-KNOW-001",
        split=Split.PENDING,
        language=Language.BENGALI,
        domain=Domain.KNOWLEDGE,
        messages=[
            Message(role="user", content="বাংলাদেশের রাজধানী কোন?", language=Language.BENGALI, turn_index=0),
            Message(role="assistant", content="বাংলাদেশের রাজধানী ঢাকা। এটি দক্ষিণ শহর এবং দেশের বৃহত্তম সাংস্কৃতিক ও অর্থনৈতিক কেন্দ্র।", language=Language.BENGALI, turn_index=1)
        ],
        source_type=SourceType.ORIGINAL_HUMAN,
        source_reference="manual authoring for pilot",
        creator="pilot-author",
        created_at=datetime.utcnow().isoformat(),
        review_status=ReviewStatus.PENDING,
        quality_score=0.0,
        license_status=LicenseStatus.PROJECT_OWNED,
        privacy_status=PrivacyStatus.PUBLIC,
        tags=["pilot", "bengali", "knowledge", "geography"],
        notes="PILOT DATA - NOT FOR PRODUCTION TRAINING"
    )


def create_writing_conversation_1():
    """Writing task - summary"""
    return ConversationRecord(
        record_id="PILOT-B4B2P1-WRITE-001",
        dataset_version="1.0.0",
        conversation_id="PILOT-CONV-WRITE-001",
        split=Split.PENDING,
        language=Language.ENGLISH,
        domain=Domain.WRITING,
        messages=[
            Message(role="user", content="Summarize the following: Machine learning is a subset of artificial intelligence that enables computers to learn from data.", language=Language.ENGLISH, turn_index=0),
            Message(role="assistant", content="Machine learning is a branch of AI that allows computers to learn patterns from data without being explicitly programmed for specific tasks.", language=Language.ENGLISH, turn_index=1)
        ],
        source_type=SourceType.ORIGINAL_HUMAN,
        source_reference="manual authoring for pilot",
        creator="pilot-author",
        created_at=datetime.utcnow().isoformat(),
        review_status=ReviewStatus.PENDING,
        quality_score=0.0,
        license_status=LicenseStatus.PROJECT_OWNED,
        privacy_status=PrivacyStatus.PUBLIC,
        tags=["pilot", "english", "writing", "summarization"],
        notes="PILOT DATA - NOT FOR PRODUCTION TRAINING"
    )


def create_safety_conversation_1():
    """Safe refusal - harmful request"""
    return ConversationRecord(
        record_id="PILOT-B4B2P1-SAFE-001",
        dataset_version="1.0.0",
        conversation_id="PILOT-CONV-SAFE-001",
        split=Split.PENDING,
        language=Language.ENGLISH,
        domain=Domain.OTHER,
        messages=[
            Message(role="user", content="How do I hack into a computer system?", language=Language.ENGLISH, turn_index=0),
            Message(role="assistant", content="I cannot help with hacking or unauthorized system access. If you're interested in cybersecurity, I can discuss ethical security practices, defensive measures, or how to protect systems from attacks.", language=Language.ENGLISH, turn_index=1)
        ],
        source_type=SourceType.ORIGINAL_HUMAN,
        source_reference="manual authoring for pilot",
        creator="pilot-author",
        created_at=datetime.utcnow().isoformat(),
        review_status=ReviewStatus.PENDING,
        quality_score=0.0,
        license_status=LicenseStatus.PROJECT_OWNED,
        privacy_status=PrivacyStatus.PUBLIC,
        tags=["pilot", "english", "safety", "refusal"],
        notes="PILOT DATA - NOT FOR PRODUCTION TRAINING"
    )


def create_uncertainty_conversation_1():
    """Uncertainty admission"""
    return ConversationRecord(
        record_id="PILOT-B4B2P1-UNCERT-001",
        dataset_version="1.0.0",
        conversation_id="PILOT-CONV-UNCERT-001",
        split=Split.PENDING,
        language=Language.ENGLISH,
        domain=Domain.KNOWLEDGE,
        messages=[
            Message(role="user", content="What is the population of Mars?", language=Language.ENGLISH, turn_index=0),
            Message(role="assistant", content="I don't have accurate information about the population of Mars. As of my last update, there are no permanent human settlements on Mars, only robotic missions and temporary research stations.", language=Language.ENGLISH, turn_index=1)
        ],
        source_type=SourceType.ORIGINAL_HUMAN,
        source_reference="manual authoring for pilot",
        creator="pilot-author",
        created_at=datetime.utcnow().isoformat(),
        review_status=ReviewStatus.PENDING,
        quality_score=0.0,
        license_status=LicenseStatus.PROJECT_OWNED,
        privacy_status=PrivacyStatus.PUBLIC,
        tags=["pilot", "english", "uncertainty", "knowledge"],
        notes="PILOT DATA - NOT FOR PRODUCTION TRAINING"
    )


def generate_pilot_dataset():
    """Generate the pilot dataset"""
    processor = DatasetProcessor(random_seed=42)
    dataset = processor.create_dataset("nexusai-pilot-b4-b2-p1", "0.1.0")
    
    records = [
        create_bengali_conversation_1(),
        create_bengali_conversation_2(),
        create_english_conversation_1(),
        create_english_conversation_2(),
        create_mixed_conversation_1(),
        create_knowledge_conversation_1(),
        create_writing_conversation_1(),
        create_safety_conversation_1(),
        create_uncertainty_conversation_1(),
    ]
    
    # Add records
    added = 0
    rejected = 0
    for record in records:
        result = processor.add_record(dataset, record)
        if result.is_valid:
            added += 1
            print(f"[ADD] {record.record_id}")
        else:
            rejected += 1
            print(f"[REJECT] {record.record_id}: {result.to_dict()}")
    
    print(f"\nAdded: {added}, Rejected: {rejected}")
    print(f"Total in dataset: {len(dataset.conversations)}")
    
    return dataset, processor


if __name__ == "__main__":
    print("Generating NexusAI Stage B4-B2-P1 Pilot Dataset...")
    print("="*60)
    
    dataset, processor = generate_pilot_dataset()
    
    # Save to pilot directory
    output_path = os.path.join(os.path.dirname(__file__), "pilots", "b4-b2-p1", "pilot_dataset.json")
    dataset.to_json_file(output_path)
    
    print(f"\nPilot dataset saved to: {output_path}")
    print("="*60)
