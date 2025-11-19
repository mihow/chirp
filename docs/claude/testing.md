# CHIRP Testing Guide

## Testing Infrastructure

CHIRP has a comprehensive testing infrastructure covering style checks, unit tests, and driver tests for all 184 radio drivers.

## Test Framework

### Tools Used

- **pytest** (7.1.3) - Test framework
- **pytest-xdist** - Parallel test execution
- **pytest-html** - HTML test reports
- **tox** - Test orchestration across environments
- **mypy** - Type checking
- **flake8** - Code style checking
- **pep8** - PEP8 compliance checking
- **pre-commit** - Git hooks for automated checks

### Test Organization

```
tests/
├── __init__.py                  # Test loader and dynamic test generation
├── conftest.py                  # Pytest configuration
├── driver_xfails.yaml           # Known test failures
├── images/                      # Test image files (184+ .img files)
│   ├── Yaesu_FT-60.img
│   ├── Baofeng_UV-5R.img
│   └── ...
├── unit/                        # Unit tests (29 files)
│   ├── test_bitwise.py
│   ├── test_import_logic.py
│   ├── test_platform.py
│   └── ...
├── test_drivers.py              # Dynamic driver tests
├── test_banks.py                # Bank functionality tests
├── test_brute_force.py          # Edge case testing
├── test_clone.py                # Clone operation tests
├── test_detect.py               # Image detection tests
├── test_edges.py                # Edge case validation
├── test_settings.py             # Settings tests
└── test_copy_all.py             # Cross-radio copy tests
```

## Running Tests

### Quick Test Commands

```bash
# Run all tests
pytest

# Run tests in parallel (faster)
pytest -n auto

# Run specific test file
pytest tests/test_bitwise.py

# Run specific test
pytest tests/unit/test_bitwise.py::TestBitwiseParser::test_basic_struct

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=chirp --cov-report=html

# Generate HTML report
pytest --html=report.html --self-contained-html
```

### Using Tox

Tox provides standardized test environments:

```bash
# Run style checks
tox -e style

# Run unit tests
tox -e unit

# Run all driver tests (slow - 184 drivers)
tox -e driver

# Run fast subset of driver tests
tox -e fast-driver

# List all environments
tox -l
```

**Tox Environments (from `tox.ini`):**

- `style` - PEP8, flake8, mypy type checking
- `unit` - Unit tests only
- `driver` - All driver tests
- `fast-driver` - Quick driver tests
- `py310`, `py312` - Python version-specific tests

### Fast Driver Testing

For quick iteration during development:

```bash
# Test single driver
python tools/fast-driver.py chirp/drivers/ft60.py

# Test multiple drivers
python tools/fast-driver.py chirp/drivers/ft60.py chirp/drivers/uv5r.py

# Test with pytest options
python tools/fast-driver.py chirp/drivers/ft60.py -- -v
```

This is much faster than running the full test suite.

## Test Types

### 1. Style Tests

**What:** Code style and static analysis.

**How to run:**
```bash
tox -e style
```

**Checks:**

#### PEP8 Compliance
```bash
python tools/cpep8.py chirp/
```

Custom PEP8 checker with exceptions in `tools/cpep8.exceptions`:
- Allows specific line length exceptions
- Ignores certain PEP8 rules for legacy code

#### Flake8
```bash
flake8 chirp/
```

Configured in `setup.cfg`:
```ini
[flake8]
max-line-length = 100
exclude = .git,__pycache__,build,dist,.tox
ignore = E501,W503
```

#### MyPy Type Checking
```bash
mypy chirp/
```

Configured in `.mypy.ini`:
```ini
[mypy]
python_version = 3.10
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = False
```

**Common Style Failures:**

1. **Line too long** - Wrap lines at 100 characters
2. **Unused imports** - Remove or comment with `# noqa`
3. **Missing type hints** - Add type annotations
4. **Whitespace issues** - Run `autopep8` or `black`

### 2. Unit Tests

**What:** Test individual modules and functions in isolation.

**Location:** `tests/unit/`

**How to run:**
```bash
tox -e unit
pytest tests/unit/
```

**Key Unit Tests:**

#### `test_bitwise.py`
Tests the bitwise memory structure parser.

```python
def test_basic_struct():
    """Test basic structure parsing"""
    definition = """
    struct {
      u8 foo;
      u16 bar;
    } test;
    """
    data = b'\x01\x02\x03\x00'
    obj = bitwise.parse(definition, data)
    assert obj.test.foo == 1
    assert obj.test.bar == 0x0302  # Little-endian
```

#### `test_import_logic.py`
Tests memory import between radios.

```python
def test_import_tone():
    """Test tone mode import"""
    src = Memory()
    src.freq = 146520000
    src.tmode = "Tone"
    src.rtone = 100.0

    dst = import_logic.import_mem(dst_radio, src)
    assert dst.tmode == "Tone"
    assert dst.rtone == 100.0
```

