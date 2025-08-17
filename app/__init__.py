# app/__init__.py
# Marks this directory as a Python package
from .paths import DEP_PATH, ROOT, STOCKFISH_PATH 
__all__ = ["DEP_PATH", "ROOT", "STOCKFISH_PATH"]
from .evaluation import score_to_cp, classify_move, fmt_eval
from .engine import Engine
from .analysis import analyze_pgn_text, analyze_game
from .motifs import detect_simple_tactics
from . import paths, evaluation, engine, analysis, motifs
from . import cli  # Import CLI module for command line interface
__version__ = "0.1.0"  # Example version, update as needed
__all__ += ["__version__", "cli", "paths", "evaluation", "engine", "analysis", "motifs"]
# Ensure the paths are set up correctly
# This is done in paths.py, but we can also ensure it here
# if __name__ == "__main__":
#    print(f"Project root: {ROOT}")
#   print(f"Stockfish path: {STOCKFISH_PATH}")
# print(f"Dependency path: {DEP_PATH}")
# # This file can be used to initialize the app package and import necessary modules.
# # You can also add any package-level initialization code here if needed.
# # Example usage:
# # from app import Engine, analyze_pgn_text
# # engine = Engine().start()
# # pgn_text = "..."  # Your PGN text here
# # analysis_results = analyze_pgn_text(pgn_text)
# print(analysis_results)
# This file is the main entry point for the app package.
# It can be used to initialize the package and import necessary modules.
# This file can be used to initialize the app package and import necessary modules.
# You can also add any package-level initialization code here if needed.
# Example usage:
# from app import Engine, analyze_pgn_text
# engine = Engine().start()
# pgn_text = "..."  # Your PGN text here
# analysis_results = analyze_pgn_text(pgn_text)
# print(analysis_results)
# This file is the main entry point for the app package.
# It can be used to initialize the package and import necessary modules.