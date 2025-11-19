# CHIRP Modules Reference

This document provides a detailed breakdown of all major modules in the CHIRP codebase.

## Core Modules

### `chirp/chirp_common.py` (~2,000 lines)

**Purpose:** Core abstractions and data structures for radio programming.

**Key Classes:**

#### `RadioFeatures`
Defines capabilities of a radio model.

```python
class RadioFeatures:
    # Memory bounds
    memory_bounds = (0, 999)         # Min/max memory channel numbers

    # Feature flags
    has_bank = False                  # Supports memory banks
    has_bank_index = False            # Banks have explicit indices
    has_bank_names = False            # Banks can be named
    has_dtcs = True                   # DTCS tone support
    has_dtcs_polarity = True          # DTCS polarity (N/R)
    has_ctone = True                  # CTCSS tone support
    has_cross = True                  # Cross-tone mode
    has_rx_dtcs = True                # Separate RX DTCS
    has_tuning_step = True            # Tuning step support
    has_name = True                   # Memory name/alpha tag
    has_offset = True                 # TX offset
    has_mode = True                   # Mode (FM/AM/NFM/etc.)
    has_comment = False               # Memory comments
    has_settings = True               # Radio settings support
    has_nostep_tuning = False         # Arbitrary frequency tuning

    # Valid values
    valid_modes = ["FM", "NFM", "AM"]  # Supported modes
    valid_tmodes = ["", "Tone", "TSQL", "DTCS", "Cross"]  # Tone modes
    valid_cross_modes = ["Tone->Tone", "DTCS->", "->DTCS", "Tone->DTCS", "DTCS->Tone", "->Tone", "DTCS->DTCS"]
    valid_power_levels = [...]        # Power levels
    valid_duplexes = ["", "+", "-", "split", "off"]
    valid_skips = ["", "S", "P"]      # Skip modes (S=skip, P=pskip)
    valid_bands = [(136000000, 174000000), (400000000, 480000000)]  # Frequency ranges in Hz
    valid_tuning_steps = [5.0, 6.25, 10.0, 12.5, 15.0, 20.0, 25.0, 50.0, 100.0]  # kHz
    valid_name_length = 6             # Max chars in memory name
    valid_characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -"

    # Special features
    has_sub_devices = False           # Multiple sub-devices (bands)
    can_odd_split = False             # Odd split support

    # Memory deletion
    memory_deletion = True            # Can delete memories
```

#### `Memory`
Represents a single memory channel.

```python
class Memory:
    number = 0                        # Memory channel number
    extd_number = ""                  # Extended number (e.g., "1A")
    name = ""                         # Alpha tag / name
    freq = 0                          # Frequency in Hz
    rtone = 88.5                      # TX CTCSS tone (Hz)
    ctone = 88.5                      # RX CTCSS tone (Hz)
    dtcs = 23                         # DTCS code
    rx_dtcs = 23                      # RX DTCS code
    dtcs_polarity = "NN"              # DTCS polarity (NN/NR/RN/RR)
    tmode = ""                        # Tone mode ("", "Tone", "TSQL", "DTCS", "Cross")
    cross_mode = "Tone->Tone"         # Cross tone mode
    duplex = ""                       # Duplex ("", "+", "-", "split", "off")
    offset = 0                        # TX offset in Hz
    mode = "FM"                       # Modulation mode
    tuning_step = 5.0                 # Tuning step in kHz
    skip = ""                         # Skip ("", "S", "P")
    power = None                      # Power level
    comment = ""                      # Comment
    immutable = []                    # List of immutable fields
    empty = False                     # Is empty memory
```

#### `Radio` (abstract base class)
Base for all radio types.

**Abstract Methods:**
```python
def get_features(self) -> RadioFeatures
def get_memory(self, number: int) -> Memory
def set_memory(self, memory: Memory)
def erase_memory(self, number: int)
```

**Optional Methods:**
```python
def get_memories(self, lo: int = None, hi: int = None) -> List[Memory]
def get_raw_memory(self, number: int) -> bytes
def get_settings(self) -> RadioSettings
def set_settings(self, settings: RadioSettings)
def get_bank_model(self) -> BankModel
```

#### `CloneModeRadio`
Base for radios with full memory clone.

**Required Methods:**
```python
def sync_in(self)                    # Download from radio
def sync_out(self)                   # Upload to radio
def process_mmap(self)               # Parse memory map after download
```

#### `LiveRadio`
Base for radios with real-time communication.

