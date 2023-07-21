import sys

def add_numbers(*args):
    return sum(args)

if __name__ == "__main__":
    numbers = [float(arg) for arg in sys.argv[1:]]
    result = add_numbers(*numbers)
    print("Result:", result)
