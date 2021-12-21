import argparse
from os import path

prog = 'check_missing_videos'
__version__ = "0.0.1"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog=prog)
    parser.add_argument("--infile", help="missing list")
    parser.add_argument("--videodir", help="video directory")
    parser.add_argument("--outfile", help="output list with status")
    parser.add_argument("--haystack", help="haystack processing ID map")
    parser.add_argument("--version", action='version', version='%(prog)s ' + __version__)

    args = parser.parse_args()
    vdir = args.videodir  # for brevity

    # process haystack video id map
    haymap = {}
    if args.haystack:
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
                        else:
                            haymap[vidid] = fields[0]
                    else:
                        print(f'Warning: ({len(fields)}) {fields}')



    with open(args.infile, 'r') as infile, open(args.outfile, 'w') as outfile:

        for line in infile:
            vidid = line.strip()

            # build base filename
            found = []
            hayproc = 'hay:no'
            base = f'{vdir}/{vidid}'

            # check file existence
            if path.exists(base + ".mp4"):
                found.append('mp4')
            if path.exists(base + ".mkv"):
                found.append('mkv')

            if len(found) == 0:
                found.append('MISSING_VIDEO')

            # check if in Haystack processed map (answer should be no)
            if vidid in haymap:
                hayproc = 'hay:yes'

            print(f'{vidid}\t{",".join(found)}\t{hayproc}')
            outfile.write(f'{vidid}\t{",".join(found)}\t{hayproc}\n')




