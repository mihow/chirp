# CHIRP AI Agent Documentation

This directory contains detailed documentation for AI agents working on the CHIRP codebase.

## Documentation Files

### **[architecture.md](architecture.md)**
Deep dive into CHIRP's architecture:
- Core design patterns (Plugin/Driver, Registry, Bitwise DSL)
- Base class hierarchy
- Data flow diagrams
- Extension points
- Threading model
- Security considerations

### **[modules.md](modules.md)**
Module-by-module reference:
- Core modules (`chirp_common`, `directory`, `bitwise`, etc.)
- UI modules (`wxui/`)
- CLI modules (`cli/`)
- Network sources (`sources/`)
- Detailed class documentation with examples

### **[testing.md](testing.md)**
Comprehensive testing guide:
- Test framework (pytest, tox)
- Running tests (style, unit, driver, edge cases)
- Test types and organization
- Writing new tests
- TDD workflow
- Debugging strategies
- CI/CD integration

### **[drivers.md](drivers.md)**
Complete driver development guide:
- Prerequisites and required information
- Step-by-step driver creation
- Memory map definitions
- Communication protocols
- Advanced features (banks, settings, sub-devices)
- Common pitfalls
- Testing checklist
- Example drivers to study

### **[api-reference.md](api-reference.md)**
Complete API reference:
- Core data structures (`Memory`, `RadioFeatures`, `PowerLevel`)
- Base radio classes (`Radio`, `CloneModeRadio`, `LiveRadio`)
- Settings framework
- Memory maps and bitwise parser
- Directory registry
- Bank model
- Error handling
- Utility functions

## Quick Navigation

### I want to...

**Understand the overall architecture**
→ Start with [architecture.md](architecture.md)

**Learn about a specific module**
→ See [modules.md](modules.md)

**Write or run tests**
→ Read [testing.md](testing.md)

**Create a new radio driver**
→ Follow [drivers.md](drivers.md)

**Look up API details**
→ Check [api-reference.md](api-reference.md)

## Parent Documentation

**[CLAUDE.md](../../CLAUDE.md)** - Main AI agent development guide with:
- Cost optimization guidelines
- Development best practices
- Project overview
- Quick start guide
- Common gotchas

## External Resources

- **Website:** https://www.chirpmyradio.com
- **Issue Tracker:** https://chirpmyradio.com/projects/chirp/issues
- **Wiki:** https://chirpmyradio.com/projects/chirp/wiki
- **Source Code:** https://github.com/kk7ds/chirp

## Contributing

When working on CHIRP:
1. Read [CLAUDE.md](../../CLAUDE.md) first for development principles
2. Consult relevant documentation in this directory
3. Run tests frequently (`python tools/fast-driver.py`)
4. Commit often with clear messages
5. Follow the coding standards (PEP8, type hints)

Remember: **Think before you code. Use CLI tools. Keep it simple.**
