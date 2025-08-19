# app/cli.py
from pathlib import Path
from .analysis import analyze_pgn_text, format_results

TEST_PGN = """[Event "Live Chess"]
[Site "Chess.com"]
[Date "2025.08.18"]
[Round "?"]
[White "medos_22"]
[Black "wetinremann"]
[Result "0-1"]
[TimeControl "600"]
[WhiteElo "662"]
[BlackElo "699"]
[Termination "wetinremann won by resignation"]
[ECO "C00"]
[EndTime "12:42:24 GMT+0000"]
[Link "https://www.chess.com/game/live/142030588646"]

1. d4 e6 2. e4 Bb4+ 3. Bd2 Qe7 4. Bxb4 Qxb4+ 5. c3 Qxb2 6. Nd2 Qxc3 7. Nf3 Nf6
8. Bb5 a6 9. Qc1 Qa5 10. Bc4 Nxe4 11. O-O Nxd2 12. Nxd2 O-O 13. Qb1 Qxd2 14. Qd3
Qf4 15. Qe3 Qd6 16. Qe4 f5 17. Qh4 Nc6 18. Bd3 Nxd4 19. g4 Nf3+ 20. Kg2 Nxh4+
0-1"""

def main(argv=None):
    import sys
    argv = argv or sys.argv[1:]
    if argv:
        p = Path(argv[0])
        pgn = p.read_text(encoding="utf-8", errors="ignore")
        print(f"Loaded PGN from: {p}")
    else:
        pgn = TEST_PGN
        print("Using built-in test game.")
    results, game = analyze_pgn_text(pgn)
    print(format_results(results, game))

