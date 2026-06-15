#!/usr/bin/env python3
"""Lanzador de la app desde la raíz del proyecto.

Permite ejecutar `python run.py` sin tener que hacer `cd src`.
"""

import os
import sys

SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
sys.path.insert(0, SRC_DIR)

from main import main  # noqa: E402

if __name__ == "__main__":
    main()
