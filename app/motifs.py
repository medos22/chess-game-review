# app/motifs.py
from .paths import DEP_PATH, STOCKFISH_PATH
import chess

def detect_simple_tactics(board: chess.Board, just_played_was_capture: bool):
    """Very light motifs on the position AFTER the move."""
    motifs = []
    if board.is_check():
        motifs.append("CHECK")
    if just_played_was_capture:
        motifs.append("CAPTURE")

    # Hanging pieces left by the side that just moved
    side_just_moved = not board.turn
    opp = board.turn
    hanging = 0
    for sq in chess.SquareSet(board.occupied_co[side_just_moved]):
        if board.piece_type_at(sq) == chess.KING:
            continue
        if board.is_attacked_by(opp, sq) and not board.is_attacked_by(side_just_moved, sq):
            hanging += 1
    if hanging:
        motifs.append(f"HANGING({hanging})")
    return motifs
