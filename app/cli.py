# app/cli.py
from pathlib import Path
from .analysis import analyze_pgn_text, format_results

TEST_PGN = """[Event "Live Chess"]
[Site "Chess.com"]
[Date "2025.08.15"]
[Round "?"]
[White "medos_22"]
[Black "GhanesGhanes"]
[Result "1-0"]
[TimeControl "600"]
[WhiteElo "608"]
[BlackElo "575"]
[Termination "medos_22 won by resignation"]
[ECO "C00"]
[EndTime "16:40:02 GMT+0000"]
[Link "https://www.chess.com/game/live/141921160118"]

1. d4 e6 2. e4 Nc6 3. Nf3 Qf6 4. Bg5 Qg6 5. Nc3 h6 6. Bh4 Nf6 7. Bb5 a6 8. Bxc6
dxc6 9. Ne5 Qxg2 10. Qf3 Qxf3 11. Nxf3 g5 12. e5 Ng4 13. h3 Nxe5 14. Nxe5 gxh4
15. Nf3 c5 16. d5 b5 17. O-O-O Bb7 18. Nxh4 exd5 19. Nxd5 Bd6 20. Nf5 Be5 21.
Nxc7+ Kf8 22. Nxa8 Bxa8 23. Rhe1 f6 24. f4 Bxf4+ 25. Kb1 Bf3 26. Rd8+ Kf7 27.
Rxh8 Bd2 28. Re7+ Kg6 29. Nh4+ Kh5 30. Nxf3 f5 31. Nxd2 f4 32. Rf7 Kg5 33. Rg8+
1-0"""

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
    results = analyze_pgn_text(pgn)
    print(format_results(results))
