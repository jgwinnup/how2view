#!/usr/bin/env python

# Extract

import argparse
# import glob
# import sys
import json
# import statistics

# Note from the VATEX Paper:
# The video has 10 English and 10 Chinese descriptions. All depicts the same video and
# thus are distantly parallel to each other, while the last five are the paired
# translations to each other.

prog = 'extract_vatex'
__version__ = "0.0.1"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog=prog)
    parser.add_argument("--infile", help="segment file with labels")
    parser.add_argument("--outfile", help="output tab separated file")
    parser.add_argument("--paronly", default=False, action='store_true', help="Extract parallel data (cap 6-10) only")
    parser.add_argument("--test", default=False, action='store_true', help='Test set, only extract EN source')

    args = parser.parse_args()
    ctr = 0

    with open(args.infile, 'r') as infile, open(f'{args.outfile}', 'w') as outfile:

        meta = json.load(infile)

        for rec in meta:
            # id, clipstart, clipstop = rec['videoID':11].split('_')
            # clipstart = 0
            # clipstop = 0
            id = rec['videoID'][:11]
            clipstart, clipstop = rec['videoID'][12:].split('_')

            # zip English and Chinese captions with index

            if args.paronly:
                start = 5
            else:
                start = 0

            if args.test:
                for i, e in enumerate(rec['enCap'][start:]):
                    # print(f'{id}\t{clipstart}\t{clipstop}\t{i}\t{e}\t{z}')
                    outfile.write(f'{id}\t{clipstart}\t{clipstop}\t{i}\t{e}\n')
            else:
                for i, (e, z) in enumerate(zip(rec['enCap'][start:], rec['chCap'][start:])):
                    # print(f'{id}\t{clipstart}\t{clipstop}\t{i}\t{e}\t{z}')
                    outfile.write(f'{id}\t{clipstart}\t{clipstop}\t{i}\t{e}\t{z}\n')
