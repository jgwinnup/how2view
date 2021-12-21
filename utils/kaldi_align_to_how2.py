import argparse
import sys

prog = 'kaldi_align_to_how2'
__version__ = "0.0.1"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog=prog)
    # parser.add_argument("--infile", help="segment file with labels")
    parser.add_argument("--outfile", help="output video id file with labels")
    parser.add_argument("--stats", help="output statistics file")
    parser.add_argument("--haystack", help="haystack processing ID map")
    parser.add_argument("--haydir", help="Haystack utterance output directory")
    parser.add_argument("--segid", help="how2 segment ID with timing")
    parser.add_argument("--fudge", type=float, help="Timestamp fudge factor (default=0.0, try 0.1)", default=0.0)
    parser.add_argument("--version", action='version', version='%(prog)s ' + __version__)

    args = parser.parse_args()

    haymap = {}

    # process haystack video id map
    with open(args.haystack, 'r') as haystack:
        first = True
        for line in haystack:
            # Skip header line
            if first:
                first = False
            else:
                fields = line.strip().split("\t")
                if len(fields) > 1:
                    vidid = fields[1][:11]  # youtube IDs are 11 chars
                    # print(f'hay id: {fields[0]} youtube id: {vidid}')

                    if vidid in haymap:
                        print(f'{fields[0]} Warning: Video {vidid} already listed with {haymap[vidid]}')
                        # should make this optional/flag
                        haymap[vidid] = fields[0]
                    else:
                        haymap[vidid] = fields[0]
                else:
                    print(f'Warning: ({len(fields)}) {fields}')

    # Work on segment file
    misslist = {}
    misscount = 0
    emptycount = 0
    ctr = 1
    with open(args.segid, 'r') as segments, open(args.outfile, 'w') as outfile:
        for line in segments:
            fields = line.strip().split(' ')
            # print(f'({len(fields)}): {fields}')
            vidid = fields[1]
            start = float(fields[2]) - args.fudge
            end = float(fields[3]) + args.fudge
            hayid = haymap.get(vidid, "MISSING")

            if hayid == 'MISSING':
                outfile.write(f'MISSING: {vidid} {start} {end}\n')
                misslist[vidid] = True
                misscount += 1
            else:
                # look up video id to haystack ID map
                capture = False
                print(f'Vid {vidid} -> hay {hayid} - start: {start} end: {end}')
                with open(f'{args.haydir}/{hayid}.utterance', 'r') as ufile:
                    done = False
                    outsents = []
                    for uline in ufile:
                        ustart, uend, utterance = uline.strip().split(' ', 2)
                        ustart = float(ustart)  # - args.fudge
                        uend = float(uend)  # + args.fudge
                        if ustart > start:
                            capture = True
                        # watch this...
                        if ustart > end:
                            capture = False
                        if capture:
                            print(f'ufields: start: {ustart} end: {uend} - {utterance}')
                            outsents.append(utterance)

                    outline = " ". join(outsents) # remove extra spaces
                    if outline == "":
                        print(f'{ctr} Warning: empty line')
                        emptycount += 1
                    print(f'{ctr}: {outline} ')
                    outfile.write(f'{outline}\n')
            ctr += 1

    with open(args.stats, 'w') as statsfile:
        # write out stats
        statsfile.write(f'output corpus:\t{args.outfile}\n')
        statsfile.write(f'segments:\t{args.segid}\n')
        statsfile.write(f'haystack id:\t{args.haystack}\n')
        statsfile.write(f'haystack dir:\t{args.haydir}\n')
        statsfile.write(f'fudge factor:\t{args.fudge}\n')
        statsfile.write(f'corpus length:\t{ctr}\n')
        statsfile.write(f'missing count:\t{misscount}\n')
        statsfile.write(f'empty count:\t{emptycount}\n')

        # write like this for easy extractions
        statsfile.write(f'Missing videos {len(misslist)} by id:\n')
        for k in misslist.keys():
            statsfile.write(f'{k}\n')
