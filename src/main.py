"""Main application entrypoint"""

import sys
import os
import argparse
import signal
import qdarkstyle
from PySide6.QtWidgets import QApplication

from gui.main_window import MainWindow
from utils.args_config import Config

def show_maps():
    """Shows all existing maps."""
    map_dir = "maps/"
    print(f"Map directory:\n>   {map_dir}")
    maps = [file for file in os.listdir(map_dir)]
    print("List of all maps:")
    for map in maps:
        print(f">   {map}")


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-map", type=str, help="Path to the map file to use for the game/training")
    parser.add_argument("-vis", type=int, default=2, help="""Visibility range for the agent (default: 2). 
                        Different maps might require agent to see more space. Be aware that changing this might 
                        completely break the training!""")
    parser.add_argument("-max_steps", type=int, default=1500, help="""Maximal steps that agent can do in 
                        one generation. For longer maps, agent needs more steps than for shorter maps""")
    parser.add_argument("command", nargs="?", choices = ["show"], help="Command to execute")
    parser.add_argument("subcommand", nargs="?", choices = ["maps"], help="Sub-command")
    
    args = parser.parse_args()
    
    if args.command == "show":
        if args.subcommand == "maps":
            show_maps()
            sys.exit(0)
        else:
            parser.print_help()
            sys.exit(1)
            
    map_path = args.map if args.map else "maps/obstacles.txt"            
    if not os.path.exists(map_path):
        print(f"Error: Map file '{map_path}' not found.")
        sys.exit(1)
    
    # Enable ctrl + c to exit app
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Qt Application intance
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api="pyside6"))
    window = MainWindow(app, Config(map_path, args.vis, args.max_steps))
    window.show()
    app.exec()
