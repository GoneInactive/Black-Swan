import sys
import os

def __init__():
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..", "clients")))
    from kraken_python_client import KrakenPythonClient