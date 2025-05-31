
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: example.py <exchange> [args...]")
        sys.exit(1)

    exchange = sys.argv[1]
    args = sys.argv[2:]

    print(f"Running strategy on exchange: {exchange}")
    if args:
        print("Received arguments:")
        for i, arg in enumerate(args, start=1):
            print(f"  Arg {i}: {arg}")
    else:
        print("No additional arguments provided.")

if __name__ == "__main__":
    main()