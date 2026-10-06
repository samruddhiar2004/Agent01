"""
tools/file_tool.py - File inspection and verification tools for Agent01.

Provides tools for the agent to check file existence, inspect size, and verify
that generated artifacts (such as Excel reports) exist on disk.
"""

import os
from typing import Dict, Any


def check_file_exists(file_path: str) -> bool:
    """
    Checks if a file exists on the filesystem.

    Args:
        file_path: Relative or absolute path to check.

    Returns:
        True if the file exists and is a regular file; False otherwise.
    """
    return os.path.isfile(file_path)


def get_file_info(file_path: str) -> Dict[str, Any]:
    """
    Retrieves file metadata to verify generated output files.

    Args:
        file_path: Path to the target file.

    Returns:
        Dictionary with file existence status, file size in bytes, and path.
    """
    if not os.path.exists(file_path):
        return {
            "exists": False,
            "path": file_path,
            "size_bytes": 0,
            "message": f"File '{file_path}' does not exist."
        }

    stat = os.stat(file_path)
    return {
        "exists": True,
        "path": file_path,
        "size_bytes": stat.st_size,
        "message": f"File exists with size {stat.st_size} bytes."
    }