**Implementation:** Each `get_memory()` / `set_memory()` reads/writes to radio directly.

#### `NetworkSourceRadio`
Base for online repeater databases.

**Required Method:**
```python
def do_fetch(self, freq: int, coords: tuple) -> List[Memory]
```

**Constants:**

```python
# CTCSS tones in Hz
TONES = [67.0, 69.3, 71.9, 74.4, 77.0, 79.7, 82.5, 85.4, 88.5, 91.5, 94.8,
         97.4, 100.0, 103.5, 107.2, 110.9, 114.8, 118.8, 123.0, 127.3, 131.8,
         136.5, 141.3, 146.2, 151.4, 156.7, 162.2, 167.9, 173.8, 179.9, 186.2,
         192.8, 203.5, 210.7, 218.1, 225.7, 233.6, 241.8, 250.3]

# DTCS codes
DTCS_CODES = [23, 25, 26, 31, 32, 36, 43, 47, 51, 53, 54, 65, 71, 72, 73, 74,
              114, 115, 116, 122, 125, 131, 132, 134, 143, 145, 152, 155, 156,
              162, 165, 172, 174, 205, 212, 223, 225, 226, 243, 244, 245, 246,
              251, 252, 255, 261, 263, 265, 266, 271, 274, 306, 311, 315, 325,
              331, 332, 343, 346, 351, 356, 364, 365, 371, 411, 412, 413, 423,
              431, 432, 445, 446, 452, 454, 455, 462, 464, 465, 466, 503, 506,
              516, 523, 526, 532, 546, 565, 606, 612, 624, 627, 631, 632, 654,
              662, 664, 703, 712, 723, 731, 732, 734, 743, 754]

# Modes
MODES = ["FM", "NFM", "AM", "NAM", "DV", "USB", "LSB", "CW", "RTTY", "DIG",
         "PKT", "NCW", "NCWR", "CWR", "P25", "DMR", "dPMR", "NXDN", "C4FM",
         "Auto"]

# Duplex modes
DUPLEX = ["", "+", "-", "split", "off"]

# Cross modes
CROSS_MODES = ["Tone->Tone", "DTCS->", "->DTCS", "Tone->DTCS", "DTCS->Tone",
               "->Tone", "DTCS->DTCS"]
```

**Location:** `/home/user/chirp/chirp/chirp_common.py`

---

### `chirp/directory.py`

**Purpose:** Central registry for radio drivers, image detection, and driver lookup.

**Key Functions:**

```python
def register(cls):
    """Decorator to register a radio driver"""
    RADIO_CLASSES.append(cls)
    DRV_TO_RADIO[f"{cls.VENDOR} {cls.MODEL}"] = cls
    return cls

def get_radio(model: str) -> Type[Radio]:
    """Get radio class by vendor and model"""
    return DRV_TO_RADIO.get(model)

def get_radio_by_image(filename: str) -> Radio:
    """Detect radio type from image file and return instance"""
    metadata = get_file_metadata(filename)
    for cls in RADIO_CLASSES:
        if hasattr(cls, 'match_model') and cls.match_model(metadata):
            return cls(filename)
    raise errors.ImageDetectFailed(f"Unknown file format: {filename}")

def register_format(name: str, pattern: bytes, readonly: bool = False):
    """Register a file format pattern for detection"""
    pass
```

**Key Data Structures:**

```python
RADIO_CLASSES = []                    # All registered radio classes
DRV_TO_RADIO = {}                     # Model name -> class mapping
```

**Location:** `/home/user/chirp/chirp/directory.py`

---

### `chirp/bitwise.py` (~1,400 lines)

**Purpose:** Custom DSL parser for radio memory structures.

**DSL Syntax:**

```c
// Seekto absolute position
#seekto 0x0000;

// Structure definition
struct memory {
  ul32 freq;              // Little-endian 32-bit unsigned
  ul16 offset;            // Little-endian 16-bit unsigned
  u8 tmode;               // 8-bit unsigned
  u8 power:2,             // 2-bit bitfield
     skip:1,              // 1-bit bitfield
     duplex:2;            // 2-bit bitfield
  char name[6];           // 6-character array
  bbcd dtcs[2];           // BCD-encoded array
};

// Array of structures
struct memory memories[128];

// Union (overlapping fields)
union {
  struct memory mem;
  u8 raw[16];
} data;

// Alignment
#seekto 0x1000;
struct {
  u8 settings[256];
} config;
```

**Data Types:**

