#!/bin/bash
# Fix Qt framework conflict by removing one of them

echo "=========================================="
echo "Fixing Qt Framework Conflict"
echo "=========================================="
echo ""
echo "You have both PySide6 and PyQt5 installed,"
echo "which causes conflicts on macOS."
echo ""
echo "Recommended: Remove PyQt5 and keep PySide6"
echo ""

read -p "Remove PyQt5? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "Uninstalling PyQt5..."
    pip uninstall -y PyQt5 PyQt5-Qt5 PyQt5-sip
    echo ""
    echo "✓ PyQt5 removed. PySide6 will be used."
    echo ""
    echo "You can now run: python launch_gui.py"
else
    echo ""
    echo "Alternative: Remove PySide6 and keep PyQt5"
    read -p "Remove PySide6? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
        echo "Uninstalling PySide6..."
        pip uninstall -y PySide6
        echo ""
        echo "✓ PySide6 removed. PyQt5 will be used."
        echo ""
        echo "You can now run: python launch_gui.py"
    else
        echo ""
        echo "Keeping both (not recommended)."
        echo "You may experience crashes."
    fi
fi

echo ""
echo "=========================================="


