"""Minimal smoke test: the entry-point script must byte-compile cleanly."""
import py_compile
from pathlib import Path


def test_script_compiles():
    script = Path(__file__).resolve().parent.parent / "dry-check.py"
    py_compile.compile(str(script), doraise=True)
