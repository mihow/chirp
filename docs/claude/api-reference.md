# CHIRP API Reference

Complete API reference for CHIRP core classes and functions.

## Core Data Structures

### `chirp_common.Memory`

Represents a single memory channel.

**Module:** `chirp.chirp_common`

**Attributes:**

| Attribute | Type | Description | Default |
|-----------|------|-------------|---------|
| `number` | `int` | Memory channel number | `0` |
| `extd_number` | `str` | Extended number (e.g., "1A") | `""` |
| `name` | `str` | Alpha tag / memory name | `""` |
| `freq` | `int` | Frequency in Hz | `0` |
| `rtone` | `float` | TX CTCSS tone (Hz) | `88.5` |
| `ctone` | `float` | RX CTCSS tone (Hz) | `88.5` |
| `dtcs` | `int` | DTCS code | `23` |
| `rx_dtcs` | `int` | RX DTCS code | `23` |
| `dtcs_polarity` | `str` | DTCS polarity (NN/NR/RN/RR) | `"NN"` |
| `tmode` | `str` | Tone mode ("", "Tone", "TSQL", "DTCS", "Cross") | `""` |
| `cross_mode` | `str` | Cross tone mode | `"Tone->Tone"` |
| `duplex` | `str` | Duplex mode ("", "+", "-", "split", "off") | `""` |
| `offset` | `int` | TX offset in Hz | `0` |
| `mode` | `str` | Modulation mode (FM, NFM, AM, etc.) | `"FM"` |
| `tuning_step` | `float` | Tuning step in kHz | `5.0` |
| `skip` | `str` | Skip mode ("", "S", "P") | `""` |
| `power` | `PowerLevel` | Power level | `None` |
| `comment` | `str` | Memory comment | `""` |
| `immutable` | `list` | List of immutable field names | `[]` |
| `empty` | `bool` | Is empty/deleted | `False` |

**Example:**

```python
from chirp import chirp_common

mem = chirp_common.Memory()
mem.number = 1
mem.freq = 146520000  # 146.52 MHz
mem.name = "SIMPLEX"
mem.mode = "FM"
mem.duplex = ""
mem.tmode = "Tone"
mem.rtone = 100.0
```

---

### `chirp_common.RadioFeatures`

Defines capabilities and constraints of a radio model.

**Module:** `chirp.chirp_common`

**Attributes:**

| Attribute | Type | Description | Default |
|-----------|------|-------------|---------|
| `memory_bounds` | `tuple` | (min, max) memory channel numbers | `(0, 999)` |
| `has_bank` | `bool` | Supports memory banks | `False` |
| `has_bank_index` | `bool` | Banks have indices | `False` |
| `has_bank_names` | `bool` | Banks can be named | `False` |
| `has_dtcs` | `bool` | DTCS tone support | `True` |
| `has_dtcs_polarity` | `bool` | DTCS polarity support | `True` |
| `has_ctone` | `bool` | CTCSS tone support | `True` |
| `has_cross` | `bool` | Cross-tone mode | `True` |
| `has_rx_dtcs` | `bool` | Separate RX DTCS | `True` |
| `has_tuning_step` | `bool` | Tuning step support | `True` |
| `has_name` | `bool` | Memory name/alpha tag | `True` |
| `has_offset` | `bool` | TX offset support | `True` |
| `has_mode` | `bool` | Mode selection | `True` |
| `has_comment` | `bool` | Memory comments | `False` |
| `has_settings` | `bool` | Settings support | `True` |
| `has_nostep_tuning` | `bool` | Arbitrary frequency | `False` |
| `has_sub_devices` | `bool` | Multiple sub-devices | `False` |
| `can_odd_split` | `bool` | Odd split frequencies | `False` |
| `valid_modes` | `list` | Supported modes | `["FM", "NFM", ...]` |
| `valid_tmodes` | `list` | Supported tone modes | `["", "Tone", ...]` |
| `valid_cross_modes` | `list` | Supported cross modes | `[...]` |
| `valid_power_levels` | `list` | Power levels (`PowerLevel`) | `[]` |
| `valid_duplexes` | `list` | Supported duplex modes | `["", "+", "-", ...]` |
| `valid_skips` | `list` | Supported skip modes | `["", "S", "P"]` |
| `valid_bands` | `list` | Frequency ranges (Hz) | `[(low, high), ...]` |
| `valid_tuning_steps` | `list` | Tuning steps (kHz) | `[5.0, 10.0, ...]` |
| `valid_name_length` | `int` | Max chars in name | `6` |
| `valid_characters` | `str` | Allowed characters | `"A-Z0-9 -"` |
| `memory_deletion` | `bool` | Can delete memories | `True` |

