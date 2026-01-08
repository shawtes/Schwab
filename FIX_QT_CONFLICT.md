# Fix Qt Framework Conflict

## Problem

You have both **PySide6** and **PyQt5** installed in your conda environment. This causes class conflicts on macOS, leading to segmentation faults when launching the GUI.

## Solution

You need to **remove one of them**. We recommend keeping **PySide6** and removing **PyQt5**.

### Quick Fix (Recommended)

```bash
# In your conda environment
conda activate schwabdev

# Remove PyQt5 (keep PySide6)
pip uninstall PyQt5 PyQt5-Qt5 PyQt5-sip

# Verify
python -c "from PySide6.QtWidgets import QApplication; print('✓ PySide6 OK')"
```

### Alternative: Keep PyQt5, Remove PySide6

```bash
# Remove PySide6 (keep PyQt5)
pip uninstall PySide6

# Verify
python -c "from PyQt5.QtWidgets import QApplication; print('✓ PyQt5 OK')"
```

### Automated Fix

Run the fix script:

```bash
bash fix_qt_conflict.sh
```

## After Fixing

Once you've removed one of them, launch the GUI:

```bash
python launch_gui.py
```

The GUI will now work without conflicts!

## Why This Happens

Both PySide6 and PyQt5 provide Qt bindings, and on macOS they can conflict at the Objective-C level, causing:
- Class implementation conflicts
- Segmentation faults
- Application crashes

**Solution**: Use only one Qt framework.

## Recommendation

**Use PySide6** because:
- It's the official Qt binding (PySide6)
- Better maintained
- Easier to install
- More modern


