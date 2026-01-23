"""
Main entry point for running DesiLang as a module.
Usage: python -m desilang run script.dl
"""

from .cli import main
import sys

if __name__ == '__main__':
    sys.exit(main())
