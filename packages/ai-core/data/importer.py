"""
Data Import Module

Handles importing data from various formats for training.
Supports: JSON, CSV, TXT
"""

import json
import os
from typing import List, Dict, Any


class DataImporter:
    """Import data from various formats"""
    
    @staticmethod
    def import_json(file_path: str) -> List[str]:
        """
        Import data from JSON file
        
        Expected formats:
        - List of strings: ["text1", "text2", ...]
        - List of Q&A: [{"question": "...", "answer": "..."}, ...]
        - List of conversations: [{"messages": [...]}, ...]
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract text from various formats
        texts = []
        
        if isinstance(data, list):
            for item in data:
                if isinstance(item, str):
                    texts.append(item)
                elif isinstance(item, dict):
                    # Handle Q&A format
                    if 'question' in item and 'answer' in item:
                        texts.append(item['question'])
                        texts.append(item['answer'])
                    # Handle conversation format
                    elif 'messages' in item:
                        for msg in item['messages']:
                            if isinstance(msg, dict) and 'content' in msg:
                                texts.append(msg['content'])
                            elif isinstance(msg, str):
                                texts.append(msg)
        
        return texts
    
    @staticmethod
    def import_csv(file_path: str, text_column: str = 'text') -> List[str]:
        """
        Import data from CSV file
        
        Args:
            file_path: Path to CSV file
            text_column: Name of column containing text data
        """
        import csv
        
        texts = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if text_column in row:
                    texts.append(row[text_column])
        
        return texts
    
    @staticmethod
    def import_txt(file_path: str) -> List[str]:
        """
        Import data from plain text file
        
        Assumes one text sample per line
        """
        texts = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    texts.append(line)
        
        return texts
    
    @staticmethod
    def import_directory(directory: str) -> List[str]:
        """
        Import all supported files from a directory
        
        Searches for: .json, .csv, .txt files
        """
        all_texts = []
        
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            
            if filename.endswith('.json'):
                all_texts.extend(DataImporter.import_json(file_path))
            elif filename.endswith('.csv'):
                all_texts.extend(DataImporter.import_csv(file_path))
            elif filename.endswith('.txt'):
                all_texts.extend(DataImporter.import_txt(file_path))
        
        return all_texts