**Example:**

```python
def get_features(self):
    rf = chirp_common.RadioFeatures()
    rf.memory_bounds = (0, 127)
    rf.has_bank = False
    rf.has_ctone = True
    rf.valid_modes = ["FM", "NFM"]
    rf.valid_bands = [(136000000, 174000000), (400000000, 480000000)]
    rf.valid_power_levels = [
        chirp_common.PowerLevel("High", watts=5),
        chirp_common.PowerLevel("Low", watts=1),
    ]
    rf.valid_name_length = 6
    return rf
```

---

### `chirp_common.PowerLevel`

Represents a power level setting.

**Module:** `chirp.chirp_common`

**Constructor:**

```python
PowerLevel(label: str, watts: int = None, dBm: int = None)
```

**Parameters:**
- `label` - Display label (e.g., "High", "Low")
- `watts` - Power in watts (optional)
- `dBm` - Power in dBm (optional)

**Example:**

```python
power_levels = [
    chirp_common.PowerLevel("High", watts=5),
    chirp_common.PowerLevel("Mid", watts=2.5),
    chirp_common.PowerLevel("Low", watts=1),
]
```

---

## Base Radio Classes

### `chirp_common.Radio` (abstract)

Abstract base class for all radios.

**Module:** `chirp.chirp_common`

**Abstract Methods:**

#### `get_features() -> RadioFeatures`

Returns the radio's capabilities.

```python
def get_features(self):
    rf = chirp_common.RadioFeatures()
    # Configure features
    return rf
```

#### `get_memory(number: int) -> Memory`

Returns memory at given channel number.

```python
def get_memory(self, number):
    if number < 0 or number > 127:
        raise errors.InvalidMemoryLocation()

    mem = chirp_common.Memory()
    mem.number = number
    # Populate from radio data
    return mem
```

**Raises:** `errors.InvalidMemoryLocation` if invalid number

#### `set_memory(mem: Memory) -> None`

Sets memory at channel.

```python
def set_memory(self, mem):
    if mem.number < 0 or mem.number > 127:
        raise errors.InvalidMemoryLocation()

    # Write to radio data
```

**Raises:** `errors.InvalidMemoryLocation` if invalid number

#### `erase_memory(number: int) -> None`

Erases/deletes memory at channel.

```python
def erase_memory(self, number):
    mem = chirp_common.Memory()
    mem.number = number
    mem.empty = True
    self.set_memory(mem)
```

**Optional Methods:**

#### `get_memories(lo: int = None, hi: int = None) -> List[Memory]`

Returns list of memories in range.

```python
def get_memories(self, lo=None, hi=None):
    rf = self.get_features()
    lo = lo or rf.memory_bounds[0]
    hi = hi or rf.memory_bounds[1]

    memories = []
    for i in range(lo, hi + 1):
        try:
            mem = self.get_memory(i)
            if not mem.empty:
                memories.append(mem)
        except errors.InvalidMemoryLocation:
            pass
    return memories
```

#### `get_raw_memory(number: int) -> bytes`

Returns raw memory data (for debugging).

```python
def get_raw_memory(self, number):
    return bytes(self._memobj.memory[number])
```

#### `get_settings() -> RadioSettings`

Returns radio settings structure.

```python
from chirp import settings

def get_settings(self):
    top = settings.RadioSettings()
    # Build settings tree
    return top
```

#### `set_settings(settings: RadioSettings) -> None`

Applies radio settings.

```python
def set_settings(self, settings):
    for element in settings:
        # Apply each setting
        pass
```

#### `get_bank_model() -> BankModel`

Returns bank model (if radio has banks).

```python
def get_bank_model(self):
    return MyRadioBankModel(self)
```

#### `get_sub_devices() -> List[Radio]`

Returns sub-device instances (for multi-band radios).

```python
def get_sub_devices(self):
    return [VHFRadio(self._mmap), UHFRadio(self._mmap)]
```

---

### `chirp_common.CloneModeRadio`

Base class for radios that download/upload full memory image.

**Module:** `chirp.chirp_common`

**Inherits:** `FileBackedRadio` → `Radio`

**Required Methods:**

#### `sync_in() -> None`

