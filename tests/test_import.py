import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_import():
    import coinglass_pipeline  # noqa: F401
