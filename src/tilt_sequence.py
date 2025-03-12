#!/usr/bin/env python3
import serial
import time
import argparse
from typing import List, Optional

class OE10Controller:
    def __init__(self, port: str, baudrate: int = 9600):
        """Initialize OE10 controller with serial connection parameters."""
        self.serial = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=2,
            rtscts=False,
            dsrdtr=False,
            xonxoff=False
        )
        
        # For 3.3V CMOS levels
        print("Setting RTS/DTR high...")
        self.serial.setRTS(True)
        self.serial.setDTR(True)
        time.sleep(0.1)
        
        # Clear any pending data
        self.serial.reset_input_buffer()
        self.serial.reset_output_buffer()
        
        print("Starting initialization sequence...")
        self._initialize_device()
        
        print(f"Serial port opened: {self.serial.name}")
        print(f"Port settings: {self.serial.get_settings()}")

    def _initialize_device(self):
        """Send the initialization sequence from the capture."""
        # First initialization command
        init_cmd1 = bytes([
            0x58, 0x8B, 0xFD, 0x8B, 0xF9, 0x8B, 0x7D, 0x59,
            0x8B, 0x8B, 0xD9, 0x8B, 0x71, 0x83, 0x00
        ])
        
        # Second initialization command
        init_cmd2 = bytes([
            0x58, 0x8B, 0xFD, 0x8B, 0xF9, 0x8B, 0x59, 0x57,
            0x8B, 0x8B, 0xF3, 0x8B, 0x71, 0x83, 0x00
        ])
        
        print("\n=== Starting Initialization ===")
        print("1. Sending first initialization command...")
        self._send_command_with_timing(init_cmd1)
        response = self._wait_for_response()
        
        print("\n2. Sending second initialization command...")
        self._send_command_with_timing(init_cmd2)
        response = self._wait_for_response()
        print("=== Initialization Complete ===\n")

    def _calculate_checksum(self, data: bytes) -> tuple[int, str]:
        """Calculate checksum and checksum indicator for a command."""
        checksum = 0
        for byte in data:
            checksum ^= byte
        
        # Handle special cases as per protocol
        if checksum == 0x3C:
            return 0xFF, '0'
        elif checksum == 0x3E:
            return 0xFF, '1'
        return checksum, 'G'

    def _create_status_command(self) -> bytes:
        """Create a status polling command based on captured pattern."""
        return bytes([
            0x58, 0x8B, 0xFD, 0x8B, 0xF9, 0x8B, 0x59, 0x57,
            0x8B, 0x8B, 0xF3, 0x8B, 0x71, 0x83, 0x00
        ])

    def _create_tilt_command(self, angle: int) -> bytes:
        """Create a tilt command with the exact pattern from captures."""
        # Movement command has a different pattern
        command = bytes([
            0x58, 0x8B, 0xFD, 0x8B, 0xF3, 0x8B, 0x5F, 0x5F,
            0x8B, 0x9D, 0x8F, 0x9F, 0x8B, 0x85, 0x8B, 0x71,
            0x83, 0x00
        ])
        
        print(f"Command bytes: {' '.join([f'0x{b:02X}' for b in command])}")
        return command

    def _send_command_with_timing(self, command: bytes) -> None:
        """Send command with precise timing from captures."""
        # Clear any pending data
        self.serial.reset_input_buffer()
        self.serial.reset_output_buffer()
        
        print("\nSending command with timing:")
        # Send first byte
        print(f"TX: 0x{command[0]:02X} (Start byte)")
        self.serial.write(bytes([command[0]]))
        self.serial.flush()
        time.sleep(0.0017)  # 1.7ms delay after start byte
        
        # Send remaining bytes with 1ms spacing
        for i, byte in enumerate(command[1:], 1):
            print(f"TX: 0x{byte:02X}")
            self.serial.write(bytes([byte]))
            self.serial.flush()
            time.sleep(0.001)  # 1ms delay between bytes
        print("Command transmission complete")

    def _send_bytes_with_delay(self, data: bytes):
        """Send bytes with small delays for 3.3V CMOS timing."""
        for byte in data:
            self.serial.write(bytes([byte]))
            self.serial.flush()
            time.sleep(0.001)  # 1ms delay between bytes

    def _wait_for_response(self) -> Optional[bytes]:
        """Wait for response with timeout."""
        print("\nWaiting for response...")
        start_time = time.time()
        response = bytearray()
        
        # Wait exactly 15ms before starting to read (from capture timing)
        time.sleep(0.015)
        
        # Read for up to 25ms (response should complete within this time)
        while time.time() - start_time < 0.040:  # 40ms total timeout
            if self.serial.in_waiting:
                byte = self.serial.read()
                if byte:
                    print(f"Time: {time.time() - start_time:.6f}s - Received: 0x{byte[0]:02X}")
                    response.extend(byte)
            time.sleep(0.0001)  # 0.1ms polling interval for faster response
        
        if response:
            print(f"\nComplete response ({len(response)} bytes):")
            print(' '.join([f'0x{b:02X}' for b in response]))
        else:
            print("No response bytes received")
        
        return bytes(response) if response else None

    def move_to_angle(self, angle: int) -> bool:
        """Move to specified angle with continuous polling."""
        try:
            # Start with status polling for 2 seconds to establish communication
            print("\nEstablishing communication...")
            self.run_polling_sequence(2.0)
            
            # Send the movement command
            command = self._create_tilt_command(angle)
            print(f"\nSending tilt command for {angle}°...")
            self._send_command_with_timing(command)
            
            # Wait for response
            response = self._wait_for_response()
            if not response:
                print(f"No response received for angle {angle}")
                return False
            
            # Continue polling for 2 more seconds after movement
            print("\nContinuing communication...")
            self.run_polling_sequence(2.0)
            
            return True
        
        except Exception as e:
            print(f"Error moving to angle {angle}: {str(e)}")
            return False

    def run_polling_sequence(self, duration: float = 5.0):
        """Run a continuous polling sequence for the specified duration."""
        try:
            start_time = time.time()
            last_cmd_time = 0
            print("\nStarting continuous polling sequence...")
            
            while time.time() - start_time < duration:
                current_time = time.time()
                
                # Ensure exactly 1 second between commands
                if current_time - last_cmd_time >= 1.0 or last_cmd_time == 0:
                    # Send status command
                    cmd = self._create_status_command()
                    self._send_command_with_timing(cmd)
                    last_cmd_time = time.time()
                    
                    # Wait for response
                    response = self._wait_for_response()
                    
                    if response:
                        print(f"Response received at {time.time() - start_time:.6f}s")
                
                # Small sleep to prevent CPU spinning
                time.sleep(0.001)
            
            print("\nPolling sequence completed.")
            
        except Exception as e:
            print(f"Error in polling sequence: {str(e)}")

    def close(self):
        """Close the serial connection."""
        if self.serial.is_open:
            self.serial.close()
            print("Serial port closed")

