import argparse

prog = 'calc_metadata_tfidf'
__version__ = "0.0.1"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog=prog)
    parser.add_argument("--infile", help="source file")
    parser.add_argument("--label", help="label file")
    parser.add_argument("--outfile", help="output file")
    parser.add_argument("--version", action='version', version='%(prog)s ' + __version__)

    args = parser.parse_args()
    yolo_labels = {}

    print(f'Reading labels')
    with open(args.label, 'r') as lbl:

        for line in lbl:

            fields = line.strip().split("\t")
            # print(f'Fields: {fields}')
            if len(fields) == 3:
                yolo_labels[fields[0]] = fields[2]
            elif len(fields) == 2:
                yolo_labels[fields[0]] = "NO_OBJECTS_DETECTED"
            else:
                print(f'Warning: didn\'t process {line}')

    print(f'Augmenting metadata')
    with open(args.infile, 'r') as infile, open(args.outfile, "w") as outfile:
        for line in infile:
            vid_id, rest  = line.split("\t", 1)  # only grab first field
            aug = line.strip() + "\t" + yolo_labels.get(vid_id, "MISSING_VIDEO") + "\n"
            outfile.write(aug)