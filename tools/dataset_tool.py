"""
tools/dataset_tool.py - Dataset inspection tools for Agent01.

Provides pure Python functions to read and count records in CSV datasets.
Uses only standard Python libraries (os, csv) without external dependencies.
"""

import os
import csv
from typing import List, Dict, Any


def read_dataset(file_path: str = "data/sample_employees.csv") -> List[Dict[str, Any]]:
    """
    Reads a CSV dataset and returns all rows as a list of dictionaries.

    Args:
        file_path: Relative or absolute path to the CSV file.

    Returns:
        List of dictionaries where keys are header column names.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        ValueError: If the file is empty or missing headers.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset file not found at '{file_path}'")

    records = []
    with open(file_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError(f"Dataset '{file_path}' has no header columns or is empty.")
        for row in reader:
            records.append(dict(row))

    return records


def count_records(file_path: str = "data/sample_employees.csv") -> int:
    """
    Counts the number of data rows in a CSV dataset (excluding header).

    Args:
        file_path: Relative or absolute path to the CSV file.

    Returns:
        The total number of records (rows) found in the dataset.

    Raises:
        FileNotFoundError: If the specified file does not exist.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset file not found at '{file_path}'")

    with open(file_path, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header is None:
            return 0
        count = sum(1 for _ in reader)

    return count
