# CHIRP Driver Development Guide

## Overview

A CHIRP driver is a Python class that implements support for a specific radio model. Drivers handle:
- Communication protocols (serial, USB, etc.)
- Memory structure parsing
- Feature capabilities
- Settings management

This guide walks through creating a new radio driver from scratch.

## Prerequisites

### Understanding Amateur Radio Concepts

Before writing a driver, familiarize yourself with:

- **Memory channels:** Stored frequencies in the radio
- **CTCSS/DCS tones:** Sub-audible tones for squelch control
- **Duplex:** Separate TX/RX frequencies (repeater operation)
- **Offset:** Frequency difference for duplex operation
- **Banks:** Grouping of memory channels
- **VFO:** Variable Frequency Oscillator
- **Split:** Different TX and RX frequencies

### Required Information

To write a driver, you need:

1. **Radio manual** - Protocol documentation
2. **Working radio** - For testing
3. **Sample memory image** - Downloaded from radio
4. **Serial protocol** - Communication commands
5. **Memory map** - How data is structured in radio memory

### Gathering Information

#### 1. Reverse Engineering Tools

```bash
# Serial port sniffer
gcc -o serialsniff tools/serialsniff.c
sudo ./serialsniff /dev/ttyUSB0

# Hex dump comparison
chirpc download /dev/ttyUSB0 before.img
# Change one setting in radio
chirpc download /dev/ttyUSB0 after.img
diff <(xxd before.img) <(xxd after.img)
```

#### 2. Study Similar Radios

Look for drivers from the same manufacturer:

```bash
# Find all Yaesu drivers
ls chirp/drivers/*yaesu* chirp/drivers/ft*.py

# Search for similar protocols
grep -r "BAUD_RATE = 9600" chirp/drivers/
```

#### 3. Community Resources

- CHIRP mailing list archives
- Manufacturer protocol documentation
- Existing reverse engineering notes

## Driver Structure

### Minimal Driver Template

