import argparse
import sys

# Use *.videolabel files to run this.

prog = 'segment_to_video_labels'
__version__ = "0.0.1"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog=prog)
    parser.add_argument("--infile", help="segment file with labels")
    parser.add_argument("--outfile", help="output video id file with labels")
    parser.add_argument("--outclass", help="output segment-based class counts")
    parser.add_argument("--version", action='version', version='%(prog)s ' + __version__)

    args = parser.parse_args()

    vidlist = {}
    classcount = {}

    with open(args.infile, "r") as infile, open(args.outfile, "w") as outfile:
        ctr = 1
        for line in infile:

            fields = line.strip().split("\t")

            # youtube video id's are 11 char (hopefully)
            vid = fields[0][:11] # .rsplit("_", 1)

            if vid not in vidlist:
                vidlist[vid] = []

            if len(fields) > 2:
                labels = fields[2].split(" ")

                for label in labels:
                    # do we track absent classes?
                    if label not in classcount:
                        classcount[label] = 1
                    else:
                        classcount[label] += 1
                # careful!
                vidlist[vid].extend(labels)

            # print(f'{ctr}: {vid}')
            ctr += 1

        for k, v in vidlist.items():
            print(f'{k}\t{" ".join(v)}')
            outfile.write(f'{k}\t{len(v)}\t{" ".join(v)}\n')

    with open(args.outclass, "w") as outclass:
        sort_classcount = sorted(classcount.items(), key=lambda item: item[1], reverse=True)
        for k, v in sort_classcount:
            outclass.write(f"{k}\t{v}\n")