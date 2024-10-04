from parsers.sig import *
import sys
import json


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    WHITE = "\033[97m"


def main():
    value = get_input()
    generate_output(value)


def get_input():
    while True:
        try:
            if len(sys.argv) == 1:
                print_usage_instructions()
                break
            elif sys.argv[1] == "--b":
                input_file, output_file = sys.argv[2], sys.argv[3]
                return 2
            elif sys.argv[1] == "--n":
                return 3
            elif sys.argv[1] == "--r":
                return 4
            else:
                return 1
        except IndexError:
            print("Usage: main.py --b input.csv output.csv")
            break


def print_usage_instructions():
    instructions = [
        (
            bcolors.BOLD
            + bcolors.WHITE
            + "\n  Individual sig usage: "
            + bcolors.ENDC
            + "main.py your sig goes here"
        ),
        (
            bcolors.BOLD
            + bcolors.WHITE
            + "\n  Individual sig usage with inference: "
            + bcolors.ENDC
            + "main.py --n <NDC> your sig goes here"
        ),
        (
            bcolors.BOLD
            + bcolors.WHITE
            + "\n  Individual sig usage with inference: "
            + bcolors.ENDC
            + "main.py --r <RxCUI> your sig goes here"
        ),
        (
            bcolors.BOLD
            + bcolors.WHITE
            + "\n  Bulk sig usage: "
            + bcolors.ENDC
            + " main.py --b input.csv output.csv\n"
        ),
        (
            "   Bulk sig instructions: \n      > Place your input file in the /csv directory.\n"
            "      > Input files are read from the /csv directory.\n"
            "      > Output files are written to the /csv/output directory.\n"
            "      > Enter the input file name (input.csv as default) and output file name (output.csv as default), separated by a space.\n"
        ),
    ]
    for instruction in instructions:
        print(instruction)


def generate_output(n):
    if n == 1:
        matches = SigParser().parse(" ".join(sys.argv[1:]))
        print(json.dumps(matches, indent=4))

    elif n == 2:
        try:
            input_file, output_file = sys.argv[2], sys.argv[3]
            if input_file.endswith(".csv") and output_file.endswith(".csv"):
                SigParser().parse_sig_csv(input_file, output_file)
                print(f"Output written to {output_file}.")
            else:
                print("Both files must end with .csv. Please try again.")
        except ValueError:
            print("Invalid. Enter input and output file names separated by a space.")
        except FileNotFoundError:
            print("Input file not found. Please try again.")
    elif n == 3:
        results = {}
        results['parsed'] = SigParser().parse(" ".join(sys.argv[3:]))
        results['inferred'] = SigParser().infer(results['parsed'], ndc=sys.argv[2]) 
        print(json.dumps(results, indent=4))
    elif n == 3:
        results = {}
        results['parsed'] = SigParser().parse(" ".join(sys.argv[3:]))
        results['inferred'] = SigParser().infer(results['parsed'], rxcui=sys.argv[2]) 
        print(json.dumps(results, indent=4))

if __name__ == "__main__":
    main()
