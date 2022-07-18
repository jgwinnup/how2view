import argparse
import pickle
from random import sample

prog = 'calc_random_sample_lines'
__version__ = "0.0.1"

if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog=prog)

    parser.add_argument("--infile", help="input data file with weights")
    parser.add_argument("--num-samples", type=int, help="number of sampled indices")
    parser.add_argument("--outfile", help="output line indices file")

    args = parser.parse_args()

    # get count of line from input file
    with open(args.infile, 'r') as infile:
        num_lines = sum(1 for line in infile)

    k = args.num_samples
    if k > num_lines:
        print(f'Warning: asked for {k} samples from a file with {num_lines} lines.')
        k = num_lines

    print(f'{args.infile} has {num_lines} lines, sampling {k}.')

    #
    idxs = sorted(sample(range(num_lines), k), reverse=True)

    print(f'Writing indices to {args.outfile}')
    with open(f'{args.outfile}', 'wb') as handle:
        pickle.dump(idxs, handle, protocol=pickle.HIGHEST_PROTOCOL)
