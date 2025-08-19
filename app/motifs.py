import chess

def detect_simple_tactics(board: chess.Board, just_played_was_capture=False) -> list:
    motifs = []
    last_move = board.peek() if board.move_stack else None
    if not last_move:
        return motifs

    # Motif 1: Check
    if board.is_check():
        motifs.append("Check")

    # Motif 2: Capture
    if just_played_was_capture:
        motifs.append("Capture")

    # Motif 3: Hanging Piece
    # If we just moved a piece to a square that's attacked but not defended
    to_sq = last_move.to_square
    attacker_color = not board.turn  # previous move's player
    defenders = board.attackers(not attacker_color, to_sq)
    attackers = board.attackers(attacker_color, to_sq)
    if attackers and not defenders:
        motifs.append("Hanging")

    # Motif 4: Fork
    # Did the moved piece now attack multiple valuable targets?
    fork_targets = 0
    for square in board.attacks(to_sq):
        if board.piece_at(square) and board.piece_at(square).color != board.turn:
            if board.piece_at(square).piece_type in {chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT}:
                fork_targets += 1
    if fork_targets >= 2:
        motifs.append("Fork")

    # Motif 5: Discovered Attack
    # Check if the move uncovered a long-range attack (rook, bishop, queen)
    from_sq = last_move.from_square
    for attacker_sq in board.attackers(not board.turn, board.king(board.turn)):
        if board.piece_at(attacker_sq) and board.piece_at(attacker_sq).piece_type in {chess.QUEEN, chess.ROOK, chess.BISHOP}:
            if board.is_pinned(board.turn, from_sq):
                motifs.append("Discovered Attack")
                break

    # Motif 6: Pin
    if board.is_pinned(not board.turn, to_sq):
        motifs.append("Pin")

    return motifs
