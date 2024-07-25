import sys

def helloWorld():
    return "Hello World"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        function_name = sys.argv[1] if sys.argv[1] else "helloWorld"
        func = globals().get(function_name)
        if func and callable(func):
            print(func())
        else:
            print("Error: Function not found")
    else:
        # Default function to call when no function name is provided
        print(helloWorld())