- `u8`, `u16`, `u32`, `u64` - Unsigned integers (native endian)
- `ul16`, `ul32`, `ul64` - Unsigned little-endian
- `ub16`, `ub32`, `ub64` - Unsigned big-endian
- `i8`, `i16`, `i32` - Signed integers
- `il16`, `il32` - Signed little-endian
- `ib16`, `ib32` - Signed big-endian
- `char[n]` - Character array
- `bbcd` - Binary-coded decimal (2 digits per byte)
- `lbcd` - Little-endian BCD

**Key Classes:**

```python
class DataElement:
    """Base for all data elements"""
    def set_value(self, value)
    def get_value(self)

class StructDataElement:
    """Structure container"""
    def __getattr__(self, name)  # Access fields by name

class ArrayDataElement:
    """Array container"""
    def __getitem__(self, index)  # Access elements by index

def parse(definition: str, data: bytes) -> StructDataElement:
    """Parse bitwise definition and map to binary data"""
    grammar = load_grammar()
    tree = parser.parse(definition)
    return build_structure(tree, data)
```

**Usage Example:**

```python
from chirp import bitwise, memmap

MEM_FORMAT = """
#seekto 0x0000;
struct {
  ul32 freq;
  char name[6];
} memory[128];
"""

data = memmap.MemoryMapBytes(b'\x00' * 2048)
mem = bitwise.parse(MEM_FORMAT, data)

# Access and modify
mem.memory[0].freq = 146520000
mem.memory[0].name = "CALL"

# Read back
print(mem.memory[0].freq)  # 146520000
print(mem.memory[0].name)  # "CALL  "
```

**Location:** `/home/user/chirp/chirp/bitwise.py`

---

### `chirp/settings.py`

**Purpose:** Framework for radio settings (non-memory configuration).

**Key Classes:**

#### `RadioSetting`
Individual setting with name, label, and value.

```python
rs = RadioSetting(
    "settings.squelch",              # Setting path
    "Squelch Level",                 # Display label
    RadioSettingValueInteger(0, 9, 5)  # Value with bounds
)
```

#### `RadioSettingGroup`
Group of related settings.

```python
basic = RadioSettingGroup("basic", "Basic Settings")
basic.append(RadioSetting(...))
basic.append(RadioSetting(...))
```

#### `RadioSettings`
Top-level settings container.

```python
top = RadioSettings()
top.append(basic_group)
top.append(advanced_group)
return top
```

#### Value Types

**`RadioSettingValueInteger(min, max, current)`**
```python
RadioSettingValueInteger(0, 255, 50)
```

**`RadioSettingValueFloat(min, max, current, resolution=0.1)`**
```python
RadioSettingValueFloat(0.0, 10.0, 5.5, 0.1)
```

**`RadioSettingValueBoolean(current)`**
```python
RadioSettingValueBoolean(True)
```

**`RadioSettingValueList(options, current)`**
```python
RadioSettingValueList(["Off", "Low", "High"], "Low")
```

**`RadioSettingValueString(min_len, max_len, current)`**
```python
RadioSettingValueString(0, 16, "My Radio")
```

**Usage in Driver:**

```python
def get_settings(self):
    top = RadioSettings()

    basic = RadioSettingGroup("basic", "Basic")
    top.append(basic)

    rs = RadioSetting("settings.squelch", "Squelch",
                      RadioSettingValueInteger(0, 9,
                          self._memobj.settings.squelch))
    basic.append(rs)

    return top

def set_settings(self, settings):
    for element in settings:
        if not isinstance(element, RadioSetting):
            self.set_settings(element)  # Recurse
            continue

        # Apply setting
        setattr(self._memobj.settings, element.get_name(), element.value)
```

**Location:** `/home/user/chirp/chirp/settings.py`

---

### `chirp/memmap.py`

**Purpose:** Memory map abstractions for radio image data.

**Classes:**

#### `MemoryMapBytes` (NEW - Required)
Binary memory map using bytes.

```python
from chirp import memmap

# Create
mmap = memmap.MemoryMapBytes(b'\x00' * 4096)

# Access
mmap[0] = 0x12
chunk = mmap[0:16]

# Get range
data = mmap.get(0x0100, 256)

# Set range
mmap.set(0x0100, b'\xFF' * 256)

# Get all as bytes
all_bytes = mmap.get_byte_compatible()
```

#### `MemoryMap` (DEPRECATED)
Old string-based memory map. **Do not use for new drivers.**

