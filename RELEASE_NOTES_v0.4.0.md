# Vibecraft Framework v0.4.0 Release Notes

**Release Date:** 27 февраля 2026 г.

## 🎉 Major Features

### Modular Mode Enhancement (Phase 9)

This release introduces comprehensive testing and documentation for the **Modular Mode** architecture, providing a robust foundation for large-scale project development with explicit module dependencies.

#### New Components

1. **ModuleManager** (`vibecraft/modes/modular/module_manager.py`)
   - Complete CRUD operations for modules
   - Path traversal security validation
   - Module initialization with standard structure
   - Integration with ModuleRegistry

2. **ModuleRegistry** (`vibecraft/modes/modular/module_registry.py`)
   - Central registry for all module metadata
   - Support for both legacy and Phase 6+ APIs
   - Caching mechanism for performance
   - Type-safe Module object conversions

3. **IntegrationManager** (`vibecraft/modes/modular/integration_manager.py`)
   - Dependency analysis and validation
   - Topological build order computation
   - Automatic interface generation (Protocol classes)
   - Connector generation for inter-module communication

#### Security Enhancements

- **Path Traversal Protection**: All module operations validate paths to prevent directory traversal attacks
- **Input Validation**: Module names validated against Python identifier rules
- **Dependency Validation**: Circular dependency detection during integration

## 📚 Documentation

Four comprehensive guides added:

1. **MODULAR_MODE.md** - Complete modular mode overview and usage
2. **MODULE_DEVELOPMENT.md** - Module development best practices
3. **INTEGRATION_GUIDE.md** - Integration layer setup and usage
4. **MIGRATION_SIMPLE_TO_MODULAR.md** - Migration path from simple to modular mode

All guides include:
- Step-by-step tutorials
- Real-world examples
- Troubleshooting sections
- Architecture diagrams

## 🧪 Testing

### Test Coverage

- **Total Tests**: 258 passing tests
- **Overall Coverage**: 59%
- **New Modular Code Coverage**: 94-98%

#### New Test Files

- `test_module_manager.py` - 19 tests
- `test_module_registry.py` - 21 tests
- `test_integration_manager.py` - 21 tests
- `test_modular_runner.py` - 13 tests
- `test_context_manager.py` - 12 tests

### Test Categories

1. **Unit Tests**: Core functionality testing
2. **Integration Tests**: Module workflow testing
3. **Security Tests**: Path traversal and validation
4. **Edge Case Tests**: Empty registries, malformed data, etc.

## 🔧 Bug Fixes & Improvements

### Deprecation Fixes

Migrated from deprecated `datetime.utcnow()` to `datetime.now(timezone.utc)`:

- `vibecraft/modes/modular/__init__.py`
- `vibecraft/context_manager.py` (3 occurrences)
- `vibecraft/exporter.py` (2 occurrences)
- `vibecraft/modes/modular/module_registry.py`

### API Improvements

1. **ModuleRegistry**: Added dual API support (legacy + Phase 6+)
2. **IntegrationManager**: Graceful handling of missing/empty registry
3. **ModuleManager**: Better error messages for module operations

## 📊 Statistics

### Code Metrics

| Metric | Value |
|--------|-------|
| Total Statements | 1,945 |
| Covered Statements | 1,147 |
| Coverage | 59% |
| Test Files | 18 |
| Test Functions | 258 |

### Module Coverage

| Module | Coverage |
|--------|----------|
| module_manager.py | 98% |
| module_registry.py | 94% |
| integration_manager.py | 94% |
| context_manager.py | 100% |
| runner.py (modular) | 98% |
| dependency_analyzer.py | 97% |

## 🔄 Breaking Changes

**None** - This release maintains backward compatibility with v0.3.0.

## 🚀 Migration Guide

### From v0.3.0 to v0.4.0

No migration required. Simply upgrade:

```bash
pip install --upgrade vibecraft
```

### For Modular Mode Users

If you're using modular mode, your existing modules are compatible. New features are additive:

```bash
# Create new modules with enhanced features
vibecraft module create auth -d "Authentication module" --depends-on database

# Analyze dependencies
vibecraft integrate analyze

# Build integration layer
vibecraft integrate build
```

## 🎯 What's Next (v0.5.0)

Planned features for next release:

1. **Visual Dashboard** - Web-based project status visualization
2. **Cross-Module Skills** - Skills that operate across multiple modules
3. **Enhanced Dependency Analysis** - Visual dependency graphs
4. **Performance Optimizations** - Faster context building for large projects

## 🙏 Acknowledgments

This release represents significant community feedback incorporation, particularly in:
- Security hardening
- API consistency
- Documentation completeness
- Test coverage

## 📝 Installation

```bash
# Fresh install
pip install vibecraft==0.4.0

# Upgrade from previous version
pip install --upgrade vibecraft
```

## 🔍 Verification

After installation, verify:

```bash
vibecraft --version
# Should output: vibecraft 0.4.0

# Run tests
pytest vibecraft-framework/tests/ -v
```

---

**Full Changelog**: https://github.com/vibecraft/vibecraft/compare/v0.3.0...v0.4.0

**PyPI Package**: https://pypi.org/project/vibecraft/0.4.0/

**Documentation**: https://github.com/vibecraft/vibecraft/tree/main/vibecraft-framework/docs
