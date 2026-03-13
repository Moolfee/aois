import os
import sys


ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
LAB1_DIR = os.path.join(ROOT_DIR, "LAB_1")

if LAB1_DIR not in sys.path:
    sys.path.insert(0, LAB1_DIR)
