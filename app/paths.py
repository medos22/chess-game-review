# app/paths.py
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]   # project root (folder that contains app/)
DEP_PATH = ROOT / "dep"
if str(DEP_PATH) not in sys.path:
    sys.path.insert(0, str(DEP_PATH))

STOCKFISH_PATH = ROOT / "stockfish" / "stockfish-windows-x86-64-avx2.exe"