Downloads memory image from radio.

```python
def sync_in(self):
    data = self._download()
    self._mmap = memmap.MemoryMapBytes(data)
    self.process_mmap()
```

**May raise:** `errors.RadioError` on communication failure

#### `sync_out() -> None`

Uploads memory image to radio.

```python
def sync_out(self):
    self._upload()
```

**May raise:** `errors.RadioError` on communication failure

#### `process_mmap() -> None`

Parses memory map after download.

```python
def process_mmap(self):
    self._memobj = bitwise.parse(MEM_FORMAT, self._mmap)
```

**Class Attributes:**

- `VENDOR` - Manufacturer name (e.g., "Yaesu")
- `MODEL` - Model name (e.g., "FT-60")
- `BAUD_RATE` - Serial baud rate (e.g., `9600`)

**Instance Attributes:**

- `pipe` - Serial port object (set by CHIRP before sync)
- `status_fn` - Progress callback function
- `_mmap` - `MemoryMapBytes` instance
- `_memobj` - Parsed bitwise structure

---

### `chirp_common.LiveRadio`

Base class for radios with real-time communication (no clone mode).

**Module:** `chirp.chirp_common`

**Inherits:** `Radio`

**Implementation:**

Each `get_memory()` / `set_memory()` communicates directly with radio.

```python
class MyLiveRadio(chirp_common.LiveRadio):
    def get_memory(self, number):
        # Send command to radio
        data = self._read_memory_from_radio(number)
        # Parse and return
        return mem

    def set_memory(self, mem):
        # Send command to radio
        self._write_memory_to_radio(mem)
```

---

### `chirp_common.NetworkSourceRadio`

Base class for online repeater databases.

**Module:** `chirp.chirp_common`

**Required Method:**

#### `do_fetch(freq: int, coords: tuple) -> List[Memory]`

Fetches repeaters from online source.

```python
def do_fetch(self, freq, coords):
    """
    Args:
        freq: Frequency in Hz
        coords: (latitude, longitude) tuple

    Returns:
        List of Memory objects
    """
    import requests

    response = requests.get(f"https://api.example.com/repeaters?freq={freq}")
    memories = []
    for data in response.json():
        mem = chirp_common.Memory()
        mem.freq = data['frequency']
        mem.name = data['callsign']
        # ... populate other fields ...
        memories.append(mem)
    return memories
```

---

## Settings Framework

### `settings.RadioSettings`

Top-level settings container.

**Module:** `chirp.settings`

**Methods:**

```python
rs = settings.RadioSettings()
rs.append(group)  # Add setting group
```

---

### `settings.RadioSettingGroup`

Group of related settings.

**Module:** `chirp.settings`

**Constructor:**

```python
RadioSettingGroup(name: str, label: str)
```

**Methods:**

```python
group = settings.RadioSettingGroup("basic", "Basic Settings")
group.append(setting)  # Add setting to group
```

---

### `settings.RadioSetting`

Individual setting.

**Module:** `chirp.settings`

**Constructor:**

```python
RadioSetting(name: str, label: str, value: RadioSettingValue)
```

**Parameters:**
- `name` - Setting path (e.g., "settings.squelch")
- `label` - Display label (e.g., "Squelch Level")
- `value` - Setting value object

**Methods:**

```python
setting.get_name()  # Returns name
setting.get_label()  # Returns label
setting.value  # Access value object
```

---

### Setting Value Types

#### `settings.RadioSettingValueInteger`

Integer setting with bounds.

```python
RadioSettingValueInteger(min: int, max: int, current: int)
```

**Example:**

```python
value = settings.RadioSettingValueInteger(0, 9, 5)
value.get_min()  # 0
value.get_max()  # 9
value.get_value()  # 5
value.set_value(7)
```

#### `settings.RadioSettingValueFloat`

Float setting with bounds.

```python
RadioSettingValueFloat(min: float, max: float, current: float, resolution: float = 0.1)
```

**Example:**

```python
value = settings.RadioSettingValueFloat(0.0, 10.0, 5.5, 0.1)
value.set_value(6.3)
```

#### `settings.RadioSettingValueBoolean`

Boolean setting.

```python
RadioSettingValueBoolean(current: bool)
```

**Example:**

```python
value = settings.RadioSettingValueBoolean(True)
value.get_value()  # True
value.set_value(False)
```

#### `settings.RadioSettingValueList`

Choice from list.

```python
RadioSettingValueList(options: list, current: str)
```

