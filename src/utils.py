#!/usr/bin/env python3
"""
Utility functions for OE10 command processing
"""

import csv
from typing import List, Dict, Generator
from pathlib import Path

def read_logic_analyzer_log(file_path: str) -> Generator[Dict, None, None]:
    """
    Read and parse a logic analyzer log file
    
    Args:
        file_path: Path to the log file
        
    Yields:
        Dict containing parsed line data
    """
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield {
                'timestamp': float(row['Time [s]']),
                'value': int(row['Value'].replace('0x', ''), 16),
                'parity_error': bool(row.get('Parity Error')),
                'framing_error': bool(row.get('Framing Error', '').strip())
            }

def find_command_sequences(data: List[Dict]) -> List[List[Dict]]:
    """
    Find complete command sequences in the data
    
    Args:
        data: List of parsed log entries
        
    Returns:
        List of command sequences
    """
    sequences = []
    current_sequence = []
    
    for entry in data:
        # Start markers: 0x98 for RX, 0x58 for TX
        if entry['value'] in [0x98, 0x58]:
            if current_sequence:
                sequences.append(current_sequence)
            current_sequence = [entry]
        elif current_sequence:
            current_sequence.append(entry)
            # End marker is always 0x00
            if entry['value'] == 0x00:
                sequences.append(current_sequence)
                current_sequence = []
    
    if current_sequence:
        sequences.append(current_sequence)
    
    # Filter out incomplete sequences
    valid_sequences = []
    for seq in sequences:
        if seq and seq[-1]['value'] == 0x00:
            valid_sequences.append(seq)
    
    return valid_sequences

def compare_sequences(seq1: List[Dict], seq2: List[Dict]) -> Dict:
    """
    Compare two command sequences to find differences
    
    Args:
        seq1: First command sequence
        seq2: Second command sequence
        
    Returns:
        Dictionary containing analysis of differences
    """
    return {
        'length_diff': len(seq2) - len(seq1),
        'different_bytes': [
            (i, s1['value'], s2['value'])
            for i, (s1, s2) in enumerate(zip(seq1, seq2))
            if s1['value'] != s2['value']
        ],
        'timing_diff': seq2[0]['timestamp'] - seq1[0]['timestamp']
    } 