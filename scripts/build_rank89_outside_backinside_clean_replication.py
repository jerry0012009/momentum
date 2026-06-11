#!/usr/bin/env python3
from pathlib import Path
import runpy

TARGET = Path(__file__).resolve().with_name('build_rank89_outside_inside_clean_replication.py')
runpy.run_path(str(TARGET), run_name='__main__')