```python
# chirp/drivers/myradio.py

from chirp import chirp_common, directory, memmap, bitwise, errors
import struct
import logging

LOG = logging.getLogger(__name__)

# Memory map definition
MEM_FORMAT = """
#seekto 0x0000;
struct {
  ul32 freq;
  ul32 offset;
  char name[6];
  u8 tmode;
  u8 power:2,
     skip:1,
     duplex:2;
} memory[128];

#seekto 0x1000;
struct {
  u8 squelch;
  u8 backlight;
} settings;
"""

@directory.register
class MyRadio(chirp_common.CloneModeRadio):
    """Vendor Model-123"""

    VENDOR = "Vendor"
    MODEL = "Model-123"
    BAUD_RATE = 9600

    _memsize = 4096

    def get_features(self):
        """Return RadioFeatures for this radio"""
        rf = chirp_common.RadioFeatures()
        rf.has_settings = True
        rf.has_bank = False
        rf.has_ctone = True
        rf.has_cross = True
        rf.has_rx_dtcs = True
        rf.has_tuning_step = True
        rf.can_odd_split = False
        rf.valid_modes = ["FM", "NFM"]
        rf.valid_tmodes = ["", "Tone", "TSQL", "DTCS", "Cross"]
        rf.valid_cross_modes = ["Tone->Tone", "DTCS->", "->DTCS",
                                 "Tone->DTCS", "DTCS->Tone"]
        rf.valid_skips = ["", "S", "P"]
        rf.valid_characters = chirp_common.CHARSET_UPPER_NUMERIC
        rf.valid_bands = [(136000000, 174000000), (400000000, 480000000)]
        rf.valid_power_levels = [
            chirp_common.PowerLevel("High", watts=5),
            chirp_common.PowerLevel("Low", watts=1),
        ]
        rf.valid_name_length = 6
        rf.valid_duplexes = ["", "-", "+", "split"]
        rf.valid_tuning_steps = [5.0, 6.25, 10.0, 12.5, 25.0]
        rf.memory_bounds = (0, 127)
        return rf

    def sync_in(self):
        """Download from radio"""
        try:
            data = self._download()
        except errors.RadioError:
            raise
        except Exception as e:
            raise errors.RadioError(f"Failed to download: {e}")

        self._mmap = memmap.MemoryMapBytes(data)
        self.process_mmap()

    def sync_out(self):
        """Upload to radio"""
        try:
            self._upload()
        except errors.RadioError:
            raise
        except Exception as e:
            raise errors.RadioError(f"Failed to upload: {e}")

    def process_mmap(self):
        """Parse memory map"""
        self._memobj = bitwise.parse(MEM_FORMAT, self._mmap)

    def get_memory(self, number):
        """Get memory channel"""
        _mem = self._memobj.memory[number]
        mem = chirp_common.Memory()
        mem.number = number

        if _mem.freq == 0xFFFFFFFF:
            mem.empty = True
            return mem

        mem.freq = int(_mem.freq)
        mem.offset = int(_mem.offset)
        mem.name = str(_mem.name).rstrip()
        mem.duplex = self._decode_duplex(_mem.duplex)
        mem.mode = "FM" if _mem.tmode < 2 else "NFM"
        mem.skip = "S" if _mem.skip else ""
        mem.power = self._decode_power(_mem.power)

        return mem

    def set_memory(self, mem):
        """Set memory channel"""
        _mem = self._memobj.memory[mem.number]

        if mem.empty:
            _mem.freq = 0xFFFFFFFF
            return

        _mem.freq = mem.freq
        _mem.offset = mem.offset
        _mem.name = mem.name.ljust(6)[:6]
        _mem.duplex = self._encode_duplex(mem.duplex)
        _mem.tmode = 0 if mem.mode == "FM" else 1
        _mem.skip = 1 if mem.skip == "S" else 0
        _mem.power = self._encode_power(mem.power)

    def _download(self):
        """Download data from radio"""
        # Implementation depends on radio protocol
        data = b""
        # ... protocol-specific download code ...
        return data

    def _upload(self):
        """Upload data to radio"""
        # Implementation depends on radio protocol
        # ... protocol-specific upload code ...
        pass

    def _decode_duplex(self, value):
        """Decode duplex from radio format"""
        DUPLEX_MAP = {0: "", 1: "+", 2: "-", 3: "split"}
        return DUPLEX_MAP.get(value, "")

    def _encode_duplex(self, duplex):
        """Encode duplex to radio format"""
        DUPLEX_MAP = {"": 0, "+": 1, "-": 2, "split": 3}
        return DUPLEX_MAP.get(duplex, 0)

    def _decode_power(self, value):
        """Decode power level"""
        rf = self.get_features()
        return rf.valid_power_levels[value]

    def _encode_power(self, power):
        """Encode power level"""
        rf = self.get_features()
        return rf.valid_power_levels.index(power)

    @classmethod
    def match_model(cls, filedata, filename):
        """Detect if file is for this radio"""
        # Check magic bytes or file size
        return len(filedata) == cls._memsize
```

## Step-by-Step Development

### Step 1: Create Driver File

```bash
# Create new driver file
touch chirp/drivers/myradio.py
```

### Step 2: Define Memory Map

Use the bitwise DSL to define the memory structure:

```python
MEM_FORMAT = """
#seekto 0x0000;
struct memory {
  ul32 freq;           // Frequency in Hz (little-endian)
  ul32 offset;         // Offset in Hz
  char name[6];        // 6-character name
  u8 tmode:3,          // Tone mode (3 bits)
     duplex:2,         // Duplex (2 bits)
     skip:1,           // Skip flag (1 bit)
     power:2;          // Power level (2 bits)
  u8 ctone;            // CTCSS tone index
  u8 rtone;            // CTCSS tone index
  bbcd dtcs[2];        // DTCS code (BCD)
};

struct memory memories[128];

#seekto 0x1000;
struct settings {
  u8 squelch;
  u8 backlight;
  char display_msg[16];
};
"""
```

**Common Data Types:**
- `u8`, `u16`, `u32` - Unsigned integers
- `ul16`, `ul32` - Little-endian unsigned
- `ub16`, `ub32` - Big-endian unsigned
- `char[n]` - Character array
- `bbcd` - BCD (2 digits per byte)
- Bitfields: `u8 field:3` (3-bit field)

