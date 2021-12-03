import argparse
import glob
import sys
# import os
# import pathlib
# from datetime import datetime

prog = 'map_yolo_labels'
__version__ = "0.0.1"

# YOLOv5 COCO Classes
nc = 80  # number of classes
names = ['PERSON', 'BICYCLE', 'CAR', 'MOTORCYCLE', 'AIRPLANE', 'BUS', 'TRAIN', 'TRUCK', 'BOAT', 'TRAFFIC_LIGHT',
         'FIRE_HYDRANT', 'STOP_SIGN', 'PARKING_METER', 'BENCH', 'BIRD', 'CAT', 'DOG', 'HORSE', 'SHEEP', 'COW',
         'ELEPHANT', 'BEAR', 'ZEBRA', 'GIRAFFE', 'BACKPACK', 'UMBRELLA', 'HANDBAG', 'TIE', 'SUITCASE', 'FRISBEE',
         'SKIS', 'SNOWBOARD', 'SPORTS_BALL', 'KITE', 'BASEBALL_BAT', 'BASEBALL_GLOVE', 'SKATEBOARD', 'SURFBOARD',
         'TENNIS_RACKET', 'BOTTLE', 'WINE_GLASS', 'CUP', 'FORK', 'KNIFE', 'SPOON', 'BOWL', 'BANANA', 'APPLE',
         'SANDWICH', 'ORANGE', 'BROCCOLI', 'CARROT', 'HOT_DOG', 'PIZZA', 'DONUT', 'CAKE', 'CHAIR', 'COUCH',
         'POTTED_PLANT', 'BED', 'DINING_TABLE', 'TOILET', 'TV', 'LAPTOP', 'MOUSE', 'REMOTE', 'KEYBOARD', 'CELL_PHONE',
         'MICROWAVE', 'OVEN', 'TOASTER', 'SINK', 'REFRIGERATOR', 'BOOK', 'CLOCK', 'VASE', 'SCISSORS', 'TEDDY_BEAR',
         'HAIR_DRIER', 'TOOTHBRUSH']  # class names

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog=prog)
    parser.add_argument("--src", help="source file")
    parser.add_argument("--out", help="output label file")
    parser.add_argument("--lbldir", help="label directory")
    parser.add_argument("--hist", help="class histogram", default="out.hist")
    # parser.add_argument("--err", help="error report", default="out.err")
    parser.add_argument("--version", action='version', version='%(prog)s ' + __version__)
    # buffers for corpus bleu
    args = parser.parse_args()

    objhist = {}

    # init class counts
    for n in names:
        objhist[n] = 0

    # stub for output classes as user-defined SPM tokens
    # with open('yolov5-all.classes', 'w') as c:
    #    c.write(",".join(names))
    # sys.exit(0)

    ctr = 0
    with open(args.src, 'r') as src, open(args.out, 'w') as lbl:
        for line in src:

            # we start at 1
            ctr += 1
            # find frame snaps for objects (line_frame.txt)
            pattern = f'{args.lbldir}/{ctr}/{ctr}_*.txt'
            matches = glob.glob(pattern)
            # sanity check
            # matches.sort()
            # print(f'{ctr}: matches: {len(matches)} :: {pattern}')

            detobjs = {}

            for name in matches:
                # print(f' {ctr}: {pattern} : {name}')

                # open file and process
                try:
                    with open(name, 'r') as objs:
                        for obj in objs:
                            fields = obj.strip().split(" ")
                            # okey = names[fields[0]]
                            detobjs[names[int(fields[0])]] = True
                except:
                    sys.stderr.write(f"Warning: {name} not found!")

            # print(f'{ctr}: objs: {detobjs}')
            lbl.write(f'{ctr}\t{" ".join(detobjs.keys())}\n')

            # increment global counts
            for k in detobjs.keys():
                objhist[k] += 1

            # debug
            # break

    print(f'Done ({ctr})')

    # write histogram
    with open(args.hist, "w") as h:

        for k, v in objhist.items():
            print(f'{k}\t{v}')
            h.write(f'{k}\t{v}\n')

