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
        parsed_sig = SigParser().parse(sig)
        sig_text = parsed_sig['sig_text']
        sig_readable = parsed_sig['sig_readable']
        print(f'\n**********************************\n\n{sig_text}   -->   {sig_readable}\n\n**********************************')
    else:
        while True:
            try:
                input_file, output_file = input("\n\n**********************************\nPlace your input file in the /csv directory.\n**********************************\n > Input files are read from the /csv directory.\n > Output files are written to the /csv/output directory.\n\n**********************************\nEnter the input file name (input.csv as default) and output file name (output.csv as default), separated by a space.\n").split(
                    " "
                )
                if input_file.endswith(".csv") and output_file.endswith(".csv"):
                    SigParser().parse_sig_csv(input_file, output_file)
                    print(f"Output written to {output_file}")
                else:
                    print("Both files must end with .csv. Please try again.")
            except ValueError:
                print("Invalid. Enter input and output file names separated by a space.")
            except FileNotFoundError:
                print("Input file not found. Please try again.")


if __name__ == "__main__":
    main()
