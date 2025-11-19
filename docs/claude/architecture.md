# CHIRP Architecture Deep Dive

## Overview

CHIRP uses a plugin-based architecture where each radio model is implemented as a separate driver that inherits from common base classes. This design allows for supporting 184+ radio models from different manufacturers while maintaining code reusability and consistency.

## Core Architecture Patterns

### 1. Plugin/Driver Pattern

Each radio driver is a Python class that:
- Inherits from a base radio class
- Registers itself with the central directory
- Implements required methods for radio communication
- Defines its capabilities through `RadioFeatures`

**Example:**
```python
from chirp import chirp_common, directory

@directory.register
class MyRadio(chirp_common.CloneModeRadio):
    VENDOR = "Example"
    MODEL = "Radio-1000"
    BAUD_RATE = 9600

    def get_features(self):
        rf = chirp_common.RadioFeatures()
        rf.memory_bounds = (0, 127)
        rf.has_bank = False
        return rf

    def sync_in(self):
        # Download from radio
        pass

    def sync_out(self):
        # Upload to radio
        pass
```

### 2. Base Class Hierarchy

```
RadioFeatures                   # Defines radio capabilities
Memory                          # Represents a memory channel
Bank                            # Represents a memory bank
BankModel                       # Bank management interface

Radio (abstract base)
├── FileBackedRadio            # For file-based configurations
│   ├── CloneModeRadio         # Full memory download/upload
│   └── NetworkSourceRadio     # Online data sources
└── LiveRadio                  # Real-time communication
```

**Key Base Classes:**

#### `Radio` (abstract)
- Base for all radio types
- Defines interface: `get_features()`, `get_memory()`, `set_memory()`
- Implements common functionality

#### `FileBackedRadio`
- Radios that work with memory images
- Has `_memobj` attribute for parsed memory
- Supports save/load from files

#### `CloneModeRadio`
- Downloads/uploads full memory image
- Implements `sync_in()` and `sync_out()`
- Most common base class for hardware radios

#### `LiveRadio`
- Real-time communication (not clone mode)
- Each operation reads/writes to radio directly
- Less common, used by some modern radios

#### `NetworkSourceRadio`
- Fetches data from online sources
- Examples: RadioReference, RepeaterBook
- Returns `Memory` objects from web APIs

**Locations:**
- Base classes: `chirp/chirp_common.py`
- Driver registry: `chirp/directory.py`
- Individual drivers: `chirp/drivers/*.py`

### 3. Registry Pattern

The `directory` module maintains a central registry of all radio drivers:

```python
# chirp/directory.py

# Registration decorator
@register
def MyRadio(CloneModeRadio):
    pass

# Driver discovery
DRV_TO_RADIO = {}  # Maps driver name to class
RADIO_CLASSES = []  # List of all registered classes

# Image detection
def get_radio_by_image(filename):
    """Detect radio type from image file"""
    for cls in RADIO_CLASSES:
        if cls.match_model(get_file_metadata(filename)):
            return cls
    raise errors.ImageDetectFailed()

# Model lookup
def get_radio(model_name):
    """Get radio class by model name"""
    return DRV_TO_RADIO.get(model_name)
```

**Key Functions:**
- `register()` - Decorator to register radio classes
- `get_radio()` - Lookup radio by model name
- `get_radio_by_image()` - Detect radio from image file
- `register_format()` - Register custom file formats

### 4. Memory Structure System (Bitwise)

CHIRP uses a custom DSL for defining radio memory structures. This is parsed by `bitwise.py` using the Lark parser.

**Example Bitwise Definition:**
```python
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
  u8 contrast;
  char display_text[16];
} settings;
"""

# Parse and use
mem = bitwise.parse(MEM_FORMAT, data)
mem.memory[0].freq = 146520000  # 146.52 MHz
mem.memory[0].name = "SIMPLEX"
```

**Bitwise Features:**
- C-like struct syntax
- Support for arrays, bitfields, unions
- `#seekto` directive for absolute positioning
- Data types: `u8`, `u16`, `u32`, `ul16`, `ul32`, `bbcd`, `char`
- Endianness: `ul` = little-endian, `ub` = big-endian
- BCD encoding: `bbcd` for Binary-Coded Decimal

**Location:** `chirp/bitwise.py` (~1,400 lines)

### 5. Settings Framework

The settings system provides a typed, hierarchical structure for radio configuration:

```python
from chirp import settings

# Create settings group
basic = settings.RadioSettingGroup("basic", "Basic Settings")

# Add settings
rs = settings.RadioSetting(
    "squelch", "Squelch Level",
    settings.RadioSettingValueInteger(0, 9, self._memobj.settings.squelch)
)
basic.append(rs)

# List setting
options = ["Off", "Low", "High"]
rs = settings.RadioSetting(
    "beep", "Beep",
    settings.RadioSettingValueList(options, options[self._memobj.settings.beep])
)
basic.append(rs)

# Return from get_settings()
group = settings.RadioSettings(basic)
return group
```

