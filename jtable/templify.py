#!/usr/bin/env python3
import  os, sys
# print(dir(jtable()))
templify_path = os.path.dirname(os.path.abspath(__file__))

if templify_path not in sys.path:
    sys.path.insert(0, templify_path)
from . import jtable

def main():
    print("Hello from templify!")
    print(dir(jtable))
    jtable.main()
    
    
    # jtable.main()

if __name__ == "__main__":
    main()