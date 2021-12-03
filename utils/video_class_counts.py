import argparse
import sys

prog = 'video_class_counts'
__version__ = "0.0.1"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog=prog)
    parser.add_argument("--infile", help="segment file with labels")
    parser.add_argument("--outclass", help="output video id file with labels")
    parser.add_argument("--version", action='version', version='%(prog)s ' + __version__)

    args = parser.parse_args()

    classcount = {}
    # prime the pump
    classcount["NONE"] = 0

    with open(args.infile, 'r') as infile, open(args.outclass, 'w') as outclass:
        ctr = 1
        for line in infile:

            fields = line.strip().split("\t")

            # make sure we actually have labels
            if len(fields) > 2:
                labels = fields[2].split(" ")
                # is this right?
                if len(labels) == 0:
                    classcount["NONE"] += 1
                else:
                    for label in labels:
                        if label not in classcount:
                            classcount[label] = 1
                        else:
                            classcount[label] += 1
            else:
                classcount["NONE"] += 1

        # sort and output
        sort_classcount = sorted(classcount.items(), key=lambda item: item[1], reverse=True)
        for k, v in sort_classcount:
            outclass.write(f"{k}\t{v}\n")



