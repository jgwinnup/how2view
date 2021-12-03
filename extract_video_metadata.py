#!/usr/bin/env python

import argparse
import glob
import sys
import json
import statistics

prog = 'extract_video_metadata'
__version__ = "0.0.1"

videodir = '/tmpssd2/how2-dataset/how2/how2'

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog=prog)
    parser.add_argument("--videodir", help="video directory")
    parser.add_argument("--out", help="output flat file")
    parser.add_argument("--tags", help="output tag counts")
    parser.add_argument("--version", action='version', version='%(prog)s ' + __version__)

    args = parser.parse_args()

    # diagnostic info
    print(f'video dir: {args.videodir}')
    print(f'out file:  {args.out}')

    # statistics containers
    ctr = 0
    ids = []
    desc_length = []
    duration = []
    likes = []
    dislikes = []
    tags = []

    tagcounts = {}

    with open(args.out, "w") as out:

        pattern = f'{args.videodir}/*.json'
        matches = glob.glob(pattern)

        for file in matches:
            with open(file, 'r') as j:
                meta = json.load(j)
                # print(f'file: {file} id: {meta["id"]}')

                id = meta["id"]
                dur = meta["duration"]
                lc = meta["like_count"]
                title = meta["title"].replace("\n", " ")
                dc = meta["dislike_count"]
                t = ",".join(meta["tags"])
                desc = meta["description"].replace("\n", " ")

                out.write(f"{id}\t{dur}\t{lc}\t{dc}\t{title}\t{t}\t{desc}\n")

                ids.append(meta["id"])
                desc_length.append(len(meta["description"]))
                duration.append(meta["duration"])
                likes.append(meta["like_count"])
                dislikes.append(meta["dislike_count"])
                tags.append(meta["tags"])

                for tg in meta["tags"]:
                    if tg in tagcounts:
                        tagcounts[tg] += 1
                    else:
                        tagcounts[tg] = 1

                # Only increment on success
                ctr += 1

    desc_mean = statistics.mean(desc_length)
    desc_median = statistics.median(desc_length)
    avg_duration = statistics.mean(duration)
    avg_likes = statistics.mean(likes)
    avg_dislikes = statistics.mean(dislikes)

    # calculate tag statistics
    taghist = [(k, v) for k, v in tagcounts.items()]
    taghist.sort(key=lambda x: x[1], reverse=True)


    print(f'Description mean length: {desc_mean}')
    print(f'Description median length: {desc_median}')
    print(f'Average duration: {avg_duration}')
    print(f'Average likes: {avg_likes}')
    print(f'Average dislikes: {avg_dislikes}')
    print(f'Unique Tags: {len(taghist)}')


    # try extracting TF-IDF features

    with open(args.tags, "w") as tagout:
        for x in taghist:
            tagout.write(f"{x[0]}\t{x[1]}\n")


