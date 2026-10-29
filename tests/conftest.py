import sys
from pathlib import Path

# Permite importar app/ y cargar_csv.py desde la raíz del proyecto.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