**Setting Types:**
- `RadioSettingValueInteger(min, max, current)` - Integer with bounds
- `RadioSettingValueFloat(min, max, current)` - Floating point
- `RadioSettingValueBoolean(current)` - Boolean on/off
- `RadioSettingValueList(options, current)` - Choice from list
- `RadioSettingValueString(min_len, max_len, current)` - Text string

**Location:** `chirp/settings.py`

### 6. Memory Map Abstraction

Two memory map implementations:

#### `MemoryMapBytes` (NEW - Required for new drivers)
```python
from chirp import memmap

# Create from bytes
data = memmap.MemoryMapBytes(b'\x00' * 4096)

# Access as bytes
data[0:4] = b'\x12\x34\x56\x78'

# Get range
chunk = data.get(0x0100, 0x0200)
```

#### `MemoryMap` (DEPRECATED - Compatibility only)
```python
# Old string-based interface
data = memmap.MemoryMap('\x00' * 4096)
```

**Location:** `chirp/memmap.py`

### 7. Import/Export Logic

Cross-radio memory import handled by `import_logic.py`:

```python
from chirp import import_logic

# Import memory from one radio to another
src_radio = directory.get_radio("Yaesu FT-60")()
dst_radio = directory.get_radio("Baofeng UV-5R")()

# Import with feature mapping
dst_mem = import_logic.import_mem(dst_radio, src_radio.get_memory(1))
dst_radio.set_memory(dst_mem)
```

**Handles:**
- Feature compatibility checking
- Tone mode translation (CTCSS, DCS, TSQL, etc.)
- Power level mapping
- Frequency validation
- Duplex conversion

**Location:** `chirp/import_logic.py`

## Data Flow

### 1. Download from Radio (Clone Mode)

```
User clicks "Download"
    ↓
wxui/clone.py: CloneDialog
    ↓
wxui/radiothread.py: RadioThread (background)
    ↓
driver.sync_in()
    ├─→ Serial communication (pyserial)
    ├─→ Build MemoryMapBytes from received data
    ├─→ Parse with bitwise
    └─→ Return complete image
    ↓
wxui/memedit.py: Display memories
```

### 2. Edit Memory

```
User edits memory in GUI
    ↓
wxui/memedit.py: OnCellChange
    ↓
driver.set_memory(Memory)
    ↓
Update _memobj (bitwise structure)
    ↓
Mark as modified
```

### 3. Upload to Radio

```
User clicks "Upload"
    ↓
wxui/clone.py: CloneDialog
    ↓
wxui/radiothread.py: RadioThread
    ↓
driver.sync_out()
    ├─→ Serialize _memobj to bytes
    ├─→ Serial communication
    └─→ Send data to radio
    ↓
Success/error dialog
```

### 4. Import from File

```
User opens .img file
    ↓
directory.get_radio_by_image(filename)
    ├─→ Try each registered driver
    ├─→ Call driver.match_model(metadata)
    └─→ Return matching driver class
    ↓
driver = RadioClass(filename)
    ↓
Load and parse image
    ↓
Display in editor
```

### 5. CLI Workflow

```bash
chirpc download /dev/ttyUSB0 radio.img
```

```
cli/main.py: main()
    ↓
directory.get_radio(args.radio)
    ↓
driver.sync_in()
    ↓
driver.save(args.file)
```

## Extension Points

### Adding a New Radio Driver

**Minimum Required:**

1. **Create driver file:** `chirp/drivers/myradio.py`

2. **Import and register:**
```python
from chirp import chirp_common, directory, memmap, bitwise

@directory.register
class MyRadio(chirp_common.CloneModeRadio):
    VENDOR = "Manufacturer"
    MODEL = "Model-123"
```

3. **Define capabilities:**
```python
def get_features(self):
    rf = chirp_common.RadioFeatures()
    rf.memory_bounds = (0, 127)
    rf.has_ctone = True
    rf.has_dtcs = True
    rf.valid_bands = [(136000000, 174000000)]
    return rf
```

4. **Implement sync:**
```python
def sync_in(self):
    # Download from radio
    data = self._download()
    self._mmap = memmap.MemoryMapBytes(data)
    self.process_mmap()

def sync_out(self):
    # Upload to radio
    self._upload(self._mmap.get_byte_compatible())
```

5. **Memory get/set:**
```python
def get_memory(self, number):
    _mem = self._memobj.memory[number]
    mem = chirp_common.Memory()
    mem.number = number
    mem.freq = int(_mem.freq) * 10  # Convert to Hz
    mem.name = str(_mem.name).rstrip()
    return mem

def set_memory(self, mem):
    _mem = self._memobj.memory[mem.number]
    _mem.freq = mem.freq / 10
    _mem.name = mem.name.ljust(6)[:6]
```

