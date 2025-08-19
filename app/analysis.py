from typing import List, Dict
from .paths import DEP_PATH, STOCKFISH_PATH
import io
import chess, chess.pgn
from .engine import Engine
from tqdm import tqdm
from .evaluation import score_to_cp, classify_quality_extended, fmt_eval

def analyze_pgn_text(pgn_text: str) -> List[Dict]:
    game = chess.pgn.read_game(io.StringIO(pgn_text))
    if not game:
        raise ValueError("No valid game in PGN.")
    return analyze_game(game), game

def analyze_game(game: chess.pgn.Game) -> List[Dict]:
    from .motifs import detect_simple_tactics  # avoid circular imports
    results: List[Dict] = []
    board = game.board()

    eng = Engine().start()
    try:
        start_info = eng.analyse_safe(board, depth=10)
        prev_cp = score_to_cp(start_info["score"])

        ply = 1
        moves = list(game.mainline_moves())
        for move in tqdm(moves, desc="Analyzing moves", unit="move"):
            white_to_move = board.turn == chess.WHITE
            was_capture = board.is_capture(move)

            board_before = board.copy(stack=False)
            lines = eng.best_lines(board, multipv=3)
            best_move = None
            if lines and "pv" in lines[0] and lines[0]["pv"]:
                best_move = lines[0]["pv"][0]

            san = board.san(move)
            board.push(move)

            after_info = eng.analyse_safe(board, depth=10)
            after_cp = score_to_cp(after_info["score"])

            label = classify_quality_extended(
                before_cp=prev_cp,
                after_cp=after_cp,
                white_to_move=white_to_move,
                played_move=move,
                board_before=board_before,
                premove_lines=lines
            )

            motifs = detect_simple_tactics(board, just_played_was_capture=was_capture)

            results.append({
                "ply": ply,
                "san": san,
                "uci": move.uci(),
                "label": label,
                "cp_loss": abs(prev_cp - after_cp),
                "eval_before": prev_cp,
                "eval_after": after_cp,
                "best_move": best_move.uci() if best_move else None,
                "motifs": motifs,
                "white_move": white_to_move
            })

            prev_cp = after_cp
            ply += 1

        return results
    finally:
        eng.stop()

def format_results(results: List[Dict], game: chess.pgn.Game = None) -> str:
    from collections import Counter

    white_name = game.headers.get("White", "White") if game else "White"
    black_name = game.headers.get("Black", "Black") if game else "Black"

    white_labels = []
    black_labels = []

    lines = ["\nANALYSIS RESULTS", "=" * 60]
    for r in results:
        move_num = (r["ply"] + 1) // 2
        side = "W" if r["white_move"] else "B"
        label = r["label"]
        cp_loss = r["cp_loss"]
        entry = f"{label}"
        if cp_loss > 10:
            entry += f" (-{cp_loss}cp)"
        if r["motifs"]:
            entry += " [" + ", ".join(r["motifs"]) + "]"
        if label in {"BLUNDER", "MISTAKE", "INACCURACY", "Miss"} and r["best_move"]:
            entry += f" | Better: {r['best_move']}"
        lines.append(f"{move_num:2d}.{side} {r['san']:>6} | {entry}")

        if r["white_move"]:
            white_labels.append(label)
        else:
            black_labels.append(label)

    def summarize(player: str, labels: List[str]) -> str:
        c = Counter(labels)
        good = sum(1 for lbl in labels if lbl.lower() == "good")
        return f"""
♟ {player.upper()} MOVE SUMMARY
-----------------------------
Brilliant:   {c['Brilliant']:2d}
Great:       {c['Great']:2d}
Best:        {c['Best']:2d}
Excellent:   {c['Excellent']:2d}
Good:        {good:2d}
Inaccuracy:  {c['INACCURACY']:2d}
Mistake:     {c['MISTAKE']:2d}
Blunder:     {c['BLUNDER']:2d}
Miss:        {c['Miss']:2d}
"""

    lines += ["", "=" * 60,
              summarize(white_name, white_labels),
              summarize(black_name, black_labels)]

    return "\n".join(lines)
