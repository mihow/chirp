# CLAUDE.md - AI Agent Development Guide for CHIRP

## IMPORTANT - Cost Optimization

**Every call to the AI model API incurs a cost and requires electricity. Be smart and make as few requests as possible. Each request gets subsequently more expensive as the context increases.**

## Efficient Development Practices

### Optimize API Usage
- **Add learnings and gotchas to this file** to avoid repeating mistakes and trial & error
- **Ignore line length and type errors until the very end**; use command line tools to fix those (`black`, `flake8`)
- **Always prefer command line tools** to avoid expensive API requests (e.g., use `git` and `jq` instead of reading whole files)
- **Use bulk operations and prefetch patterns** to minimize database queries

### Think Holistically
- **What is the PURPOSE of this tool?** Why is it failing on this issue?
- **Is this a symptom of a larger architectural problem?** Take a step back and analyze the root cause
- **Evaluate alternatives** before implementing complex solutions

### Development Best Practices
- **Commit often** - Small, focused commits make debugging easier
- **Use TDD whenever possible** - Tests first, implementation second
- **Keep it simple** - Always think hard and evaluate more complex approaches and alternative approaches before moving forward

---

## Project Overview: CHIRP

**CHIRP** (https://www.chirpmyradio.com) is a cross-platform cross-radio programming tool for amateur radio (ham radio) operators.

### Core Purpose
- Program memory channels on 184+ radio models from various manufacturers (Yaesu, Icom, Baofeng, Kenwood, etc.)
- Download/upload configurations from/to physical radios via serial connection
- Import/export radio configurations between different radio models
- Manage radio settings, banks, and memories
- Query online repeater databases (RadioReference, RepeaterBook, DMR-MARC)

### Technology Stack
- **Language:** Python 3.10+ (moving to 3.12)
- **GUI:** wxPython 4.0-4.2.0
- **CLI:** Custom command-line interface (`chirpc`)
- **Testing:** pytest with pytest-xdist for parallel execution
- **Type Checking:** mypy
- **Code Style:** flake8, PEP8 (with custom exceptions)
- **Serial Communication:** pyserial
- **Build System:** tox for test orchestration

### Key Architecture Patterns

#### 1. Plugin/Driver System
Each radio model has its own driver that inherits from base classes:
- `CloneModeRadio` - For radios that download/upload full memory images
- `LiveRadio` - For real-time radio communication
- `FileBackedRadio` - For file-based radio configurations
- `NetworkSourceRadio` - For online data sources

**Location:** `/chirp/drivers/` (184 driver files)

#### 2. Registry Pattern
Central driver registration using decorators:
```python
@directory.register
class MyRadio(chirp_common.CloneModeRadio):
    VENDOR = "Example"
    MODEL = "Radio-1000"
```
**Location:** `/chirp/directory.py`

#### 3. Bitwise Memory Structure DSL
Custom C-like language for defining radio memory layouts:
- Parses binary memory structures
- Handles endianness, BCD encoding, bitfields
- Uses Lark parser for grammar

**Location:** `/chirp/bitwise.py`

#### 4. Settings Framework
Typed settings system for radio configuration:
- `RadioSettingGroup` - Groups of settings
- `RadioSetting` - Individual setting with validation
- Value types: Integer, String, List, Boolean

**Location:** `/chirp/settings.py`

### Directory Structure

```
chirp/
├── chirp_common.py          # Core abstractions (Memory, RadioFeatures, base classes)
├── directory.py             # Driver registry and discovery
├── bitwise.py               # Memory structure parser (~1,400 lines)
├── settings.py              # Settings framework
├── memmap.py                # Memory map abstractions
├── platform.py              # Platform-specific code (Win/Linux/macOS)
├── errors.py                # Exception hierarchy
├── import_logic.py          # Memory import/export between radios
├── logger.py                # Logging configuration
├── util.py                  # Utilities (hexprint, BCD encoding)
├── bandplan*.py             # Frequency band plans (NA, IARU R1/R2/R3, Australia)
├── cli/                     # Command-line interface (3 files)
├── drivers/                 # 184 radio drivers
├── wxui/                    # wxPython GUI (19 modules)
├── sources/                 # Network data sources (7 files)
├── share/                   # Icons, images, desktop files
├── stock_configs/           # Pre-configured channel lists (20 CSV files)
└── locale/                  # Internationalization

tests/
├── images/                  # Test images (184+ .img files for drivers)
├── unit/                    # Unit tests (29 test files)
├── test_drivers.py          # Dynamic driver test generation
├── test_banks.py            # Bank functionality tests
├── test_brute_force.py      # Edge case testing
├── test_clone.py            # Clone operation tests
├── test_settings.py         # Settings tests
├── conftest.py              # Pytest configuration
└── driver_xfails.yaml       # Known test failures

tools/
├── cpep8.py                 # Custom PEP8 checker
├── check_commit.sh          # Commit validation
├── fast-driver.py           # Fast driver testing
└── serialsniff.c            # Serial communication sniffer
```

### Testing Infrastructure

#### Test Execution
```bash
# Style checks
tox -e style

# Unit tests
tox -e unit

# All driver tests
tox -e driver

# Fast single driver test
python tools/fast-driver.py chirp/drivers/ft60.py

# Run tests in parallel
pytest -n auto
```

#### Test Types
1. **Style tests:** PEP8, flake8, mypy
2. **Unit tests:** 29 test files in `tests/unit/`
3. **Driver tests:** Automated tests for all 184 drivers
4. **Integration tests:** Clone, settings, banks, edges

#### CI/CD (GitHub Actions)
- Style checks on every PR
- Unit tests on Ubuntu 22.04
- Driver tests on Python 3.10 and 3.12
- Auto-generated support matrix

### Code Quality Standards

#### Commit Guidelines
- **Rebase-only** (no merge commits)
- Reference CHIRP issues: `Fixes #1234`
- Meaningful first line for mailing list
- Must use `MemoryMapBytes` for new drivers (not deprecated `MemoryMap`)
- Test images required for new drivers

#### Code Style
- PEP8 compliance (with exceptions in `tools/cpep8.exceptions`)
- Type hints required (mypy checking)
- Python 3.10+ only (no Python 2 compatibility)
- GPLv3 license for all code

#### Pre-commit Hooks
```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### Common Development Tasks

#### Creating a New Radio Driver

1. **Create driver file:** `chirp/drivers/myradio.py`
2. **Inherit from base class:**
   ```python
   @directory.register
   class MyRadio(chirp_common.CloneModeRadio):
       VENDOR = "Manufacturer"
       MODEL = "Model-123"
       BAUD_RATE = 9600
   ```
3. **Define memory map:** Use bitwise DSL or `MemoryMapBytes`
4. **Implement methods:**
   - `get_features()` - Return `RadioFeatures` instance
   - `get_memory(number)` - Get memory at position
   - `set_memory(memory)` - Set memory at position
   - `sync_in()` - Download from radio
   - `sync_out()` - Upload to radio
5. **Add test image:** Place `.img` file in `tests/images/`
6. **Run tests:** `python tools/fast-driver.py chirp/drivers/myradio.py`

#### Debugging Radio Communication

```bash
# Enable debug logging
export CHIRP_DEBUG=y

# Run with verbose output
chirpc --verbose download /dev/ttyUSB0 output.img

# Use serial sniffer (Linux)
gcc -o serialsniff tools/serialsniff.c
./serialsniff /dev/ttyUSB0
```

#### Running Specific Tests

```bash
# Test single driver
pytest tests/test_drivers.py -k ft60

# Test with coverage
pytest --cov=chirp tests/

# Test specific functionality
pytest tests/unit/test_bitwise.py::TestBitwiseParser
```

### Common Gotchas and Learnings

#### 1. Memory Maps
- **Always use `MemoryMapBytes`** for new drivers (not `MemoryMap`)
- `MemoryMap` is deprecated but kept for compatibility
- Binary data should be treated as bytes, not strings

#### 2. Bitwise Structures
- Endianness matters! Use `#seekto` directives carefully
- BCD encoding is common in radios: `bbcd` type
- Arrays are 0-indexed in bitwise, but radio memory channels often start at 1

#### 3. Serial Communication
- **Baud rate mismatches** cause garbled data
- Some radios need delays between commands
- Always implement proper error handling in `sync_in()`/`sync_out()`
- Test on actual hardware, not just images

#### 4. Testing
- Every driver must have a test image in `tests/images/`
- Test images should be minimal but complete
- Known failures go in `tests/driver_xfails.yaml`
- Use `fast-driver.py` for quick iteration

#### 5. Import/Export
- Not all features translate between radios
- Check `import_logic.py` for compatibility handling
- Test cross-radio imports thoroughly

#### 6. wxPython GUI
- UI operations must run on main thread
- Use `radiothread.py` for background radio operations
- Always handle `RadioError` exceptions

#### 7. Platform Differences
- Serial port names: `/dev/ttyUSB0` (Linux), `COM1` (Windows), `/dev/cu.usbserial` (macOS)
- Path separators handled by `platform.py`
- Test on multiple platforms when possible

### Performance Tips

#### 1. Minimize File Reads
```bash
# Bad: Reading entire file to check one field
python -c "import json; print(json.load(open('config.json'))['version'])"

# Good: Use jq
jq -r '.version' config.json
```

#### 2. Use Git Efficiently
```bash
# Check if file changed without reading
git diff --name-only HEAD file.py

# Get specific info without full log
git log -1 --format='%an' file.py
```

#### 3. Batch Operations
- Use `git add .` instead of multiple `git add` commands
- Use `pytest -n auto` for parallel test execution
- Leverage `import_logic.py` for bulk memory operations

#### 4. Prefer CLI Tools
- `grep` instead of reading files line by line
- `find` instead of recursive directory walking
- `sed`/`awk` for text transformations

### Useful Commands

```bash
# Check which drivers support a feature
grep -r "has_ctone = True" chirp/drivers/

# Find all radios from a vendor
grep -r 'VENDOR = "Yaesu"' chirp/drivers/

# Count supported radio models
ls chirp/drivers/*.py | wc -l

# See test failures
pytest --tb=short tests/

# Generate coverage report
pytest --cov=chirp --cov-report=html tests/

# Validate single driver without full test
python -c "from chirp import directory; directory.get_radio('Yaesu FT-60')"
```

### Resources

- **Website:** https://www.chirpmyradio.com
- **Issue Tracker:** https://chirpmyradio.com/projects/chirp/issues
- **Wiki:** https://chirpmyradio.com/projects/chirp/wiki
- **Developer Docs:** `README.developers`
- **CLI Docs:** `README.chirpc`
- **Installation:** `INSTALL`

### Detailed Documentation

See `/docs/claude/` for in-depth module documentation:
- `architecture.md` - Detailed architecture analysis
- `modules.md` - Module-by-module breakdown
- `testing.md` - Testing strategies and infrastructure
- `drivers.md` - Driver development guide
- `api-reference.md` - Core API documentation

---

## Quick Start for AI Agents

1. **Understand the domain:** Amateur radio, memory channels, repeaters, CTCSS/DCS tones
2. **Study core abstractions:** Read `chirp/chirp_common.py` first
3. **Look at examples:** Check `chirp/drivers/ft60.py` or `chirp/drivers/fake.py`
4. **Run tests early:** Use `tools/fast-driver.py` for quick feedback
5. **Use CLI tools:** Minimize API calls by leveraging `git`, `grep`, `jq`, etc.
6. **Check existing issues:** Search https://chirpmyradio.com/projects/chirp/issues before implementing
7. **Follow commit standards:** Reference issues, rebase-only, meaningful messages
8. **Test thoroughly:** Unit tests, driver tests, and ideally hardware testing

Remember: **Think before you code. Use CLI tools. Commit often. Keep it simple.**
