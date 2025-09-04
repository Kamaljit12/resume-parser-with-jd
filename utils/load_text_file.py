import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import conifg

# jd file path
file_path = conifg.jd_file_path

# function to load text file path
def load_text_file(file_path: str = file_path) -> str:
    # load jd text file
    with open(file_path, "r", encoding="utf-8") as f:
        jd_text = f.read()
    return jd_text