import argparse
import pickle
from random import sample

prog = 'sample_selected_lines'
__version__ = "0.0.1"

if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog=prog)

    parser.add_argument("--infile", help="input data file with weights")
    parser.add_argument("--selected", help="pickle with selected indices")
    parser.add_argument("--outfile", help="output data file with selected lines")

    args = parser.parse_args()

    with open(args.selected, 'rb') as handle:
        idxs = pickle.load(handle)
        sidxs = set(idxs)


    with open(args.infile, 'r') as infile, open(args.outfile, 'w') as outfile:

        ctr = 1
        for line in infile:

            if ctr in sidxs:
                outfile.write(line)

            ctr += 1