**Example:**

```python
options = ["Off", "Low", "High"]
value = settings.RadioSettingValueList(options, "Low")
value.get_options()  # ["Off", "Low", "High"]
value.get_value()  # "Low"
value.set_value("High")
```

#### `settings.RadioSettingValueString`

String setting.

```python
RadioSettingValueString(min_len: int, max_len: int, current: str)
```

**Example:**

```python
value = settings.RadioSettingValueString(0, 16, "My Radio")
value.set_value("New Name")
```

---

## Memory Map

### `memmap.MemoryMapBytes`

Binary memory map using bytes.

**Module:** `chirp.memmap`

**Constructor:**

```python
MemoryMapBytes(data: bytes = None)
```

**Methods:**

#### `get(start: int, length: int) -> bytes`

Get byte range.

```python
chunk = mmap.get(0x0100, 256)
```

#### `set(start: int, data: bytes) -> None`

Set byte range.

```python
mmap.set(0x0100, b'\xFF' * 256)
```

#### `get_byte_compatible() -> bytes`

Get all data as bytes.

```python
all_data = mmap.get_byte_compatible()
```

#### Indexing

```python
# Get single byte
byte = mmap[0]

# Get slice
chunk = mmap[0:16]

# Set single byte
mmap[0] = 0x12

# Set slice
mmap[0:4] = b'\x12\x34\x56\x78'
```

---

## Bitwise Parser

### `bitwise.parse()`

Parse bitwise definition and map to binary data.

**Module:** `chirp.bitwise`

**Function:**

```python
parse(definition: str, data: bytes) -> StructDataElement
```

**Parameters:**
- `definition` - Bitwise DSL string
- `data` - Binary data (bytes or MemoryMapBytes)

**Returns:** Parsed structure object

**Example:**

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

# Access
mem.memory[0].freq = 146520000
mem.memory[0].name = "CALL"

# Read back
freq = int(mem.memory[0].freq)
name = str(mem.memory[0].name)
```

---

## Directory Registry

### `directory.register`

Decorator to register a radio driver.

**Module:** `chirp.directory`

**Usage:**

```python
from chirp import directory

@directory.register
class MyRadio(chirp_common.CloneModeRadio):
    VENDOR = "Vendor"
    MODEL = "Model-123"
```

---

### `directory.get_radio()`

Get radio class by model name.

**Module:** `chirp.directory`

**Function:**

```python
get_radio(model: str) -> Type[Radio]
```

**Parameters:**
- `model` - Model name in format "Vendor Model"

**Returns:** Radio class

**Raises:** `KeyError` if not found

**Example:**

```python
from chirp import directory

RadioClass = directory.get_radio("Yaesu FT-60")
radio = RadioClass("ft60.img")
```

---

### `directory.get_radio_by_image()`

Detect radio type from image file.

**Module:** `chirp.directory`

**Function:**

```python
get_radio_by_image(filename: str) -> Radio
```

**Parameters:**
- `filename` - Path to image file

**Returns:** Radio instance

**Raises:** `errors.ImageDetectFailed` if detection fails

**Example:**

```python
from chirp import directory

radio = directory.get_radio_by_image("unknown.img")
print(f"Detected: {radio.VENDOR} {radio.MODEL}")
```

---

## Bank Model

### `chirp_common.BankModel` (abstract)

Abstract base for bank management.

**Module:** `chirp.chirp_common`

**Abstract Methods:**

#### `get_num_banks() -> int`

Returns number of banks.

#### `get_banks() -> List[Bank]`

Returns list of bank objects.

#### `add_memory_to_bank(mem: Memory, bank: Bank) -> None`

Adds memory to bank.

#### `remove_memory_from_bank(mem: Memory, bank: Bank) -> None`

Removes memory from bank.

#### `get_memory_mappings(mem: Memory) -> List[Bank]`

Returns banks containing this memory.

**Optional Methods:**

#### `get_bank_by_index(index: int) -> Bank`

Returns bank by index.

---

### `chirp_common.Bank`

Represents a memory bank.

**Module:** `chirp.chirp_common`

**Constructor:**

```python
Bank(model: BankModel, index: str, name: str)
```

**Methods:**

```python
bank.get_name()  # Returns name
bank.set_name(name)  # Sets name (if supported)
bank.get_index()  # Returns index
```

---

## Error Handling

### Error Classes

**Module:** `chirp.errors`

#### `RadioError`

Base exception for all radio errors.

```python
raise errors.RadioError("General error")
```

#### `InvalidMemoryLocation`

Invalid memory channel number.

```python
if number < 0 or number > 127:
    raise errors.InvalidMemoryLocation(f"Invalid channel: {number}")
