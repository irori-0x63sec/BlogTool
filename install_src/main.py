import sys
import os

# install_src をPythonパスに追加
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from gui.main_window import launch_main 

if __name__ == "__main__":
    launch_main()
