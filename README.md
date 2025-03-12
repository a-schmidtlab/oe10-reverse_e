# OE10 Tilt Controller Protocol Analysis and experimental Implementation

## Overview

This project provides an experiment for controlling and analyzing the OE10 pan/tilt unit's communication protocol. It includes an analysis tools for understanding the protocol and an implementation code for controlling the device.

### Key Components

1. **Protocol Analysis Tools**
   - Logic analyzer data processing
   - Command pattern identification
   - Timing analysis and verification
   - Response pattern matching

2. **Control Implementation**
   - Real-time command generation
   - Serial communication handling
   - Response processing
   - State management

3. **Development Tools**
   - Protocol simulation
   - Command validation
   - Timing verification
   - Hardware interface testing

### Core Features

- **Protocol Reverse Engineering**
  - Binary protocol analysis
  - Timing characteristics measurement
  - Command structure identification
  - Response pattern analysis

- **Hardware Communication**
  - Serial port management
  - Hardware flow control handling
  - Voltage level verification
  - Timing-accurate transmission

- **Command Generation**
  - Status queries
  - Initialization sequences
  - Movement commands
  - Error handling

## Project Structure

```
oe10-reverse_e/
├── README.md
├── requirements.txt
├── src/
│   ├── decoder.py         # Command decoder implementation
│   ├── encoder.py         # Command encoder/generator
│   ├── utils.py           # Utility functions for data handling
│   └── oe10_commander.py  # Main command generation script
├── tests/
│   └── test_decoder.py    # Unit tests
├── docs/
│   └── tilt_command_protocol.md  # Protocol documentation
└── data/
    └── raw_captures/      # Raw logic analyzer captures
        ├── Command Captures/
        │   ├── 2025-03-12_13-26-50 tilt 10 rx.txt     # Response to 10° tilt
        │   ├── 2025-03-12_13-27-46 tilt 10 tx.txt     # 10° tilt command
        │   ├── 2025-03-12_13-29-10 nothing rx.txt     # Idle response
        │   └── 2025-03-12_13-29-10 nothing tx.txt     # No command
        └── Protocol Analysis/
            ├── 2025-03-12_15-16-23 TX.csv             # Detailed TX timing analysis
            └── 2025-03-12_15-17-12 RX.csv             # Detailed RX timing analysis
```

## Protocol Analysis

### Command Types and Patterns

1. **Status Query Command** (15 bytes)
```
TX: 58 8B FD 8B F9 8B 7D 59 8B 8B D9 8B 71 83 00
RX: 98 16 F2 16 C6 16 E6 16 FA B2 76 76 32 2A 1A 32 2A 1A 3A 3A 16 9E 16 E2 06 00
```

2. **Initialization Command** (15 bytes)
```
TX: 58 8B FD 8B F9 8B 59 57 8B 8B F3 8B 71 83 00
RX: 98 16 F2 16 CA 16 E6 16 B2 AE 9E FE FE 32 2A 1A 32 2A 1A 16 A6 16 E2 06 00
```

3. **Movement Command** (18 bytes)
```
TX: 58 8B FD 8B F3 8B 5F 5F 8B 9D 8F 9F 8B 85 8B 71 83 00
RX: 98 16 F2 16 E2 16 E6 16 BE BE 3A 1E 3E 16 16 16 E2 06 00
```

### Command Structure

#### TX (Command) Pattern
- Start marker: 0x58
- Sync byte: 0x8B (repeated throughout)
- End sequence: 0x71 0x83 0x00
- Framing errors at start (0x58) and end (0x00)

#### RX (Response) Pattern
- Start marker: 0x98 (mirror of TX 0x58)
- Sync byte: 0x16 (mirror of TX 0x8B)
- End sequence: 0xE2 0x06 0x00
- Framing errors at specific positions

### Timing Characteristics

1. **Command Transmission**
   - 1.7ms delay after start byte
   - 1ms between subsequent bytes
   - Total command transmission: ~16-18ms

2. **Response Timing**
   - Command to response delay: 36-39ms
   - Response transmission time: ~25ms
   - Total cycle time: 60-65ms

3. **Command Sequence**
   - Status queries sent every ~1 second during normal operation
   - Movement commands interrupt the normal polling sequence
   - Return to status polling after movement completion

### Protocol Operation

1. **Initialization Sequence**
   - Initial status query
   - Initialization command
   - Verification response
   - Begin regular status polling

2. **Movement Operation**
   - Status query before movement
   - Movement command
   - Modified response pattern
   - Resume status polling

### Implementation Notes

1. **Command Framing**
   - All commands start with 0x58
   - All responses start with 0x98
   - Consistent sync byte patterns (0x8B/0x16)
   - Fixed end sequences

2. **Error Detection**
   - Intentional framing errors at specific positions
   - Response validation through sync bytes
   - Status feedback in response data

3. **Timing Requirements**
   - Precise byte timing during transmission
   - Specific delays between command and response
   - Regular polling interval maintenance

## Implementation Details

### Software Architecture

1. **Command Layer**
   - Command generation and validation
   - Byte sequence construction
   - Timing control
   - Error detection

2. **Communication Layer**
   - Serial port management
   - Hardware flow control
   - Buffer handling
   - Response timeout management

