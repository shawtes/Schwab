# Installing GUI Dependencies

## Important: Use Your Conda Environment

You're using a conda environment called `schwabdev`. Make sure you're in that environment before installing or running the GUI.

## Quick Install

```bash
# Activate your conda environment (if not already active)
conda activate schwabdev

# Install GUI dependencies
pip install PySide6 python-dotenv matplotlib seaborn

# OR install everything from requirements.txt
pip install -r requirements.txt
```

## Verify Installation

```bash
# Make sure you're in conda environment
conda activate schwabdev

# Test imports
python -c "from PySide6.QtWidgets import QApplication; print('✓ PySide6 OK')"
# OR if PySide6 not available:
python -c "from PyQt5.QtWidgets import QApplication; print('✓ PyQt5 OK')"
```

## Launch GUI

```bash
# Make sure conda environment is active
conda activate schwabdev

# Launch GUI
python launch_gui.py
# OR
python trading_gui.py
```

## Troubleshooting

### If you see "externally-managed-environment" error:
- You're using the system Python, not conda Python
- Solution: Activate conda environment first
  ```bash
  conda activate schwabdev
  ```

### If PySide6 installation fails in conda:
- Try PyQt5 instead (already works):
  ```bash
  conda install -c conda-forge pyqt
  ```

### Check which Python you're using:
```bash
which python
# Should show something like: /path/to/conda/envs/schwabdev/bin/python
```

## Alternative: Install via Conda

```bash
conda activate schwabdev
conda install -c conda-forge pyside6 python-dotenv matplotlib seaborn pandas numpy scikit-learn
```


