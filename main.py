from parsers.sig import *
import sys, argparse


def main():
    parser = setup_parser()
    args = parser.parse_args()

    if len(sys.argv) <= 1:
        parser.print_usage()
        sys.exit("Error: No arguments provided")
    elif args.m:
        generate_single()
    elif args.b:
        input_file, output_file = args.b
        check_csv_files(args.b)
        generate_bulk(input_file, output_file)
    else:
        sys.exit("An unknown error occured.")


def setup_parser():
    parser = argparse.ArgumentParser(
        prog="ParseRx",
        description="A modern, lightweight medication sig parser.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-m", nargs=argparse.REMAINDER, help="""Enter a single sig to parse."""
    )
    parser.add_argument(
        "-b",
        nargs=2,
        metavar=("input.csv", "output.csv"),
        help="""Bulk sig instructions:
> Place your input file in the /csv directory.
> Input files are read from the /csv directory.
> Output files are written to the /csv/output directory.
> Enter the input file name (input.csv as default) and output file name (output.csv as default), separated by a space.""",
    )
    return parser


def check_csv_files(filenames):
    for filename in filenames:
        if not filename.endswith(".csv"):
            raise argparse.ArgumentTypeError("All files must have a .csv extension")
    return filenames


def generate_single():
    print(SigParser().parse(" ".join(sys.argv[1:])))


def generate_bulk(input, output):
    SigParser().parse_sig_csv(input, output)


if __name__ == "__main__":
    main()