```

#### `InvalidDataError`

Invalid data format.

```python
raise errors.InvalidDataError("Corrupt image file")
```

#### `InvalidValueError`

Invalid value for field.

```python
if freq < 136000000:
    raise errors.InvalidValueError(f"Frequency too low: {freq}")
```

#### `UnsupportedToneError`

Tone not supported by radio.

```python
if tone not in supported_tones:
    raise errors.UnsupportedToneError(f"Tone {tone} not supported")
```

#### `ImageDetectFailed`

Could not detect radio from image.

```python
raise errors.ImageDetectFailed("Unknown file format")
```

---

## Constants

### Tone Lists

**Module:** `chirp.chirp_common`

#### `TONES`

List of standard CTCSS tones in Hz:

```python
chirp_common.TONES = [67.0, 69.3, 71.9, ..., 250.3]
```

#### `DTCS_CODES`

List of standard DTCS codes:

```python
chirp_common.DTCS_CODES = [23, 25, 26, 31, ..., 754]
```

### Mode Lists

#### `MODES`

List of standard modulation modes:

```python
chirp_common.MODES = ["FM", "NFM", "AM", "NAM", "DV", "USB", "LSB", "CW", ...]
```

### Character Sets

```python
chirp_common.CHARSET_UPPER_NUMERIC = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
chirp_common.CHARSET_ALPHANUMERIC = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
```

---

## Utility Functions

### `util.hexprint()`

Pretty-print binary data as hex dump.

**Module:** `chirp.util`

```python
hexprint(data: bytes, addrfmt: str = None) -> str
```

**Example:**

```python
from chirp import util

data = b'\x01\x02\x03\x04'
print(util.hexprint(data))
# 0000: 01 02 03 04
```

---

### `util.bcd_encode()`

Encode integer as BCD.

**Module:** `chirp.util`

```python
bcd_encode(value: int, width: int = 2) -> bytes
```

**Example:**

```python
from chirp import util

bcd = util.bcd_encode(123, 2)  # b'\x01\x23'
```

---

### `util.bcd_decode()`

Decode BCD to integer.

**Module:** `chirp.util`

```python
bcd_decode(data: bytes) -> int
```

**Example:**

```python
from chirp import util

value = util.bcd_decode(b'\x01\x23')  # 123
```

---

## Platform

### `platform.get_platform()`

Get platform-specific instance.

**Module:** `chirp.platform`

```python
from chirp import platform

plat = platform.get_platform()
config_dir = plat.config_dir()
```

**Methods:**

- `config_dir()` - Configuration directory
- `log_dir()` - Log directory
- `list_serial_ports()` - Available serial ports

---

## Import Logic

### `import_logic.import_mem()`

Import memory between radios with feature translation.

**Module:** `chirp.import_logic`

```python
import_mem(dst_radio: Radio, src_mem: Memory, overrides: dict = None) -> Memory
```

**Parameters:**
- `dst_radio` - Destination radio
- `src_mem` - Source memory
- `overrides` - Optional field overrides

**Returns:** Translated memory for destination radio

**Raises:** `errors.InvalidValueError` if incompatible

**Example:**

```python
from chirp import import_logic

src_radio = directory.get_radio("Yaesu FT-60")("ft60.img")
dst_radio = directory.get_radio("Baofeng UV-5R")("uv5r.img")

src_mem = src_radio.get_memory(1)
dst_mem = import_logic.import_mem(dst_radio, src_mem)
dst_radio.set_memory(dst_mem)
```

---

## Summary

This API reference covers the essential interfaces for CHIRP development. For complete details, refer to the source code in `chirp/chirp_common.py` and related modules.

Key patterns:
- **Data structures:** `Memory`, `RadioFeatures`, `PowerLevel`
- **Base classes:** `Radio`, `CloneModeRadio`, `LiveRadio`
- **Settings:** `RadioSettings`, `RadioSetting`, value types
- **Memory maps:** `MemoryMapBytes`
- **Parsing:** `bitwise.parse()`
- **Registry:** `@directory.register`, `get_radio()`
- **Error handling:** Exception hierarchy in `errors`

Consult example drivers in `chirp/drivers/` for real-world usage.
