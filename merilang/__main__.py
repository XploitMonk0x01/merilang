"""
Main entry point for running MeriLang as a module.
Usage: python -m MeriLang run script.dl
"""

from .cli import main
import sys

if __name__ == '__main__':
    sys.exit(main())