def main():
    parser = argparse.ArgumentParser(description='Control OE10 tilt sequence')
    parser.add_argument('--port', required=True, help='Serial port (e.g., /dev/ttyUSB0)')
    parser.add_argument('--baudrate', type=int, default=9600, help='Baud rate')
    parser.add_argument('--poll', action='store_true', help='Run polling sequence')
    parser.add_argument('--duration', type=float, default=5.0, help='Polling duration in seconds')
    args = parser.parse_args()

    print(f"\nInitializing OE10 controller on {args.port} at {args.baudrate} baud")
    controller = OE10Controller(args.port, args.baudrate)
    
    try:
        if args.poll:
            print("\nRunning polling sequence...")
            controller.run_polling_sequence(args.duration)
        else:
            print("\nStarting tilt sequence...")
            
            # Move to 10 degrees
            print("\nPhase 1: Moving to 10°...")
            if controller.move_to_angle(10):
                print("Successfully moved to 10°")
            else:
                print("Failed to move to 10°")
            
            # Wait for movement to complete
            print("\nWaiting for movement to complete...")
            time.sleep(2)
            
            # Move back to 0 degrees
            print("\nPhase 2: Moving back to 0°...")
            if controller.move_to_angle(0):
                print("Successfully moved to 0°")
            else:
                print("Failed to move to 0°")
                
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        controller.close()

if __name__ == "__main__":
    main() 