#### `test_platform.py`
Tests platform-specific functionality.

```python
def test_config_dir():
    """Test config directory detection"""
    platform = get_platform()
    config = platform.config_dir()
    assert os.path.exists(config) or True  # May not exist yet
```

#### `test_settings.py`
Tests settings framework.

```python
def test_radio_setting_value_integer():
    """Test integer setting value"""
    val = RadioSettingValueInteger(0, 10, 5)
    assert val.get_value() == 5

    val.set_value(7)
    assert val.get_value() == 7

    with pytest.raises(ValueError):
        val.set_value(11)  # Out of range
```

#### Other Unit Tests
- `test_bandplan.py` - Band plan validation
- `test_csv.py` - CSV import/export
- `test_logger.py` - Logging functionality
- `test_memmap.py` - Memory map operations
- `test_util.py` - Utility functions

**Writing Unit Tests:**

```python
import pytest
from chirp import module_to_test

class TestFeature:
    def setup_method(self):
        """Run before each test"""
        self.obj = module_to_test.SomeClass()

    def teardown_method(self):
        """Run after each test"""
        pass

    def test_basic_functionality(self):
        """Test basic behavior"""
        result = self.obj.method()
        assert result == expected

    def test_error_handling(self):
        """Test error cases"""
        with pytest.raises(ValueError):
            self.obj.method(invalid_input)

    @pytest.mark.parametrize("input,expected", [
        (1, 2),
        (2, 4),
        (3, 6),
    ])
    def test_multiple_cases(self, input, expected):
        """Test multiple inputs"""
        assert self.obj.double(input) == expected
```

### 3. Driver Tests

**What:** Automated tests for all 184 radio drivers.

**Location:** `tests/test_drivers.py` (dynamic test generation)

**How to run:**
```bash
# All drivers (slow)
tox -e driver
pytest tests/test_drivers.py

# Single driver
pytest tests/test_drivers.py -k "FT-60"

# Fast subset
tox -e fast-driver
```

**Dynamic Test Generation:**

The test framework automatically generates tests for each driver:

```python
# tests/__init__.py

def _get_test_images():
    """Find all test images"""
    images = []
    for file in os.listdir("tests/images"):
        if file.endswith(".img"):
            images.append(file)
    return images

# Generate test for each image
for image in _get_test_images():
    radio_class = directory.get_radio_by_image(f"tests/images/{image}")
    # Create test functions
    pytest_generate_tests(radio_class, image)
```

**Test Cases Generated:**

Each driver is tested for:

1. **Clone In/Out** - Download and upload
2. **Get/Set Memory** - Read and write memories
3. **Edges** - Boundary conditions
4. **Banks** - Bank operations (if supported)
5. **Settings** - Settings get/set (if supported)
6. **Brute Force** - All possible values
7. **Copy** - Cross-radio copying

**Test Image Requirements:**

Every driver must have a test image:
- Filename: `Vendor_Model.img`
- Location: `tests/images/`
- Content: Valid radio memory image
- Size: Should be minimal but complete

**Example:**
```
tests/images/Yaesu_FT-60.img
tests/images/Baofeng_UV-5R.img
tests/images/Icom_IC-V86.img
```

### 4. Edge Case Tests

**What:** Test boundary conditions and edge cases.

**Location:** `tests/test_edges.py`

**Tests:**

```python
def test_memory_bounds(radio):
    """Test memory boundaries"""
    rf = radio.get_features()

    # Test lower bound
    mem = radio.get_memory(rf.memory_bounds[0])
    assert mem.number == rf.memory_bounds[0]

    # Test upper bound
    mem = radio.get_memory(rf.memory_bounds[1])
    assert mem.number == rf.memory_bounds[1]

    # Test out of bounds (should raise)
    with pytest.raises(errors.InvalidMemoryLocation):
        radio.get_memory(rf.memory_bounds[1] + 1)

def test_frequency_limits(radio):
    """Test frequency edge cases"""
    rf = radio.get_features()
    for low, high in rf.valid_bands:
        # Test at edges
        test_freq(radio, low)
        test_freq(radio, high)

        # Test outside (should fail validation)
        with pytest.raises(errors.InvalidValueError):
            test_freq(radio, low - 1)
```

### 5. Bank Tests

**What:** Test bank functionality for radios that support banks.

**Location:** `tests/test_banks.py`

**Tests:**