```python
mmap = memmap.MemoryMap('\x00' * 4096)  # DEPRECATED!
```

**Location:** `/home/user/chirp/chirp/memmap.py`

---

### `chirp/errors.py`

**Purpose:** Exception hierarchy for error handling.

**Exception Classes:**

```python
class RadioError(Exception):
    """Base for all radio errors"""
    pass

class InvalidMemoryLocation(RadioError):
    """Invalid memory channel number"""
    pass

class InvalidDataError(RadioError):
    """Invalid data format"""
    pass

class InvalidValueError(RadioError):
    """Invalid value for field"""
    pass

class ImageDetectFailed(RadioError):
    """Could not detect radio from image"""
    pass

class UnsupportedToneError(RadioError):
    """Tone not supported by radio"""
    pass

class RadioNotConnectedError(RadioError):
    """Radio not connected"""
    pass

class RadioTimeoutError(RadioError):
    """Communication timeout"""
    pass
```

**Usage:**

```python
from chirp import errors

if number < rf.memory_bounds[0] or number > rf.memory_bounds[1]:
    raise errors.InvalidMemoryLocation(f"Invalid memory: {number}")

if freq < 136000000 or freq > 174000000:
    raise errors.InvalidValueError(f"Frequency out of range: {freq}")
```

**Location:** `/home/user/chirp/chirp/errors.py`

---

### `chirp/import_logic.py`

**Purpose:** Import memories between different radio models with feature translation.

**Key Functions:**

```python
def import_mem(dst_radio: Radio, src_mem: Memory, overrides=None) -> Memory:
    """
    Import memory from one radio to another, translating features.

    - Validates frequency against dst_radio bands
    - Maps tone modes
    - Converts power levels
    - Handles duplex differences
    """
    dst_rf = dst_radio.get_features()
    dst_mem = Memory()

    # Copy basic fields
    dst_mem.freq = src_mem.freq
    dst_mem.name = src_mem.name[:dst_rf.valid_name_length]

    # Validate frequency
    if not is_valid_freq(dst_rf, src_mem.freq):
        raise errors.InvalidValueError("Frequency not supported")

    # Map tone modes
    if dst_rf.has_ctone and src_mem.tmode == "Tone":
        dst_mem.tmode = "Tone"
        dst_mem.rtone = src_mem.rtone

    # Map power
    if dst_rf.valid_power_levels:
        dst_mem.power = closest_power(dst_rf, src_mem.power)

    return dst_mem

def is_valid_freq(rf: RadioFeatures, freq: int) -> bool:
    """Check if frequency is valid for radio"""
    for low, high in rf.valid_bands:
        if low <= freq <= high:
            return True
    return False
```

**Location:** `/home/user/chirp/chirp/import_logic.py`

---

### `chirp/logger.py`

**Purpose:** Logging configuration.

**Setup:**

```python
import logging
from chirp import logger

# Initialize logging
logger.init_logging()

# Get logger
LOG = logging.getLogger(__name__)

# Log levels
LOG.debug("Debug message")
LOG.info("Info message")
LOG.warning("Warning message")
LOG.error("Error message")
```

**Environment Variables:**

- `CHIRP_DEBUG=y` - Enable debug logging
- `CHIRP_LOG_LEVEL=DEBUG` - Set log level

**Location:** `/home/user/chirp/chirp/logger.py`

---

### `chirp/util.py`

**Purpose:** Utility functions.

**Key Functions:**

```python
def hexprint(data: bytes, addrfmt: str = None) -> str:
    """Pretty-print binary data as hex dump"""
    return formatted_hex_dump

def bcd_encode(value: int, width: int = 2) -> bytes:
    """Encode integer as BCD"""
    return bcd_bytes

def bcd_decode(data: bytes) -> int:
    """Decode BCD to integer"""
    return integer

def get_dict_rev(d: dict, value) -> key:
    """Reverse dictionary lookup"""
    for k, v in d.items():
        if v == value:
            return k
```

**Location:** `/home/user/chirp/chirp/util.py`

---

### `chirp/platform.py`

**Purpose:** Platform-specific functionality (Windows, Linux, macOS).

**Key Functions:**

