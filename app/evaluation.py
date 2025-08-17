# app/evaluation.py
from .paths import DEP_PATH, STOCKFISH_PATH
import chess, chess.engine

THRESHOLDS = {"inaccuracy": 50, "mistake": 100, "blunder": 300}

def score_to_cp(score: chess.engine.PovScore) -> int:
    """Return centipawns from White's perspective."""
    s = score.pov(chess.WHITE)
    if s.is_mate():
        m = s.mate()
        return 10_000 - m if m > 0 else -10_000 - m
    cp = s.score(mate_score=10_000)
    return int(cp) if cp is not None else 0

def classify_move(eval_before_cp: int, eval_after_cp: int, white_just_moved: bool):
    """Return (label, cp_loss) for the side that just moved."""
    if white_just_moved:
        cp_loss = max(0, eval_before_cp - eval_after_cp)
    else:
        cp_loss = max(0, eval_after_cp - eval_before_cp)

    if cp_loss >= THRESHOLDS["blunder"]:
        return "BLUNDER", cp_loss
    if cp_loss >= THRESHOLDS["mistake"]:
        return "MISTAKE", cp_loss
    if cp_loss >= THRESHOLDS["inaccuracy"]:
        return "INACCURACY", cp_loss
    return "GOOD", cp_loss

def fmt_eval(cp: int) -> str:
    if abs(cp) >= 9_500:
        return "M" if cp > 0 else "-M"
    return f"{cp/100:+.2f}"
