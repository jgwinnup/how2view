import argparse
import pickle

prog = 'tfidf_label_weight_corpus'
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
    parser.add_argument("--infile", help="input data file with weights")
    parser.add_argument("--weights", help="Weights pickle")
    parser.add_argument("--outfile", help="output weights file")

    args = parser.parse_args()

    with open(args.weights, 'rb') as handle:
        weights = pickle.load(handle)

    with open(args.infile, 'r') as infile, open(args.outfile, 'w') as outfile:

        for line in infile:

            outline = []
            tokens = line.strip().split()

            for t in tokens:
                # if token matches a label in weights, use norm'd TF-IDF weight
                # otherwise it's a normal word and put weight 1.0
                tw = 1.0
                if t in weights:
                    tw = weights[t]['norm_tfidf']

                outline.append(str(tw))  # write it as a string...

            outfile.write(" ".join(outline) + '\n')