### Step 3: Implement Communication Protocol

#### Serial Communication

Most radios use serial communication:

```python
def _download(self):
    """Download from radio"""
    # Enter clone mode
    self.pipe.write(b"CLONE_MODE\r\n")
    time.sleep(0.1)

    # Check ACK
    ack = self.pipe.read(1)
    if ack != b'\x06':
        raise errors.RadioError("Radio did not acknowledge")

    # Download data
    data = b""
    for addr in range(0, self._memsize, 16):
        # Request block
        cmd = struct.pack(">HB", addr, 16)  # Address + length
        self.pipe.write(cmd)

        # Read block
        block = self.pipe.read(16)
        if len(block) != 16:
            raise errors.RadioError("Short read")

        data += block

        # Progress reporting
        status = chirp_common.Status()
        status.cur = addr
        status.max = self._memsize
        status.msg = "Cloning from radio"
        self.status_fn(status)

    return data

def _upload(self):
    """Upload to radio"""
    # Enter clone mode
    self.pipe.write(b"CLONE_MODE\r\n")
    time.sleep(0.1)

    # Upload data
    for addr in range(0, self._memsize, 16):
        # Prepare block
        block = self._mmap[addr:addr+16]

        # Send command
        cmd = struct.pack(">HB", addr, 16)
        self.pipe.write(cmd + block)

        # Wait for ACK
        ack = self.pipe.read(1)
        if ack != b'\x06':
            raise errors.RadioError("Radio did not acknowledge")

        # Progress reporting
        status = chirp_common.Status()
        status.cur = addr
        status.max = self._memsize
        status.msg = "Cloning to radio"
        self.status_fn(status)
```

#### Common Protocol Patterns

**1. Command-Response:**
```python
def _send_command(self, cmd, response_len):
    """Send command and read response"""
    self.pipe.write(cmd)
    resp = self.pipe.read(response_len)
    return resp
```

**2. Checksums:**
```python
def _checksum(self, data):
    """Calculate checksum"""
    return sum(data) & 0xFF

def _download_block(self, addr, length):
    """Download block with checksum"""
    cmd = struct.pack(">HB", addr, length)
    self.pipe.write(cmd)

    block = self.pipe.read(length)
    checksum = self.pipe.read(1)[0]

    if self._checksum(block) != checksum:
        raise errors.RadioError("Checksum failed")

    return block
```

**3. Handshaking:**
```python
def _enter_clone_mode(self):
    """Enter clone mode with handshake"""
    # Send magic sequence
    self.pipe.write(b"\x02PROGRAM\x00")
    time.sleep(0.5)

    # Wait for radio response
    for i in range(10):
        resp = self.pipe.read(1)
        if resp == b'\x06':
            return  # Success
        time.sleep(0.1)

    raise errors.RadioError("Radio did not enter clone mode")
```

### Step 4: Implement Memory Get/Set

