import argparse

# run on .labels files

prog = 'segment_object_hist'
__version__ = "0.0.1"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog=prog)
    parser.add_argument("--infile", help="segment file with labels")
    parser.add_argument("--outfile", help="output video id file with labels")
    parser.add_argument("--version", action='version', version='%(prog)s ' + __version__)

    args = parser.parse_args()

    counts = {}
    counts[0] = 0
    with open(args.infile, 'r') as infile:
        for line in infile:

            fields = line.strip().split('\t')

            if len(fields) > 1:
                objs = fields[1].split(' ')
                lenobj = len(objs)
                # if not counts[lenobj]:
                if lenobj not  in counts:
                    counts[lenobj] = 0
                counts[lenobj] += 1
            # no objects
            else:
                counts[0] += 1

    with open(args.outfile, 'w') as outfile:
        #for i, c in enumerate(counts):
        for i, c in counts.items():
            print(f'{i}\t{c}')
            outfile.write(f'{i}\t{c}\n')
