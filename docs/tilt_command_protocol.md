# OE10 Pan/Tilt Unit - Tilt Command Protocol

## Command Structure (TX)

The tilt command consists of 15 bytes sent to the device:

```
Start Marker | Sync Bytes & Data                                          | End
0x58         | 0x8B 0xFD 0x8B 0xF9 0x8B 0x59 0x57 0x8B 0x8B 0xF3 0x8B 0x71 0x83 | 0x00
```

### Breakdown:
- **Start Marker**: `0x58` (with framing error)
- **Sync Byte**: `0x8B` (appears 6 times throughout the message)
- **Data Bytes**: `0xFD 0xF9 0x59 0x57 0xF3 0x71 0x83`
- **End Marker**: `0x00` (with framing error)
- **Duration**: ~15.3ms (0.0153 seconds)

## Response Structure (RX)

The device responds with a 25-byte message:

```
Start Marker | Sync Bytes & Data                                                                                              | End
0x98         | 0x16 0xF2 0x16 0xCA 0x16 0xE6 0x16 0xB2 0xAE 0x9E 0xFE 0xFE 0x3E 0x3A 0x3E 0x3E 0x3E 0x3E 0x16 0xA2 0x16 0xE2 0x06 | 0x00
```

### Breakdown:
- **Start Marker**: `0x98` (with framing error)
- **Sync Byte**: `0x16` (appears 6 times throughout the message)
- **Data Bytes**: `0xF2 0xCA 0xE6 0xB2 0xAE 0x9E 0xFE 0xFE 0x3E 0x3A 0x3E 0x3E 0x3E 0x3E 0xA2 0xE2 0x06`
- **End Marker**: `0x00` (with framing error)
- **Duration**: ~28.1ms (0.0281 seconds)

## Timing
- Response delay: ~20.7ms (0.0207 seconds) between TX start and RX start
- Total transaction time: ~49ms

## Protocol Notes
1. Both TX and RX use framing errors on start and end markers
2. Different sync bytes are used for TX (0x8B) and RX (0x16)
3. Response includes repeated 0x3E bytes which may indicate position feedback
4. Command appears to be acknowledged with a status response

## Serial Configuration
- Baud rate: TBD (needs to be calculated from timing)
- Framing errors suggest possible custom timing or bit patterns 