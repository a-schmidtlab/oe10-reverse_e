#!/usr/bin/env python3
"""
Script to analyze OE10 command samples and identify patterns
"""

from decoder import OE10Decoder
from utils import read_logic_analyzer_log, find_command_sequences, compare_sequences
from pathlib import Path
import sys
import os

def analyze_file(file_path: str, label: str = "") -> list:
    """Analyze a single log file and return its command sequences"""
    print(f"\nAnalyzing {label} file: {file_path}")
    print("-" * 50)
    
    # Read and parse the file
    data = list(read_logic_analyzer_log(file_path))
    sequences = find_command_sequences(data)
    
    print(f"Found {len(sequences)} sequences")
    
    # Print first sequence
    if sequences:
        seq = sequences[0]  # Take first sequence as example
        print(f"\nFirst Sequence:")
        print("Timestamp | Value  | Errors")
        print("-" * 40)
        for entry in seq:
            errors = []
            if entry.get('parity_error'):
                errors.append('P')
            if entry.get('framing_error'):
                errors.append('F')
            error_str = ','.join(errors) if errors else ''
            print(f"{entry['timestamp']:.4f} | 0x{entry['value']:02X} | {error_str}")
    
    return sequences

def analyze_sequence(seq: list, title: str = "Sequence Analysis"):
    """Analyze a single command sequence"""
    print(f"\n{title}:")
    print("-" * 50)
    
    # Identify key parts of the sequence
    start_marker = next((x for x in seq if x['value'] in [0x98, 0x58]), None)
    end_marker = next((x for x in seq if x['value'] == 0x00), None)
    sync_bytes = [x for x in seq if x['value'] in [0x16, 0x8B]]  # Different sync bytes for TX/RX
    
    print(f"Start marker: 0x{start_marker['value']:02X} at {start_marker['timestamp']:.4f}s")
    print(f"Number of sync/repeat bytes: {len(sync_bytes)}")
    print(f"End marker: 0x{end_marker['value']:02X} at {end_marker['timestamp']:.4f}s")
    print(f"Sequence length: {len(seq)} bytes")
    print(f"Duration: {end_marker['timestamp'] - start_marker['timestamp']:.4f}s")
    
    # Look for patterns in the data portion
    data_bytes = [x['value'] for x in seq if x['value'] not in [0x98, 0x58, 0x16, 0x8B, 0x00]]
    print("\nData bytes (excluding markers/sync):")
    print(' '.join(f"0x{x:02X}" for x in data_bytes))
    
    return {
        'data_bytes': data_bytes,
        'sync_count': len(sync_bytes),
        'sequence_length': len(seq),
        'start_time': start_marker['timestamp'],
        'end_time': end_marker['timestamp'],
        'duration': end_marker['timestamp'] - start_marker['timestamp']
    }

def analyze_tx_rx_pair(tx_file: str, rx_file: str):
    """Analyze a pair of TX and RX files"""
    print("\nAnalyzing TX-RX Pair")
    print("=" * 50)
    
    # Analyze both files
    tx_sequences = analyze_file(tx_file, "TX")
    rx_sequences = analyze_file(rx_file, "RX")
    
    if tx_sequences and rx_sequences:
        tx_analysis = analyze_sequence(tx_sequences[0], "TX Command Analysis")
        rx_analysis = analyze_sequence(rx_sequences[0], "RX Response Analysis")
        
        # Compare sequences
        print("\nTX-RX Comparison:")
        print("-" * 50)
        print(f"TX sequence length: {tx_analysis['sequence_length']} bytes")
        print(f"RX sequence length: {rx_analysis['sequence_length']} bytes")
        print(f"TX duration: {tx_analysis['duration']:.4f}s")
        print(f"RX duration: {rx_analysis['duration']:.4f}s")
        
        # Calculate response delay
        response_delay = rx_analysis['start_time'] - tx_analysis['start_time']
        print(f"\nResponse delay: {response_delay:.4f}s")
        
        # Compare data patterns
        print("\nData pattern comparison:")
        tx_data = tx_analysis['data_bytes']
        rx_data = rx_analysis['data_bytes']
        
        print("\nTX data pattern:")
        print(' '.join(f"0x{x:02X}" for x in tx_data))
        print("\nRX data pattern:")
        print(' '.join(f"0x{x:02X}" for x in rx_data))

def main():
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data" / "samples"
    
    # Analyze tilt command pair
    tx_file = data_dir / "2025-03-12_13-27-46 tilt 10 tx.txt"
    rx_file = data_dir / "2025-03-12_13-26-50 tilt 10 rx.txt"
    
    analyze_tx_rx_pair(str(tx_file), str(rx_file))

if __name__ == "__main__":
    main() 