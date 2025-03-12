# OE10 Pan/Tilt Unit Command Decoder

This project provides tools to decode and generate commands for the OE10 pan/tilt unit. It includes analysis of serial communication patterns and command generation capabilities.

## How It Works

### Command Protocol
The OE10 pan/tilt unit uses a serial protocol with the following characteristics:
- Commands start with a marker byte (0x58 for TX, 0x98 for RX)
- Regular sync bytes are used (0x8B for TX, 0x16 for RX)
- Commands end with 0x00
- Both commands and responses include framing errors at start/end

### Script Components

1. **Command Generation (`oe10_commander.py`)**
   - Generates properly formatted command sequences
   - Handles serial communication with the device
   - Provides both simulation and hardware modes
   - Example: `python3 src/oe10_commander.py --simulate --angle 10`

2. **Protocol Decoder (`decoder.py`)**
   - Decodes incoming messages from the device
   - Extracts position feedback and status information
   - Handles sync byte patterns and error detection

3. **Data Analysis (`utils.py`)**
   - Parses logic analyzer captures
   - Identifies command sequences
   - Compares TX/RX patterns
   - Helps analyze timing relationships

### Data Flow
1. Command Generation:
   ```
   User Input → Command Generation → Serial TX → Device → Serial RX → Response Decoding
   ```

2. Capture Analysis:
   ```
   Logic Analyzer Files → Parse Data → Find Sequences → Extract Patterns → Analysis Results
   ```

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
        ├── 2025-03-12_13-26-50 tilt 10 rx.txt     # Response to 10° tilt
        ├── 2025-03-12_13-27-46 tilt 10 tx.txt     # 10° tilt command
        ├── 2025-03-12_13-29-10 nothing rx.txt     # Idle response
        └── 2025-03-12_13-29-10 nothing tx.txt     # No command
```

## Features

- Decode OE10 pan/tilt unit serial commands
- Generate valid command sequences
- Support for movement commands (pan/tilt)
- Analysis of command patterns
- Simulation mode for testing without hardware
- Real hardware control via serial port

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command Generation
```bash
# Simulate a tilt command (safe testing without hardware)
python3 src/oe10_commander.py --simulate --angle 10

# Send command to actual device
python3 src/oe10_commander.py --port /dev/ttyUSB0 --angle 10

# Specify different baud rate (if needed)
python3 src/oe10_commander.py --port /dev/ttyUSB0 --angle 10 --baudrate 19200
```

### Data Analysis
The `data/raw_captures` directory contains logic analyzer captures of the serial communication:
- TX files: Commands sent to the device
- RX files: Responses received from the device
- Captures are timestamped and labeled with the command type
- Analysis scripts can process these files to understand the protocol

### Protocol Details
The serial communication protocol uses:
- Hex-encoded commands with specific start/end markers
- Regular sync bytes for message framing
- Position feedback in device responses
- Error detection through framing errors
- Consistent timing patterns

Complete protocol documentation is available in `docs/tilt_command_protocol.md`

## Development

### Adding New Commands
1. Study the command pattern in logic analyzer captures
2. Add command generation function to `oe10_commander.py`
3. Update decoder to handle new response patterns
4. Document the new command in the protocol documentation

### Testing
- Use simulation mode for initial testing
- Verify timing with logic analyzer
- Compare generated commands with captured patterns
- Run unit tests: `python -m pytest tests/`

## License

MIT License

Copyright (c) 2025 Axel Schmidt

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to:

1. Update tests as appropriate
2. Follow the existing code style
3. Document new code using docstrings and comments
4. Update the README if needed

### Development Process

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code of Conduct

- Be respectful of others
- Use inclusive language
- Accept constructive criticism
- Focus on what is best for the community

For questions or concerns, please contact the maintainers.