```python
def get_memory(self, number):
    """Get memory channel"""
    _mem = self._memobj.memories[number]
    mem = chirp_common.Memory()
    mem.number = number

    # Check if empty
    if _mem.freq == 0xFFFFFFFF:
        mem.empty = True
        return mem

    # Frequency
    mem.freq = int(_mem.freq)

    # Offset
    mem.offset = int(_mem.offset)

    # Name
    mem.name = str(_mem.name).rstrip()

    # Duplex
    DUPLEX_MAP = {0: "", 1: "+", 2: "-", 3: "split"}
    mem.duplex = DUPLEX_MAP.get(_mem.duplex, "")

    # Mode
    MODE_MAP = {0: "FM", 1: "NFM", 2: "AM"}
    mem.mode = MODE_MAP.get(_mem.mode, "FM")

    # Tones
    TMODE_MAP = {0: "", 1: "Tone", 2: "TSQL", 3: "DTCS"}
    mem.tmode = TMODE_MAP.get(_mem.tmode, "")

    if mem.tmode in ["Tone", "TSQL"]:
        mem.rtone = chirp_common.TONES[_mem.rtone]
        mem.ctone = chirp_common.TONES[_mem.ctone]
    elif mem.tmode == "DTCS":
        mem.dtcs = chirp_common.DTCS_CODES[_mem.dtcs]

    # Power
    rf = self.get_features()
    if _mem.power < len(rf.valid_power_levels):
        mem.power = rf.valid_power_levels[_mem.power]

    # Skip
    mem.skip = "S" if _mem.skip else ""

    return mem

def set_memory(self, mem):
    """Set memory channel"""
    _mem = self._memobj.memories[mem.number]

    # Handle empty
    if mem.empty:
        _mem.freq = 0xFFFFFFFF
        return

    # Frequency
    _mem.freq = mem.freq

    # Offset
    _mem.offset = mem.offset

    # Name (pad to 6 chars)
    _mem.name = mem.name.ljust(6)[:6]

    # Duplex
    DUPLEX_MAP = {"": 0, "+": 1, "-": 2, "split": 3}
    _mem.duplex = DUPLEX_MAP.get(mem.duplex, 0)

    # Mode
    MODE_MAP = {"FM": 0, "NFM": 1, "AM": 2}
    _mem.mode = MODE_MAP.get(mem.mode, 0)

    # Tones
    TMODE_MAP = {"": 0, "Tone": 1, "TSQL": 2, "DTCS": 3}
    _mem.tmode = TMODE_MAP.get(mem.tmode, 0)

    if mem.tmode in ["Tone", "TSQL"]:
        try:
            _mem.rtone = chirp_common.TONES.index(mem.rtone)
            _mem.ctone = chirp_common.TONES.index(mem.ctone)
        except ValueError:
            raise errors.UnsupportedToneError(f"Tone {mem.rtone} not supported")
    elif mem.tmode == "DTCS":
        try:
            _mem.dtcs = chirp_common.DTCS_CODES.index(mem.dtcs)
        except ValueError:
            raise errors.UnsupportedToneError(f"DTCS {mem.dtcs} not supported")

    # Power
    rf = self.get_features()
    _mem.power = rf.valid_power_levels.index(mem.power)

    # Skip
    _mem.skip = 1 if mem.skip == "S" else 0
```

### Step 5: Add Settings Support (Optional)

```python
from chirp import settings

def get_settings(self):
    """Return radio settings"""
    top = settings.RadioSettings()

    # Basic settings group
    basic = settings.RadioSettingGroup("basic", "Basic Settings")
    top.append(basic)

    # Squelch setting
    rs = settings.RadioSetting(
        "settings.squelch", "Squelch Level",
        settings.RadioSettingValueInteger(
            0, 9, self._memobj.settings.squelch
        )
    )
    basic.append(rs)

    # Backlight setting
    options = ["Off", "Auto", "On"]
    rs = settings.RadioSetting(
        "settings.backlight", "Backlight",
        settings.RadioSettingValueList(
            options, options[self._memobj.settings.backlight]
        )
    )
    basic.append(rs)

    # Display message
    rs = settings.RadioSetting(
        "settings.display_msg", "Display Message",
        settings.RadioSettingValueString(
            0, 16, str(self._memobj.settings.display_msg).rstrip()
        )
    )
    basic.append(rs)

    return top

def set_settings(self, settings):
    """Apply radio settings"""
    for element in settings:
        if not isinstance(element, settings.RadioSetting):
            self.set_settings(element)  # Recurse into groups
            continue

        try:
            # Parse setting path
            obj = self._memobj
            bits = element.get_name().split(".")
            for bit in bits[:-1]:
                obj = getattr(obj, bit)

            # Set value
            setting = bits[-1]
            if isinstance(element.value, settings.RadioSettingValueList):
                # Find index
                options = element.value.get_options()
                setattr(obj, setting, options.index(str(element.value)))
            else:
                setattr(obj, setting, element.value)
        except Exception as e:
            LOG.error(f"Failed to set {element.get_name()}: {e}")
            raise
```

### Step 6: Add Test Image

```bash
# Download from actual radio
chirpc download /dev/ttyUSB0 tests/images/Vendor_Model-123.img

# Or create minimal test image
python -c "import sys; sys.stdout.buffer.write(b'\x00' * 4096)" > tests/images/Vendor_Model-123.img
```

### Step 7: Test the Driver

