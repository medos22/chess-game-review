# app/analysis.py
from typing import List, Dict
from .paths import DEP_PATH, STOCKFISH_PATH
import io
import chess, chess.pgn
from .engine import Engine
from tqdm import tqdm
from .evaluation import score_to_cp, classify_move, fmt_eval

def analyze_pgn_text(pgn_text: str) -> List[Dict]:
    game = chess.pgn.read_game(io.StringIO(pgn_text))
    if not game:
        raise ValueError("No valid game in PGN.")
    return analyze_game(game)

def analyze_game(game: chess.pgn.Game) -> List[Dict]:
    from .motifs import detect_simple_tactics  # avoid circular imports
    results: List[Dict] = []
    board = game.board()

    eng = Engine().start()
    try:
        # Eval starting position (White perspective)
        start_info = eng.analyse_safe(board, depth=10)
        prev_cp = score_to_cp(start_info["score"])

        ply = 1
        moves = list(game.mainline_moves())
        for move in tqdm(moves, desc="Analyzing moves", unit="move"):
            white_to_move = board.turn == chess.WHITE
            was_capture = board.is_capture(move)

            # Best suggestion before playing the move
            lines = eng.best_lines(board, multipv=3)
            best_move = None
            if lines and "pv" in lines[0] and lines[0]["pv"]:
                best_move = lines[0]["pv"][0]

            san = board.san(move)
            board.push(move)

            # Eval after the move (shallow)
            after_info = eng.analyse_safe(board, depth=10)
            after_cp = score_to_cp(after_info["score"])

            # Classify move
            label, cp_loss = classify_move(prev_cp, after_cp, white_to_move)

            # Run deep eval if it's a big mistake/blunder
            deep_eval = None
            if cp_loss >= 100:
                deep_info = eng.analyse_safe(board, depth=25)
                deep_eval = score_to_cp(deep_info["score"])

            motifs = detect_simple_tactics(board, just_played_was_capture=was_capture)

            results.append({
                "ply": ply,
                "san": san,
                "uci": move.uci(),
                "label": label,
                "cp_loss": cp_loss,
                "eval_before": prev_cp,
                "eval_after": after_cp,
                "best_move": best_move.uci() if best_move else None,
                "motifs": motifs,
                "white_move": white_to_move,
                "deep_eval": deep_eval
            })

            prev_cp = after_cp
            ply += 1

        return results
    finally:
        eng.stop()


def format_results(results: List[Dict]) -> str:
    lines = ["\nANALYSIS RESULTS", "=" * 60]
    for r in results:
        move_num = (r["ply"] + 1) // 2
        side = "W" if r["white_move"] else "B"
        parts = [r["label"]]
        if r["cp_loss"] > 10:
            parts.append(f"-{r['cp_loss']}cp")
        parts.append(f"({fmt_eval(r['eval_before'])} → {fmt_eval(r['eval_after'])})")
        if r["motifs"]:
            parts.append("[" + ", ".join(r["motifs"]) + "]")
        if r["label"] in {"MISTAKE","BLUNDER"} and r["best_move"]:
            parts.append(f"Better: {r['best_move']}")
        lines.append(f"{move_num:2d}.{side} {r['san']:>6} | " + " — ".join(parts))

    if results:
        total = len(results)
        bl = sum(1 for r in results if r["label"] == "BLUNDER")
        ms = sum(1 for r in results if r["label"] == "MISTAKE")
        ia = sum(1 for r in results if r["label"] == "INACCURACY")
        good = total - bl - ms - ia
        lines += ["", "=" * 60, "GAME SUMMARY",
                  f"Total moves: {total}",
                  f"Good moves: {good}",
                  f"Inaccuracies: {ia}",
                  f"Mistakes: {ms}",
                  f"Blunders: {bl}"]
    return "\n".join(lines)