```python
def test_bank_names(radio):
    """Test bank naming"""
    if not radio.get_features().has_bank:
        pytest.skip("Radio does not support banks")

    banks = radio.get_bank_model()
    bank = banks.get_bank_by_index(0)

    # Test get name
    name = bank.get_name()

    # Test set name (if supported)
    if radio.get_features().has_bank_names:
        bank.set_name("TEST")
        assert bank.get_name() == "TEST"

def test_bank_membership(radio):
    """Test adding/removing memories from banks"""
    if not radio.get_features().has_bank:
        pytest.skip("Radio does not support banks")

    banks = radio.get_bank_model()
    bank = banks.get_bank_by_index(0)
    mem = radio.get_memory(0)

    # Add to bank
    banks.add_memory_to_bank(mem, bank)

    # Check membership
    assert mem in bank.get_memories()

    # Remove from bank
    banks.remove_memory_from_bank(mem, bank)
    assert mem not in bank.get_memories()
```

### 6. Settings Tests

**What:** Test radio settings get/set functionality.

**Location:** `tests/test_settings.py`

**Tests:**

```python
def test_settings_roundtrip(radio):
    """Test settings can be read and written back"""
    if not radio.get_features().has_settings:
        pytest.skip("Radio does not support settings")

    # Get original settings
    settings1 = radio.get_settings()

    # Apply settings
    radio.set_settings(settings1)

    # Get again
    settings2 = radio.get_settings()

    # Compare (should be identical)
    assert_settings_equal(settings1, settings2)

def test_setting_validation(radio):
    """Test setting value validation"""
    if not radio.get_features().has_settings:
        pytest.skip("Radio does not support settings")

    settings = radio.get_settings()

    # Find integer setting
    for element in settings:
        if isinstance(element.value, RadioSettingValueInteger):
            # Test valid value
            element.value.set_value(element.value.get_min())
            element.value.set_value(element.value.get_max())

            # Test invalid value
            with pytest.raises(ValueError):
                element.value.set_value(element.value.get_max() + 1)
            break
```

### 7. Clone Tests

**What:** Test download/upload operations.

**Location:** `tests/test_clone.py`

**Tests:**

```python
def test_clone_from_file(radio):
    """Test loading from file"""
    # Radio should already be loaded from test image
    mem = radio.get_memory(0)
    assert mem is not None

def test_clone_from_radio(radio, mock_serial):
    """Test cloning from hardware radio (mocked)"""
    mock_serial.setup_response(b'test_data')

    radio.pipe = mock_serial
    radio.sync_in()

    # Verify data received
    assert len(radio._mmap) > 0
```

### 8. Brute Force Tests

**What:** Test all possible values for memory fields.

**Location:** `tests/test_brute_force.py`

**Tests:**

```python
def test_all_tones(radio):
    """Test all valid tones"""
    rf = radio.get_features()

    if not rf.has_ctone:
        pytest.skip("No tone support")

    mem = radio.get_memory(0)

    for tone in chirp_common.TONES:
        mem.rtone = tone
        radio.set_memory(mem)
        mem2 = radio.get_memory(0)
        assert abs(mem2.rtone - tone) < 0.1  # Allow rounding

def test_all_modes(radio):
    """Test all valid modes"""
    rf = radio.get_features()

    mem = radio.get_memory(0)

    for mode in rf.valid_modes:
        mem.mode = mode
        radio.set_memory(mem)
        mem2 = radio.get_memory(0)
        assert mem2.mode == mode

def test_all_power_levels(radio):
    """Test all power levels"""
    rf = radio.get_features()

    if not rf.valid_power_levels:
        pytest.skip("No power level support")

    mem = radio.get_memory(0)

    for power in rf.valid_power_levels:
        mem.power = power
        radio.set_memory(mem)
        mem2 = radio.get_memory(0)
        assert mem2.power == power
```

## Known Test Failures

Some tests are expected to fail for specific drivers due to known issues. These are tracked in `tests/driver_xfails.yaml`:

```yaml
# tests/driver_xfails.yaml

Yaesu_FT-60:
  - test_edges:
      reason: "Known issue with edge frequencies"
  - test_brute_force_dtcs:
      reason: "DTCS 023 not supported"

Baofeng_UV-5R:
  - test_clone:
      reason: "Clone requires physical radio"
```

**Usage in tests:**

```python
@pytest.mark.xfail(reason="Known issue #1234")
def test_something(radio):
    pass
```

## CI/CD Integration

### GitHub Actions

**Workflows (`.github/workflows/`):**

#### `style.yml`
```yaml
name: Style Checks
on: [pull_request]
jobs:
  style:
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v2
      - name: Run style checks
        run: tox -e style
```

#### `unit.yml`
```yaml
name: Unit Tests
on: [pull_request]
jobs:
  unit:
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v2
      - name: Run unit tests
        run: tox -e unit
```

#### `driver.yml`
```yaml
name: Driver Tests
on: [pull_request]
strategy:
  matrix:
    python: ["3.10", "3.12"]
jobs:
  driver:
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v2
      - name: Run driver tests
        run: tox -e driver
```