```bash
# Quick test
python tools/fast-driver.py chirp/drivers/myradio.py

# Full test suite
pytest tests/test_drivers.py -k "Model-123" -v
```

## Advanced Features

### Bank Support

```python
from chirp import chirp_common

class MyRadioBankModel(chirp_common.BankModel):
    """Bank model for MyRadio"""

    def get_num_banks(self):
        """Return number of banks"""
        return 10

    def get_banks(self):
        """Return list of banks"""
        banks = []
        for i in range(10):
            bank = chirp_common.Bank(self, "%i" % i, "Bank-%i" % (i + 1))
            bank.index = i
            banks.append(bank)
        return banks

    def add_memory_to_bank(self, memory, bank):
        """Add memory to bank"""
        _bank = self._radio._memobj.banks[bank.index]
        _bank.members[memory.number] = 1

    def remove_memory_from_bank(self, memory, bank):
        """Remove memory from bank"""
        _bank = self._radio._memobj.banks[bank.index]
        _bank.members[memory.number] = 0

    def get_memory_mappings(self, memory):
        """Return banks containing this memory"""
        banks = []
        for bank in self.get_banks():
            _bank = self._radio._memobj.banks[bank.index]
            if _bank.members[memory.number]:
                banks.append(bank)
        return banks

@directory.register
class MyRadio(chirp_common.CloneModeRadio):
    # ... existing code ...

    def get_features(self):
        rf = super().get_features()
        rf.has_bank = True
        rf.has_bank_names = True
        return rf

    def get_bank_model(self):
        """Return bank model"""
        return MyRadioBankModel(self)
```

### Image Detection

```python
@classmethod
def match_model(cls, filedata, filename):
    """Detect if image is for this radio"""
    # Check file size
    if len(filedata) != cls._memsize:
        return False

    # Check magic bytes
    if filedata[0:4] != b'MRAD':
        return False

    # Check model ID
    model_id = filedata[4:10]
    if model_id != b'M-123\x00':
        return False

    return True
```

### Multiple Sub-devices

For radios with multiple bands (e.g., VHF/UHF):

```python
class MyRadioVHF(MyRadio):
    """VHF sub-device"""
    VARIANT = "VHF"
    _vhf_range = (136000000, 174000000)

    def get_features(self):
        rf = super().get_features()
        rf.valid_bands = [self._vhf_range]
        return rf

class MyRadioUHF(MyRadio):
    """UHF sub-device"""
    VARIANT = "UHF"
    _uhf_range = (400000000, 480000000)

    def get_features(self):
        rf = super().get_features()
        rf.valid_bands = [self._uhf_range]
        return rf

@directory.register
class MyRadio(chirp_common.CloneModeRadio):
    # ... existing code ...

    def get_features(self):
        rf = super().get_features()
        rf.has_sub_devices = True
        return rf

    def get_sub_devices(self):
        """Return sub-devices"""
        return [MyRadioVHF(self._mmap), MyRadioUHF(self._mmap)]
```

## Common Pitfalls

### 1. Endianness

```python
# WRONG - assumes native endian
freq = struct.unpack("I", data[0:4])[0]

# CORRECT - explicit little-endian
freq = struct.unpack("<I", data[0:4])[0]

# CORRECT - using bitwise
# ul32 = little-endian unsigned 32-bit
mem.memory[0].freq  # Automatically handles endianness
```

### 2. String Handling

```python
# WRONG - Python 3 strings are Unicode
_mem.name = mem.name

# CORRECT - Pad and truncate
_mem.name = mem.name.ljust(6)[:6]

# CORRECT - Handle encoding
_mem.name = mem.name.encode('ascii', 'ignore').decode()[:6].ljust(6)
```

### 3. Empty Memories

```python
# WRONG - Don't skip empty check
def get_memory(self, number):
    _mem = self._memobj.memory[number]
    mem = Memory()
    mem.freq = _mem.freq  # May be 0xFFFFFFFF!
    return mem

# CORRECT - Check for empty
def get_memory(self, number):
    _mem = self._memobj.memory[number]
    mem = Memory()
    mem.number = number

    if _mem.freq == 0xFFFFFFFF:
        mem.empty = True
        return mem

    mem.freq = _mem.freq
    return mem
```