```python
def get_platform() -> Platform:
    """Get platform-specific instance"""
    if os.name == "nt":
        return Win32Platform()
    elif sys.platform == "darwin":
        return MacOSXPlatform()
    else:
        return UnixPlatform()

class Platform:
    def config_dir(self) -> str:
        """Get configuration directory"""
        # Linux: ~/.config/chirp
        # Windows: %APPDATA%\chirp
        # macOS: ~/Library/Application Support/chirp

    def log_dir(self) -> str:
        """Get log directory"""

    def list_serial_ports(self) -> List[str]:
        """List available serial ports"""
        # Platform-specific serial port enumeration
```

**Location:** `/home/user/chirp/chirp/platform.py`

---

## UI Modules (`chirp/wxui/`)

### `chirp/wxui/main.py`

**Purpose:** Main application window.

**Key Classes:**

- `ChirpMainWindow` - Main frame
- `EditorNotebook` - Tab control for multiple radios

**Location:** `/home/user/chirp/chirp/wxui/main.py`

---

### `chirp/wxui/memedit.py`

**Purpose:** Memory editor grid.

**Key Classes:**

- `ChirpMemEdit` - Main memory editor panel
- `ChirpMemEditGrid` - Grid control for memories

**Features:**
- Editable grid for memory channels
- Copy/paste support
- Import from CSV
- Validation on cell change

**Location:** `/home/user/chirp/chirp/wxui/memedit.py`

---

### `chirp/wxui/settingsedit.py`

**Purpose:** Settings editor panel.

**Key Classes:**

- `ChirpSettingsEdit` - Settings editor panel
- Creates UI controls from `RadioSettings` structure

**Location:** `/home/user/chirp/chirp/wxui/settingsedit.py`

---

### `chirp/wxui/clone.py`

**Purpose:** Clone (download/upload) dialogs.

**Key Classes:**

- `CloneDialog` - Base clone dialog
- `DownloadDialog` - Download from radio
- `UploadDialog` - Upload to radio

**Location:** `/home/user/chirp/chirp/wxui/clone.py`

---

### `chirp/wxui/radiothread.py`

**Purpose:** Background thread for radio operations.

**Key Classes:**

```python
class RadioJob:
    """Represents a radio operation"""
    def run(self, radio):
        pass

class RadioThread(threading.Thread):
    """Background thread for radio operations"""
    def run(self):
        try:
            result = self.job.run(self.radio)
            wx.PostEvent(self.parent, RadioJobEvent(result=result))
        except Exception as e:
            wx.PostEvent(self.parent, RadioJobEvent(error=e))
```

**Location:** `/home/user/chirp/chirp/wxui/radiothread.py`

---

## CLI Modules (`chirp/cli/`)

### `chirp/cli/main.py`

**Purpose:** Command-line interface.

**Commands:**

```bash
chirpc download <port> <file>          # Download from radio
chirpc upload <file> <port>            # Upload to radio
chirpc query <file>                    # Query radio info
chirpc get_memory <file> <number>      # Get single memory
chirpc set_memory <file> <number> <freq>  # Set memory
chirpc copy <src> <dst>                # Copy between radios
```

**Location:** `/home/user/chirp/chirp/cli/main.py`

---

## Network Sources (`chirp/sources/`)

### `chirp/sources/radioreference.py`

**Purpose:** RadioReference.com integration.

**API:** SOAP-based web service for repeater data.

**Location:** `/home/user/chirp/chirp/sources/radioreference.py`

---

### `chirp/sources/repeaterbook.py`

**Purpose:** RepeaterBook.com integration.

**API:** REST API for repeater data.

**Location:** `/home/user/chirp/chirp/sources/repeaterbook.py`

---

## Summary Table

| Module | Purpose | Size | Key Classes |
|--------|---------|------|-------------|
| `chirp_common.py` | Core abstractions | ~2,000 lines | `Radio`, `Memory`, `RadioFeatures` |
| `directory.py` | Driver registry | ~400 lines | N/A (functions) |
| `bitwise.py` | Memory structure DSL | ~1,400 lines | `DataElement`, `parse()` |
| `settings.py` | Settings framework | ~500 lines | `RadioSetting`, `RadioSettings` |
| `memmap.py` | Memory maps | ~200 lines | `MemoryMapBytes` |
| `import_logic.py` | Cross-radio import | ~300 lines | `import_mem()` |
| `errors.py` | Exceptions | ~100 lines | `RadioError` hierarchy |
| `logger.py` | Logging | ~100 lines | Logging setup |
| `util.py` | Utilities | ~200 lines | Various helpers |
| `platform.py` | Platform support | ~300 lines | `Platform` classes |

Each module is designed for a specific purpose with clear interfaces, enabling easy testing and maintenance.
