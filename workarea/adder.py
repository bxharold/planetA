#!/usr/local/bin/python3
# adder.py

from addera import function_from_another_file

def main():
    print(add(12))
    function_from_another_file()

def add(x):
    return x+1

if __name__ == "__main__":
    main()

"""
addera.py:
def function_from_another_file():
    print("function in another file.")
"""