### 4. Index vs Value

```python
# WRONG - Storing tone frequency directly
_mem.rtone = mem.rtone  # Stores 88.5, not index!

# CORRECT - Store index
_mem.rtone = chirp_common.TONES.index(mem.rtone)

# CORRECT - Retrieve frequency
mem.rtone = chirp_common.TONES[_mem.rtone]
```

### 5. Memory Maps

```python
# WRONG - Using deprecated MemoryMap
from chirp import memmap
self._mmap = memmap.MemoryMap("\x00" * 4096)

# CORRECT - Using MemoryMapBytes
from chirp import memmap
self._mmap = memmap.MemoryMapBytes(b'\x00' * 4096)
```

## Testing Checklist

- [ ] Driver file created in `chirp/drivers/`
- [ ] Registered with `@directory.register`
- [ ] Test image in `tests/images/Vendor_Model.img`
- [ ] `get_features()` returns valid `RadioFeatures`
- [ ] `sync_in()` downloads from radio
- [ ] `sync_out()` uploads to radio
- [ ] `get_memory()` returns valid `Memory` objects
- [ ] `set_memory()` writes to memory map
- [ ] Empty memories handled correctly
- [ ] Tone modes work (CTCSS, DCS)
- [ ] Power levels work
- [ ] Skip flags work
- [ ] Settings (if applicable) work
- [ ] Banks (if applicable) work
- [ ] Passes `tools/fast-driver.py`
- [ ] Passes full pytest driver tests
- [ ] Tested on actual hardware

## Debugging Tips

### Enable Debug Logging

```bash
export CHIRP_DEBUG=y
python tools/fast-driver.py chirp/drivers/myradio.py
```

### Serial Sniffing

```bash
# Compile sniffer
gcc -o serialsniff tools/serialsniff.c

# Run between official software and radio
sudo ./serialsniff /dev/ttyUSB0

# Capture official download sequence
# Then replicate in your driver
```

### Memory Dump Comparison

```python
# Dump before and after
import sys
data = open(sys.argv[1], 'rb').read()
for i in range(0, len(data), 16):
    print("%04x: %s" % (i, " ".join("%02x" % b for b in data[i:i+16])))
```

### Interactive Testing

```python
from chirp import directory

# Load driver
radio = directory.get_radio("Vendor Model-123")("tests/images/Vendor_Model-123.img")

# Test memory access
mem = radio.get_memory(0)
print(mem)

# Modify
mem.freq = 146520000
radio.set_memory(mem)

# Verify
mem2 = radio.get_memory(0)
print(mem2.freq)
```

## Example Drivers to Study

### Simple Drivers
- `chirp/drivers/fake.py` - Minimal example
- `chirp/drivers/ft60.py` - Well-structured Yaesu
- `chirp/drivers/uv5r.py` - Popular Baofeng

### Complex Drivers
- `chirp/drivers/btech.py` - Large, feature-rich
- `chirp/drivers/icf.py` - Icom format handler
- `chirp/drivers/th9800.py` - Multiple bands

### Special Cases
- `chirp/drivers/generic_csv.py` - CSV import/export
- `chirp/sources/radioreference.py` - Network source
- `chirp/drivers/tk8180.py` - Advanced settings

## Resources

- **Mailing list:** https://chirpmyradio.com/projects/chirp/wiki/MailingList
- **Issue tracker:** https://chirpmyradio.com/projects/chirp/issues
- **Developer wiki:** https://chirpmyradio.com/projects/chirp/wiki/Developers
- **Example drivers:** `chirp/drivers/`
- **Test framework:** `tests/`

## Contributing Your Driver

1. **Test thoroughly** on actual hardware
2. **Add test image** to `tests/images/`
3. **Run style checks:** `tox -e style`
4. **Run tests:** `python tools/fast-driver.py chirp/drivers/myradio.py`
5. **Create pull request** following `.github/pull_request_template.md`
6. **Reference issue** if applicable: `Fixes #1234`
7. **Commit message:** `[myradio] Add support for Vendor Model-123`

Remember: Every driver makes CHIRP more valuable to the amateur radio community!
