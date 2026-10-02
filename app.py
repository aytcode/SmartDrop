#!/usr/bin/env python3
"""
SmartDrop Launcher
Usage: python app.py
"""
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from smartdrop.app import main

if __name__ == "__main__":
    main()
