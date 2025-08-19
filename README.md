# chess-game-review

from pathlib import Path

# Save the README content to a markdown file
readme_content = """
# ♟️ Chess Move Analyzer

A Python-based engine-backed tool that analyzes chess games and classifies moves as **Brilliant**, **Great**, **Good**, **Mistake**, **Blunder**, and more — inspired by Chess.com’s move review system.

---

## 📌 Project Overview

This project uses **Stockfish** to evaluate chess games (in PGN format) and explain each move using:
- Pre-move and post-move evaluations
- MultiPV (best move alternatives)
- Tactical motifs and material changes
- Centipawn loss thresholds

The result is a labeled list of every move in the game with its classification and reason — suitable for post-game analysis or building a UI around.

---

## 🔍 Features

- ✅ Detects **Blunders**, **Mistakes**, and **Inaccuracies**
- ✅ Classifies **Brilliant**, **Great**, **Excellent**, **Best**, **Missed** moves
- ✅ Highlights basic tactical motifs (like checks, captures, and hanging pieces)
- ✅ Uses Stockfish's full strength (depth 25) **only for crucial moments**
- ✅ Outputs detailed per-move reports including CP loss and better suggestions

---

## 🧠 How It Works

For each move in the game:
1. Evaluate the position before the move (`depth=10`)
2. Push the move, then evaluate again (`depth=10`)
3. If the evaluation drops significantly, analyze deeper (`depth=25`)
4. Use MultiPV to see if better options existed
5. Label the move using custom thresholds and sacrifice logic

---

## 📁 Project Structure

```bash
├── app/
│   ├── analysis.py          # Main analysis loop
│   ├── evaluation.py        # Label logic & sacrifice detection
│   ├── engine.py            # Stockfish wrapper
│   ├── motifs.py            # Detect checks, captures, hangings
│   ├── cli.py               # Command-line runner (insert your pgn here)
│   └── paths.py             # Setup paths to Stockfish binary
├── stockfish/               # Stockfish source/binary
├── dep/                     #dep
├── main.py                  # Script entry point(run this code and you are good to go)
