import argparse
import re

prog = 'backfill_missing'
__version__ = "0.0.1"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog=prog)
    parser.add_argument("--infile", help="input ASR corpus with MISSING lines")
    parser.add_argument("--gold", help="Gold training data for backfill")
    parser.add_argument("--outfile", help="output corpus")
    parser.add_argument("--stats", help="output statistics file")
    parser.add_argument("--version", action='version', version='%(prog)s ' + __version__)

    args = parser.parse_args()

    # compile MISSING: detector
    missing_re = re.compile('^MISSING:')
    blank_re = re.compile('^\s+$')
    misslist = []
    misscount = 0
    blanklist = []
    blankcount = 0
    ctr = 1
    with open(args.infile, 'r') as infile, open(args.gold, 'r') as goldfile, open(args.outfile, 'w') as outfile:

        for inline in infile:
            goldline = goldfile.readline().strip()
            inline = inline.strip()

            if missing_re.match(inline):
                print(f'{ctr} found missing')
                outline = goldline
                misscount += 1
            elif inline == '':  # blank_re.match(inline)
                print(f'{ctr} found blank line')
                outline = goldline
                blankcount += 1
            else:
                outline = inline

            outfile.write(f'{outline}\n')

            ctr += 1

    # output stats
    with open(args.stats, 'w') as statsfile:
        statsfile.write(f'input:\t{args.infile}\n')
        statsfile.write(f'gold:\t{args.gold}\n')
        statsfile.write(f'output:\t{args.outfile}\n')
        statsfile.write(f'missing:\t{misscount}\n')
        statsfile.write(f'blank:\t{blankcount}\n')