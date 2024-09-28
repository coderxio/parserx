from parsers.sig import *
import csv


def main():
    value = get_input()
    generate_output(value)


def get_input():
    while True:
        try:
            value = int(
                input(
                    "Enter [1] for a single sig. Enter [2] for bulk sigs via .csv file: "
                )
            )
            if value not in (1, 2):
                pass
            else:
                return value
        except ValueError:
            pass


def generate_output(n):
    if n == 1:
        sig = input("Enter sig: ")
        print(SigParser().parse(sig))

    else:
        while True:
            try:
                inputfile, outputfile = input("Enter input.csv and output.csv: ").split(
                    " "
                )
                if inputfile.endswith(".csv") and outputfile.endswith(".csv"):
                    with open(inputfile, "r") as file:
                        print(file)
                else:
                    print("Both files must end with .csv. Please try again.")
            except ValueError:
                pass
            except FileNotFoundError:
                print("Input file not found. Please try again.")
                pass


if __name__ == "__main__":
    main()


# parsed_sig = SigParser().parse(x)
# print(parsed_sig)
