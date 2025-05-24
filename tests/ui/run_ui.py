import sys
import os
import subprocess

if __name__ == '__main__':
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../rust_client/target/debug')))
    subprocess.run(['python', 'ui/app.py'])


