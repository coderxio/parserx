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
                    "Enter 1 for a single sig. Enter 2 for bulk sigs via .csv file: "
                )
            )
            if value in (1, 2):
                return value
            else:
                print("Invalid value. Enter either a 1 or 2 to continue.")
        except ValueError:
            print("Invalid value. Enter either a 1 or 2 to continue.")


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
                    with open(inputfile, "r") as infile:
                        with open(outputfile, "w", newline='') as outfile:
                            reader = csv.reader(infile)
                            writer = csv.writer(outfile)
                            for row in reader:
                                parsed_sig = SigParser().parse(row[0])
                                writer.writerow([parsed_sig])
                        print(f"Output written to {outputfile}")
                        break
                else:
                    print("Both files must end with .csv. Please try again.")
            except ValueError:
                print("Invalid. Enter input and output file names separated by a space.")
            except FileNotFoundError:
                print("Input file not found. Please try again.")


if __name__ == "__main__":
    main()