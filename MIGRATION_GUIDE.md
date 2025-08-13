# Migration Guide - Architecture Refactoring

This document outlines the changes made during the architecture refactoring and provides guidance for migrating existing code.

## Summary of Changes

### ✅ Backward Compatible Changes

All changes maintain full backward compatibility. Existing code will continue to work without modifications.

### 🔧 Default Behavior Changes

1. **Plugin System Default**: The default renderer now uses the plugin system (`use_plugin_system=True`)
   - **Impact**: Better performance and more features by default
   - **Migration**: No action required - existing code will automatically benefit
   - **Rollback**: Set `use_plugin_system=False` to use legacy renderers

2. **Shared Validator Instance**: Validation utilities now use a shared validator instance
   - **Impact**: Better performance for repeated validations
   - **Migration**: No action required - API remains the same

### 📁 File Organization Changes

1. **Convenience Functions Moved**: `quick_render` and related functions moved to `convenience.py`
   - **Impact**: Cleaner `__init__.py` file (reduced from 375 to 260 lines)
   - **Migration**: No action required - functions still available via `from mermaid_render import quick_render`

2. **README Files Added**: Each module now has a comprehensive README
   - **Impact**: Better documentation and understanding of module responsibilities
   - **Migration**: No action required

### ⚙️ Configuration Enhancements

1. **Enhanced MermaidConfig**: Added new default configuration options
   - **New defaults**:
     - `use_plugin_system: True`
     - `fallback_enabled: True`
     - `max_fallback_attempts: 3`
   - **Migration**: No action required - new defaults improve reliability

## Before and After Comparison

### Project Structure

**Before:**
```
mermaid_render/
├── __init__.py (375 lines - too large)
├── core.py
├── models/
├── renderers/
├── validators/
├── utils/
├── config/
├── ai/
├── interactive/
├── collaboration/
├── templates/
└── (missing README files)
```

**After:**
```
mermaid_render/
├── __init__.py (260 lines - focused on imports)
├── convenience.py (new - convenience functions)
├── core.py (enhanced with better defaults)
├── models/ (+ README.md)
├── renderers/ (+ README.md)
├── validators/ (+ README.md)
├── utils/ (+ README.md, optimized validation)
├── config/ (+ README.md)
├── ai/ (+ README.md)
├── interactive/ (+ README.md)
├── collaboration/ (+ README.md)
└── templates/ (+ README.md)
```

### Code Quality Improvements

1. **Validation System**:
   - **Before**: Multiple validator instances created for each validation call
   - **After**: Shared validator instance for better performance

2. **Configuration System**:
   - **Before**: Plugin system disabled by default
   - **After**: Plugin system enabled by default with fallback support

3. **Module Organization**:
   - **Before**: Large `__init__.py` with mixed responsibilities
   - **After**: Focused `__init__.py` with convenience functions in separate module

## Recommended Actions

### For New Projects

1. **Use the defaults**: The new defaults provide the best experience
2. **Leverage module READMEs**: Each module now has comprehensive documentation
3. **Use plugin system**: Take advantage of the enhanced plugin-based rendering

### For Existing Projects

1. **No immediate action required**: All existing code continues to work
2. **Consider testing**: Run your existing tests to verify everything works
3. **Optional optimization**: Remove explicit `use_plugin_system=True` since it's now the default

### Example Migration

**Before (still works):**
```python
from mermaid_render import MermaidRenderer

# Explicitly enabling plugin system
renderer = MermaidRenderer(use_plugin_system=True)
```

**After (recommended):**
```python
from mermaid_render import MermaidRenderer

# Plugin system is now enabled by default
renderer = MermaidRenderer()
```

## Testing Your Migration

Run these commands to verify everything works:

```bash
# Test basic functionality
python -c "from mermaid_render import quick_render; print('✓ Import works')"

# Test rendering
python -c "from mermaid_render import quick_render; result = quick_render('flowchart TD\n    A --> B'); print('✓ Rendering works')"

# Test configuration
python -c "from mermaid_render import MermaidConfig; config = MermaidConfig(); print('✓ Config works, plugin system:', config.get('use_plugin_system'))"
```

## Rollback Instructions

If you need to rollback to the previous behavior:

```python
from mermaid_render import MermaidRenderer

# Use legacy rendering system
renderer = MermaidRenderer(use_plugin_system=False)
```

## Support

If you encounter any issues after the refactoring:

1. Check that your code follows the examples in this guide
2. Verify that all dependencies are properly installed
3. Run the test commands above to isolate the issue
4. Check the module README files for detailed usage information

## Benefits of the Refactoring

1. **Better Performance**: Shared validator instances and optimized defaults
2. **Improved Maintainability**: Cleaner module organization and documentation
3. **Enhanced Features**: Plugin system enabled by default
4. **Better Documentation**: Comprehensive README files in each module
5. **Future-Proof**: Architecture ready for new features and extensions