**Status Checks:**
All PRs must pass:
- Style checks
- Unit tests
- Driver tests on Python 3.10 and 3.12

## Pre-commit Hooks

Install pre-commit hooks to run tests before committing:

```bash
# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files

# Skip hooks (not recommended)
git commit --no-verify
```

**Configuration (`.pre-commit-config.yaml`):**

```yaml
repos:
  - repo: local
    hooks:
      - id: style
        name: Style checks
        entry: tox -e style
        language: system
        pass_filenames: false

      - id: unit
        name: Unit tests
        entry: tox -e unit
        language: system
        pass_filenames: false
```

## Writing Tests for New Drivers

### 1. Create Test Image

```bash
# Download from physical radio
chirpc download /dev/ttyUSB0 tests/images/Vendor_Model.img
```

### 2. Minimal Test

Your driver will automatically be tested if:
- Image exists in `tests/images/`
- Driver is registered with `@directory.register`
- Driver filename matches image

### 3. Add Driver-Specific Tests

```python
# tests/test_myradio.py

import pytest
from tests import base

class TestMyRadio(base.DriverTest):
    """Driver-specific tests"""

    def test_special_feature(self):
        """Test special feature unique to this radio"""
        mem = self.radio.get_memory(0)
        # Test special feature
        assert mem.special_field == expected
```

### 4. Handle Known Failures

If some tests fail for known reasons:

```python
@pytest.mark.xfail(reason="Issue #1234")
def test_problematic_feature(self):
    pass
```

Or add to `tests/driver_xfails.yaml`.

## Test-Driven Development (TDD)

### TDD Workflow

1. **Write test first** (it will fail)
2. **Implement minimum code** to make test pass
3. **Refactor** while keeping tests green
4. **Repeat**

**Example:**

```python
# Step 1: Write failing test
def test_new_feature():
    radio = MyRadio()
    result = radio.new_feature()
    assert result == expected

# Step 2: Implement
class MyRadio:
    def new_feature(self):
        return expected  # Minimum implementation

# Step 3: Refactor
class MyRadio:
    def new_feature(self):
        # Better implementation
        return self._calculate_result()

# Tests still pass!
```

## Debugging Tests

### Running with Debugging

```bash
# Run with print statements visible
pytest -s

# Run with debugger on failure
pytest --pdb

# Run specific test with verbose output
pytest -vv tests/unit/test_bitwise.py::TestBitwiseParser::test_basic_struct

# Show local variables on failure
pytest -l
```

### Using Python Debugger

```python
def test_something():
    # Set breakpoint
    import pdb; pdb.set_trace()

    # Or use breakpoint() in Python 3.7+
    breakpoint()

    result = function_to_test()
    assert result == expected
```

### Logging in Tests

```bash
# Enable debug logging
export CHIRP_DEBUG=y
pytest tests/test_drivers.py -k FT-60

# View logs
cat /tmp/chirp_debug.log
```

## Performance Testing

### Measure Test Duration

```bash
# Show slowest tests
pytest --durations=10

# Time entire suite
time pytest

# Profile tests
pytest --profile
```

### Parallel Execution

```bash
# Use all CPU cores
pytest -n auto

# Use specific number of workers
pytest -n 4
```

## Coverage Analysis

```bash
# Generate coverage report
pytest --cov=chirp --cov-report=html

# View report
open htmlcov/index.html

# Show missing lines
pytest --cov=chirp --cov-report=term-missing

# Fail if coverage below threshold
pytest --cov=chirp --cov-fail-under=80
```

## Best Practices

### 1. Test Naming
- Use descriptive names: `test_frequency_validation_rejects_out_of_band`
- Group related tests in classes
- Use `test_` prefix for pytest discovery

### 2. Test Independence
- Each test should be independent
- Don't rely on test execution order
- Clean up after tests (use fixtures)

### 3. Test Data
- Use minimal test data
- Avoid real serial ports in automated tests
- Mock hardware interactions

### 4. Assertions
- Use specific assertions: `assert x == 5` not `assert x`
- Add messages: `assert x == 5, f"Expected 5, got {x}"`
- Use pytest helpers: `pytest.approx()` for floats

### 5. Fixtures
```python
@pytest.fixture
def radio():
    """Fixture providing a radio instance"""
    r = MyRadio("tests/images/test.img")
    yield r
    # Cleanup if needed
    r.close()

def test_with_fixture(radio):
    """Test using fixture"""
    mem = radio.get_memory(0)
    assert mem is not None
```

## Summary

CHIRP's testing infrastructure ensures:
- **Code quality** through style checks
- **Correctness** through unit and integration tests
- **Compatibility** through driver tests for all 184 radios
- **Regression prevention** through automated CI/CD
- **Developer productivity** through fast test iterations

Always run tests before submitting PRs and add tests for new features!
