# app/engine.py
from __future__ import annotations
from .paths import DEP_PATH, STOCKFISH_PATH
from typing import Optional, List, Tuple
from .paths import STOCKFISH_PATH
import chess, chess.engine

ENGINE_OPTS = {"Threads": 8, "Hash": 256, "UCI_ShowWDL": True}
DEFAULT_DEPTH = 16

class Engine:
    def __init__(self, path=STOCKFISH_PATH):
        self.path = str(path)
        self.proc: Optional[chess.engine.SimpleEngine] = None

    def start(self):
        if not STOCKFISH_PATH.exists():
            raise FileNotFoundError(f"Stockfish not found at {STOCKFISH_PATH}")
        self.proc = chess.engine.SimpleEngine.popen_uci(self.path)
        try:
            self.proc.configure(ENGINE_OPTS)
        except chess.engine.EngineError:
            # Retry without WDL if unsupported
            safe = {k:v for k,v in ENGINE_OPTS.items() if k != "UCI_ShowWDL"}
            self.proc.configure(safe)
        return self

    def stop(self):
        if self.proc:
            try:
                self.proc.quit()
            finally:
                self.proc = None

    # single position, robust, returns raw info dict
    def analyse_safe(self, board: chess.Board, depth: int = DEFAULT_DEPTH, multipv: int = 1):
        assert self.proc, "Engine not started"
        try:
            result = self.proc.analyse(board, chess.engine.Limit(depth=depth), multipv=multipv)
            if isinstance(result, list):
                return result[0]  # just return the top line
            return result
        except Exception as e:
            print(f"[!] Engine error at depth {depth}: {e}")
            return {"score": chess.engine.PovScore(chess.engine.Cp(0), board.turn)}



    # multipv best lines
    def best_lines(self, board: chess.Board, multipv=3, depth: int = DEFAULT_DEPTH):
        assert self.proc, "Engine not started"
        try:
            res = self.proc.analyse(board, chess.engine.Limit(depth=depth), multipv=multipv)
            if not isinstance(res, list):
                res = [res]
            return res
        except Exception:
            single = self.analyse_safe(board, depth=depth)
            return [single]
