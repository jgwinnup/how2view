import argparse

prog = 'exclude_video_ids'
__version__ = "0.0.1"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog=prog)
    parser.add_argument("--infile", help="metadata file")
    parser.add_argument("--exclude", help="exclude video ids")
    parser.add_argument("--outfile", help="pruned metadata file")
    parser.add_argument("--version", action='version', version='%(prog)s ' + __version__)

    args = parser.parse_args()

    exclude = {}
    # read exclusion list
    with open(args.exclude, 'r') as exfile:

        # assumes 11 char youtube video id...
        for line in exfile:
            exclude[line.strip()] = True

    # process metadata file and write out non-excluded entries
    exclude_count = 0
    with open(args.infile, 'r') as infile, open(args.outfile, 'w') as outfile:

        for line in infile:
            vid_id, rest = line.split("\t", 1)
            if vid_id in exclude:
                print(f'Excluding video id {vid_id}')
                exclude_count += 1
            else:
                outfile.write(line)  # already has LF

    print(f'Total videos excluded: {exclude_count}')