6. **Add test image:** `tests/images/Manufacturer_Model-123.img`

### Adding a Network Source

```python
@directory.register
class MySource(chirp_common.NetworkSourceRadio):
    VENDOR = "MySource"
    MODEL = "Database"

    def do_fetch(self, freq, coords):
        # Fetch from web API
        response = requests.get(f"https://api.example.com/repeaters?freq={freq}")
        memories = []
        for data in response.json():
            mem = chirp_common.Memory()
            mem.freq = data['frequency']
            mem.name = data['callsign']
            memories.append(mem)
        return memories
```

**Location:** `chirp/sources/`

### Adding Custom Settings

```python
def get_settings(self):
    top = settings.RadioSettings()

    # Create group
    basic = settings.RadioSettingGroup("basic", "Basic")
    top.append(basic)

    # Add settings
    rs = settings.RadioSetting(
        "settings.squelch", "Squelch",
        settings.RadioSettingValueInteger(0, 9, self._memobj.settings.squelch)
    )
    basic.append(rs)

    return top

def set_settings(self, settings):
    for element in settings:
        if not isinstance(element, settings.RadioSetting):
            self.set_settings(element)  # Recurse into groups
            continue

        # Apply setting
        obj = self._memobj
        for attr in element.get_name().split('.'):
            obj = getattr(obj, attr)
        obj.set_value(element.value)
```

## Platform-Specific Code

`chirp/platform.py` handles platform differences:

```python
import platform
from chirp import platform as chirp_platform

# Get config directory
config_dir = chirp_platform.get_platform().config_dir()
# Linux: ~/.config/chirp
# Windows: %APPDATA%\chirp
# macOS: ~/Library/Application Support/chirp

# Serial port listing
ports = chirp_platform.get_platform().list_serial_ports()
# Platform-specific serial enumeration
```

## Error Handling

Exception hierarchy in `chirp/errors.py`:

```
Exception
└── RadioError (base for all radio errors)
    ├── InvalidMemoryLocation
    ├── InvalidDataError
    ├── InvalidValueError
    ├── ImageDetectFailed
    ├── UnsupportedToneError
    └── RadioNotifications (warnings)
```

**Usage:**
```python
from chirp import errors

if not (136000000 <= freq <= 174000000):
    raise errors.InvalidValueError("Frequency out of range")
```

## Threading Model

GUI uses background threads for radio operations:

```python
# wxui/radiothread.py

class RadioThread(threading.Thread):
    def run(self):
        try:
            # Perform radio operation
            self.radio.sync_in()
            wx.PostEvent(self.parent, RadioJobEvent(success=True))
        except Exception as e:
            wx.PostEvent(self.parent, RadioJobEvent(success=False, error=e))
```

**Important:**
- Radio operations run in background threads
- UI updates via `wx.PostEvent()`
- Never block the main GUI thread

## Performance Considerations

### 1. Memory Image Caching
- Downloaded images cached in `_mmap`
- Bitwise parsing done once in `process_mmap()`
- Avoid re-parsing on every `get_memory()` call

### 2. Bulk Operations
- Use `get_memories()` instead of multiple `get_memory()` calls when possible
- Batch serial communication to reduce overhead

### 3. Lazy Loading
- Network sources fetch on demand
- Large settings groups loaded progressively

## Security Considerations

### 1. Serial Port Access
- Validate port names before opening
- Handle permission errors gracefully
- Close ports on errors to avoid locks

### 2. File Operations
- Validate file paths (no path traversal)
- Check file sizes before loading
- Handle malformed images safely

### 3. Network Sources
- Use HTTPS where possible
- Validate/sanitize API responses
- Handle network errors gracefully
- Rate limiting for API calls

## Testing Integration

Architecture supports comprehensive testing:

```python
# tests/test_drivers.py

def test_edges(radio):
    """Test edge cases for all drivers"""
    rf = radio.get_features()

    # Test memory bounds
    mem = radio.get_memory(rf.memory_bounds[0])
    assert mem.number == rf.memory_bounds[0]

    # Test invalid memory
    with pytest.raises(errors.InvalidMemoryLocation):
        radio.get_memory(rf.memory_bounds[1] + 1)
```

Dynamic test generation creates tests for all 184 drivers automatically.

## Summary

CHIRP's architecture provides:
- **Extensibility:** Easy to add new radio drivers
- **Reusability:** Common base classes reduce duplication
- **Testability:** Clear interfaces enable comprehensive testing
- **Maintainability:** Separation of concerns (UI, drivers, core)
- **Platform Independence:** Abstraction layer for OS differences

The plugin pattern allows the community to contribute drivers for new radios without modifying core code, while the bitwise DSL makes it efficient to define complex memory structures.
