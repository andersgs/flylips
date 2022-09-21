"""
Implements the CLI comoponent of the tool.

It will take either a list of files, or a directory, or a single file with a list of files as input
and will output a CSV file with the results.

It will optionally plot results to PNG files if the --plot option is used.
"""

import argparse
import pathlib
from flylips import __version__ as version
from flylips.wing import Wing
from flylips.combined_plot import combined_plot

USAGE = """
    - With a list of files (e.g., wing1.txt wing2.txt wing3.txt):
        flylips -i wing1.txt wing2.txt wing3.txt
        OR
        flylips --input *.txt
    - With a directory (e.g., /path/to/wings):
        flylips -d /path/to/wings
        OR
        flylips --directory /path/to/wings
    - With a file with a list of files one per line (e.g., /path/to/wings.txt):
        flylips -f /path/to/wings.txt
        OR
        flylips --file /path/to/wings.txt
    - With a list of files and output to a CSV file (e.g., /path/to/wings.csv):
        flylips -i wing1.txt wing2.txt wing3.txt -o /path/to/wings.csv
"""

def parse_args():
    """
    Parse the arguments from the command line prompt.
    For input, we can either specify a list of files, a directory, or a file with a list of files.
    The list of input files will be stored in a list, and have the -i/--input option
    The directory will be stored as a pathlib.Path object, and have the -d/--directory option
    The file with a list of files will be stored as a pathlib.Path object, and have the -f/--file option
    The csv output will default to stdout, but can be specified with the -o/--output option
    """
    parser = argparse.ArgumentParser(usage=USAGE, description="Estimate the size and shape of a fly wing using an Ellipse")
    parser.add_argument('-i', '--input', nargs='+', help='Input files', type=pathlib.Path)
    parser.add_argument('-d', '--directory', help='Input directory', type=pathlib.Path)
    parser.add_argument('-f', '--file', help='File with list of input files', type=pathlib.Path)
    parser.add_argument('-o', '--output', help='Output CSV file', default='-', type=argparse.FileType('w'))
    parser.add_argument('-p', '--plot', action='store_true', help='Plot results to PNG files')
    parser.add_argument('--version', action='version', version=f'%(prog)s {version}')
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    files = []
    if args.input:
        files.extend(args.input)
    elif args.directory:
        files.extend(args.directory.glob('*.txt'))
    elif args.file:
        with open(args.file) as f:
            files.extend([pathlib.Path(line.strip()) for line in f.readlines()])
    else:
        print("No input specified")
    
    wings = []
    for ix,file in enumerate(files):
        wing = Wing(file)
        wings.append(wing)
        try:
            wing.report(outfile=args.output, include_header=(ix==0))
        except ValueError as e:
            print(e)
            continue
        
        if args.plot:
            wing.plot()
            wing.plot_anchor_points()
    combined_plot(wings)
if __name__ == "__main__":
    main()