import sys
import pycep.interpreter

def main():
    if len(sys.argv) > 1:
        pycep.interpreter.execfile(sys.argv[1])
    return 0
    
if __name__ == '__main__':
    main()