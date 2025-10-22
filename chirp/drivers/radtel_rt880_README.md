# Radtel RT-880 / iRadio UV-98 Driver

## Status: Experimental - Testing Required

This driver provides initial support for the Radtel RT-880 mobile radio, also sold as the iRadio UV-98.

## Background

The RT-880 driver is based on the existing Radtel RT-900 driver structure, as both radios appear to be part of the same product family. However, this driver has **not been tested with actual RT-880 hardware** and requires verification.

## What Works

- Driver loads successfully in CHIRP
- Inherits communication protocol from RT-900 series
- Supports standard features: channels, tones, power levels, settings
- Registered for both "Radtel RT-880" and "iRadio UV-98" model names

## What Needs Testing

The following parameters are currently set based on RT-900 and need verification with actual hardware:

### 1. Radio Identification
- **Magic String**: `PROGRAMBT80U`
- **Fingerprint 1**: `\x01\x36\x01\x80\x04\x00\x05\x20`
- **Fingerprint 2**: `\x02\x00\x02\x60\x01\x03\x30\x04`

These may be different for RT-880. If connection fails, the radio will return its actual identification strings.

### 2. Memory Configuration
- **Channel Count**: 999 channels
- **Memory Layout**: Inherited from RT-900

The RT-880 may have a different number of channels (commonly 128, 256, 512, or 999).

### 3. Radio Specifications
- **Power Levels**: High (8W), Middle (4W), Low (1W)
- **Frequency Range**: 18-1000 MHz
- **Features**: Bluetooth, noise reduction, per-channel AM

Verify these match the actual RT-880 specifications.

## How to Test

If you have an RT-880 or iRadio UV-98 radio:

1. **Backup Your Radio**: Before testing, save your current radio configuration using the manufacturer's software if available.

2. **Try Download**:
   - Connect your programming cable
   - Start CHIRP and select "Radtel RT-880" or "iRadio UV-98"
   - Attempt to download from radio
   - Note any error messages or identification strings

3. **Report Results**:
   - If successful: Create a test image file and submit it
   - If failed: Report the error and any identification strings shown
   - File an issue on the CHIRP bug tracker with details

4. **Testing Checklist**:
   - [ ] Radio connects and downloads successfully
   - [ ] Channel count is correct
   - [ ] All channels read properly
   - [ ] Settings read properly
   - [ ] Can modify and upload changes
   - [ ] Changes persist after upload
   - [ ] Power levels are accurate
   - [ ] Frequency ranges are correct
   - [ ] All radio features accessible

## Known Information

- **Base Radio**: Radtel RT-900 series
- **Alternate Name**: iRadio UV-98
- **Type**: Mobile transceiver
- **Protocol Reference**: https://github.com/rampa069/RT880-misc/blob/main/Protocol.md
  (Note: This document appears to describe firmware flashing, not memory programming)

## Contributing

To update this driver:

1. Test with actual hardware
2. Update identification strings if needed
3. Verify channel count and memory layout
4. Confirm power levels and features
5. Create test image: `tests/images/Radtel_RT-880.img`
6. Update driver code with verified values
7. Remove experimental warnings
8. Submit pull request with test results

## File Information

- **Driver File**: `chirp/drivers/radtel_rt880.py`
- **Based On**: `chirp/drivers/radtel_rt900.py`
- **Test Image**: `tests/images/Radtel_RT-880.img` (not yet created)

## Contact

- CHIRP Project: https://chirpmyradio.com
- Issue Tracker: https://chirpmyradio.com/projects/chirp/issues
- Mailing List: https://chirpmyradio.com/projects/chirp/wiki/MailingList
