import argparse
import pickle

prog = 'corpus_drop_labels'
__version__ = "0.0.1"

# YOLOv5 COCO Classes
# nc = 80  # number of classes
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
    parser.add_argument("--infile", help="input file")
    parser.add_argument("--labels", help="labels file")
    parser.add_argument("--drop-list", help="comma separated list of labels to drop")
    parser.add_argument("--outfile", help="output weights file")
    parser.add_argument("--space-labels", default=False, action='store_true', help="Add spaces between output labels (for prespm systems)")
    parser.add_argument("--report", help="Report file for dropped labels")
    # option for formatting output labels

    args = parser.parse_args()

    with open(args.infile, 'r') as infile, open(args.labels, 'r') as labelfile, open(args.outfile, 'w') as outfile, open(args.report, 'w') as report:

        droplist = []

        potentialdrops = args.drop_list.split(',')

        for p in potentialdrops:
            if p in names:
                print(f'Dropping label {p}')
                # report.write(f'Dropping label {p}\n')
                droplist.append(p)
            else:
                print(f'Invalid label: {p}')

        # report.write(f'Pruning {metric} scores less than {thresh}\n')

        totallbl = 0
        droplbl = 0

        for line, labelline in zip(infile, labelfile):

            line = line.strip()
            labels = labelline.strip().split('\t')

            outlabels = []
            # print(f'Length: {len(labels)}')
            # If we have labels, see if they're in droplist
            if len (labels) == 2:
                lbls = labels[1].split(" ")
                for lbl in lbls:
                    totallbl += 1
                    if lbl not in droplist:
                        outlabels.append(lbl)
                    else:
                        droplbl += 1

            # make this fancier in the future
            # Output in despaced form so Marian can spm the input
            if args.space_labels:
                outlabelstr = ' '.join(outlabels)
            else:
                outlabelstr = ''.join(outlabels)

            outline = []
            if args.space_labels:
                outfile.write(f'{line} {outlabelstr}\n')
            else:
                outfile.write(f'{line}{outlabelstr}\n')

        # finish up report
        report.write(f'{totallbl} labels\n')
        report.write(f'{droplbl} {(float(droplbl)/float(totallbl))*100.0:0.4f}% dropped labels\n')

        # write dropped labels with scores
        for d in droplist:
            report.write(f'Dropped label {d}\n')