3. **Analysis Layer**
   - Pattern recognition
   - Timing measurement
   - Response validation
   - State tracking

### Script Components

1. **oe10_commander.py**
   ```python
   class OE10Commander:
       def __init__(self, port, baudrate=9600):
           self.port = port
           self.baudrate = baudrate
           self.initialize_connection()

       def send_command(self, command_type, params=None):
           # Command generation and sending
           pass

       def wait_for_response(self, timeout=100):
           # Response handling with timeout
           pass
   ```

2. **decoder.py**
   ```python
   class OE10Decoder:
       def decode_response(self, response_bytes):
           # Response pattern matching and decoding
           pass

       def validate_checksum(self, data):
           # Checksum validation
           pass
   ```

3. **utils.py**
   ```python
   class ProtocolAnalyzer:
       def analyze_timing(self, capture_data):
           # Timing analysis
           pass

       def extract_patterns(self, data_stream):
           # Pattern extraction
           pass
   ```

## Troubleshooting History and Current Status

### Protocol Implementation Attempts

1. **Initial ASCII Protocol Implementation**
   - Implemented documented ASCII protocol
   - Used standard command format: `<to:from:length:command:data:checksum:checksum_ind>`
   - No response from device
   - Concluded: Device uses binary protocol instead of ASCII

2. **Binary Protocol - First Attempt**
   - Captured "nothing" command sequence
   - Implemented exact byte pattern: `58 8B FD 8B F9 8B 7D 59 8B 8B D9 8B 71 83 00`
   - Added proper timing (1.7ms after start, 1ms between bytes)
   - Result: Commands sent successfully but no response received

3. **Timing Refinements**
   - Added 36-39ms wait for response
   - Implemented continuous polling (1-second interval)
   - Verified command transmission with logic analyzer
   - Result: Commands transmitted correctly, timing verified, still no response

4. **Hardware Flow Control Investigation**
   - Disabled hardware flow control
   - Set RTS/DTR lines high
   - Verified 3.3V CMOS levels
   - Result: Proper voltage levels confirmed, still no response

5. **Command Pattern Variations**
   - Implemented both initialization sequences
   - Added movement command pattern
   - Verified exact byte patterns with original captures
   - Result: All patterns match original software, no response

### Current Implementation Status

1. **What's Working**
   - Command transmission timing (verified with logic analyzer)
   - Proper voltage levels (3.3V CMOS)
   - Exact byte patterns matching original software
   - Framing error generation at correct positions

2. **What's Not Working**
   - No response received from device
   - No LED activity on commands
   - No movement when sending tilt commands

3. **Verified Hardware Conditions**
   - Power supply: Confirmed
   - Serial connection: Verified
   - Voltage levels: Correct
   - Cable connections: Proper

### Analysis of Non-Response

Given that the hardware setup is correct and verified, the lack of response likely stems from one of these protocol-level issues:

1. **Initialization Sequence**
   - Device might require a specific sequence of commands before accepting movement commands
   - Current sequence might be missing a crucial step between initialization and movement

2. **Timing Sensitivity**
   - Although we match the observed timing, there might be additional timing requirements
   - Device might require precise gaps between initialization and first command

3. **State Management**
   - Device might need to be in a specific state to accept commands
   - Current implementation might not be properly transitioning the device through its states

4. **Command Validation**
   - Device might have additional validation requirements beyond the observed pattern
   - Some bytes in the command sequence might serve as validation that we haven't identified

### Next Steps

1. **Protocol Analysis**
   - Capture and analyze more initialization sequences
   - Look for patterns in the timing between command sequences
   - Analyze relationship between command types and device states

2. **Implementation Refinement**
   - Try variations in initialization timing
   - Implement different command sequences
   - Add more detailed response timeout handling

3. **Validation Requirements**
   - Investigate possible checksum patterns
   - Look for state indicators in command sequences
   - Analyze byte patterns for hidden validation mechanisms



### Usage

1. **Port Configuration**
   - Baud rate: 9600
   - Data bits: 8
   - Parity: None
   - Stop bits: 1
   - Flow control: None

2. **Command Examples**
   ```bash
   # Simulate a tilt command (safe testing without hardware)
   python3 src/oe10_commander.py --simulate --angle 10

   # Send command to actual device
   python3 src/oe10_commander.py --port /dev/ttyUSB0 --angle 10

   # Specify different baud rate (if needed)
   python3 src/oe10_commander.py --port /dev/ttyUSB0 --angle 10 --baudrate 19200
   ```

3. **Data Analysis**
   - Use raw_captures directory for protocol analysis
   - Run timing analysis with provided tools
   - Verify command patterns against captures
   - Monitor responses with logic analyzer



## Protocol Verification

### Command Validation

1. **Structure Verification**
   - Start marker (0x58)
   - Sync bytes (0x8B)
   - Command body
   - End sequence

2. **Timing Verification**
   - Start byte delay (1.7ms)
   - Inter-byte timing (1ms)
   - Response wait time (36-39ms)
   - Total cycle time

3. **Response Validation**
   - Start marker (0x98)
   - Sync bytes (0x16)
   - Status data
   - End sequence

## Contact

 (c) 2025 Axel Schmidt
