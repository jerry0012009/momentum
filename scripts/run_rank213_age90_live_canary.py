#!/usr/bin/env python3
from __future__ import annotations

import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "config" / "execution" / "rank213_age90_live_canary.yaml"
REUSED_SHELL = ROOT / "scripts" / "run_rank213_largecap_xs_jump_veto_live_canary.py"


def main() -> int:
    argv = list(sys.argv[1:])
    if "--config" not in argv:
        argv = ["--config", str(DEFAULT_CONFIG), *argv]
    sys.argv = [str(REUSED_SHELL), *argv]
    runpy.run_path(str(REUSED_SHELL), run_name="__main__")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
