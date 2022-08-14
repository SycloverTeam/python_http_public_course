import pathlib
import sys
folder = pathlib.Path(__file__).absolute()
sys.path.append(str(folder.parent.parent))
