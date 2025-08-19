from .paths import DEP_PATH, STOCKFISH_PATH
import chess, chess.engine

THRESHOLDS = {"inaccuracy": 50, "mistake": 100, "blunder": 300}

# Convert engine score to centipawns (White POV)
def score_to_cp(score: chess.engine.PovScore) -> int:
    s = score.pov(chess.WHITE)
    if s.is_mate():
        m = s.mate()
        return 10000 - m if m > 0 else -10000 - m
    return int(s.score(mate_score=10000))

def classify_move(eval_before_cp: int, eval_after_cp: int, white_just_moved: bool):
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
    if abs(cp) >= 9500:
        return "M" if cp > 0 else "-M"
    return f"{cp/100:+.2f}"

PIECE_CP = {
    chess.PAWN: 100, chess.KNIGHT: 320, chess.BISHOP: 330,
    chess.ROOK: 500, chess.QUEEN: 900
}

def piece_cp(board: chess.Board, sq: chess.Square) -> int:
    return PIECE_CP.get(board.piece_type_at(sq), 0)

def immediate_material_swing(board: chess.Board, move: chess.Move) -> int:
    from_val = piece_cp(board, move.from_square)
    to_val = piece_cp(board, move.to_square)
    promo_penalty = 200 if move.promotion and move.promotion != chess.QUEEN else 0
    return to_val - (from_val + promo_penalty)

def is_sacrifice(board_before, move, before_cp, after_cp):
    swing = immediate_material_swing(board_before, move)
    try:
        see = board_before.see(move)
    except:
        see = 0
    eval_ok = (after_cp - before_cp) >= -50
    return (swing <= -300 or see <= -200) and eval_ok

def _multipv_rank_and_gap(lines, played_move_uci: str):
    rank = None
    best_cp = None
    played_cp = None
    for i, li in enumerate(lines, start=1):
        if not li.get("pv"): continue
        score = score_to_cp(li["score"])
        if best_cp is None:
            best_cp = score
        mv = li["pv"][0].uci()
        if mv == played_move_uci:
            rank = i
            played_cp = score
    if rank is None or played_cp is None or best_cp is None:
        return None, None
    return rank, max(0, best_cp - played_cp)

def classify_quality_extended(before_cp, after_cp, white_to_move, played_move, board_before, premove_lines):
    label, cp_loss = classify_move(before_cp, after_cp, white_to_move)

    # If clearly bad, return it
    if label in {"BLUNDER", "MISTAKE", "INACCURACY"}:
        return label

    # Extended logic for non-bad moves
    rank, gap = _multipv_rank_and_gap(premove_lines, played_move.uci())
    if rank is None:
        return "Good" if cp_loss < 50 else "GOOD"

    only_move = False
    if len(premove_lines) >= 2:
        first = score_to_cp(premove_lines[0]["score"])
        second = score_to_cp(premove_lines[1]["score"])
        only_move = (first - second) >= 150 and rank == 1

    is_brilliant = is_sacrifice(board_before, played_move, before_cp, after_cp)
    is_not_lost = abs(before_cp) < 500
    eval_gain = after_cp - before_cp if white_to_move else before_cp - after_cp

    if only_move and is_brilliant and is_not_lost and eval_gain >= 50:
        return "Brilliant"

    if only_move and rank == 1:
        return "Great"

    if rank == 1 and gap <= 10:
        return "Best"

    if rank <= 2 and gap <= 50:
        return "Excellent"

    if rank <= 3 and gap <= 100:
        return "Good"

    best_score = score_to_cp(premove_lines[0]["score"])
    missed_big = gap >= 300
    missed_mate = hasattr(premove_lines[0]["score"], "is_mate") and premove_lines[0]["score"].is_mate()
    if (missed_big or missed_mate) and cp_loss < 100:
        return "Miss"

    if cp_loss < 50:
        return "Good"

    return "GOOD"
