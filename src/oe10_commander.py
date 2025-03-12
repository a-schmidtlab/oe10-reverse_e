#!/usr/bin/env python3
"""
OE10 Pan/Tilt Unit Command Generator and Decoder
This script can generate tilt commands and decode responses from the OE10 unit.
"""

import serial
import time
from typing import List, Tuple, Optional
import argparse

class OE10Commander:
    # Protocol constants
    TX_START = 0x58
    TX_SYNC = 0x8B
    RX_START = 0x98
    RX_SYNC = 0x16
    END_MARKER = 0x00
    
    def __init__(self, port: str = "/dev/ttyUSB0", baudrate: int = 9600):
        """Initialize the commander with serial port settings"""
        self.port = port
        self.baudrate = baudrate
        self.serial = None
    
    def connect(self):
        """Open the serial connection"""
        self.serial = serial.Serial(
            port=self.port,
            baudrate=self.baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1
        )
    
    def disconnect(self):
        """Close the serial connection"""
        if self.serial and self.serial.is_open:
            self.serial.close()
    
    def generate_tilt_command(self, angle: float) -> bytes:
        """
        Generate a tilt command for the specified angle
        
        Args:
            angle: Tilt angle in degrees
            
        Returns:
            bytes: The command sequence
        """
        # For 10° tilt, we observed this sequence:
        command = [
            self.TX_START,      # Start marker
            self.TX_SYNC, 0xFD, # Sync + Data
            self.TX_SYNC, 0xF9, # Sync + Data
            self.TX_SYNC, 0x59, # Sync + Data
            0x57,               # Data
            self.TX_SYNC,       # Sync
            self.TX_SYNC,       # Sync
            0xF3,               # Data
            self.TX_SYNC,       # Sync
            0x71,               # Data
            0x83,               # Data
            self.END_MARKER     # End marker
        ]
        
        return bytes(command)
    
    def decode_response(self, data: bytes) -> dict:
        """
        Decode a response from the device
        
        Args:
            data: Response bytes from the device
            
        Returns:
            dict: Decoded information from the response
        """
        if not data or len(data) < 3:
            return {'error': 'Response too short'}
            
        if data[0] != self.RX_START or data[-1] != self.END_MARKER:
            return {'error': 'Invalid response markers'}
            
        # Extract data bytes (excluding start, sync bytes, and end marker)
        data_bytes = []
        i = 0
        while i < len(data):
            if data[i] == self.RX_SYNC:
                i += 1  # Skip sync byte
            elif data[i] not in [self.RX_START, self.END_MARKER]:
                data_bytes.append(data[i])
            i += 1
        
        return {
            'start_marker': hex(data[0]),
            'end_marker': hex(data[-1]),
            'data_bytes': [hex(b) for b in data_bytes],
            'position_feedback': [hex(b) for b in data_bytes if b == 0x3E],
            'raw_bytes': [hex(b) for b in data]
        }
    
    def send_tilt_command(self, angle: float) -> Optional[dict]:
        """
        Send a tilt command and read the response
        
        Args:
            angle: Tilt angle in degrees
            
        Returns:
            dict: Decoded response from the device
        """
        if not self.serial or not self.serial.is_open:
            return {'error': 'Serial port not open'}
            
        command = self.generate_tilt_command(angle)
        self.serial.write(command)
        
        # Wait for response (observed delay was ~21ms)
        time.sleep(0.025)
        
        # Read response (expecting 25 bytes)
        response = self.serial.read(25)
        return self.decode_response(response)

def main():
    parser = argparse.ArgumentParser(description='OE10 Pan/Tilt Unit Commander')
    parser.add_argument('--port', default='/dev/ttyUSB0', help='Serial port')
    parser.add_argument('--baudrate', type=int, default=9600, help='Baud rate')
    parser.add_argument('--angle', type=float, default=10.0, help='Tilt angle in degrees')
    parser.add_argument('--simulate', action='store_true', help='Simulate without hardware')
    
    args = parser.parse_args()
    
    commander = OE10Commander(args.port, args.baudrate)
    
    if args.simulate:
        # Demonstrate command generation
        command = commander.generate_tilt_command(args.angle)
        print(f"\nGenerated command for {args.angle}° tilt:")
        print("Bytes:", ' '.join(f"0x{b:02X}" for b in command))
        
        # Simulate a response
        simulated_response = bytes([
            0x98, 0x16, 0xF2, 0x16, 0xCA, 0x16, 0xE6, 0x16,
            0xB2, 0xAE, 0x9E, 0xFE, 0xFE, 0x3E, 0x3A, 0x3E,
            0x3E, 0x3E, 0x3E, 0x16, 0xA2, 0x16, 0xE2, 0x06,
            0x00
        ])
        decoded = commander.decode_response(simulated_response)
        print("\nSimulated response decode:")
        for key, value in decoded.items():
            print(f"{key}: {value}")
    else:
        try:
            commander.connect()
            response = commander.send_tilt_command(args.angle)
            print(f"\nResponse from device:")
            for key, value in response.items():
                print(f"{key}: {value}")
        finally:
            commander.disconnect()

if __name__ == "__main__":
    main() 