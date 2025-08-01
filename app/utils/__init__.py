# Utility functions and helpers

import hashlib
from pathlib import Path
from typing import List, Dict, Any

def calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA-256 hash of a file"""
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def get_existing_file_hashes(data_dir: Path) -> Dict[str, str]:
    """Get hash of all existing files in data directory"""
    existing_hashes = {}
    if data_dir.exists():
        for file_path in data_dir.iterdir():
            if file_path.is_file():
                file_hash = calculate_file_hash(file_path)
                existing_hashes[file_hash] = file_path.name
    return existing_hashes

def is_duplicate_content(file_path: Path, existing_hashes: Dict[str, str]) -> bool:
    """Check if file content is duplicate based on hash"""
    file_hash = calculate_file_hash(file_path)
    return file_hash in existing_hashes 