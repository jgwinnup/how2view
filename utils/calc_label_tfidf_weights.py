import argparse
import math
import pickle
import string

prog = 'calc_label_tfidf_weights'
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
    parser.add_argument("--labels", help="Labels (all) file corresponding to infile")
    parser.add_argument("--weights", help="output weight table +(python pickle)")

    args = parser.parse_args()

    label_weights = {}

    numDocs = 0
    wordCount = 0
    docFreq = {}
    docLen = {}
    termFreq = {}
    termIDF = {}
    output = {}

    with open(args.labels, 'r') as lblfile:
        for line in lblfile:

            numDocs += 1

            docTerms = {}

            tokens = line.strip().split(" ")[1:]
            wordCount += len(tokens)

            for token in tokens:

                if token in termFreq.keys():
                    termFreq[token] += 1
                else:
                    termFreq[token] = 1

                # get term occurrences for this document
                if token in docTerms.keys():
                    docTerms[token] += 1
                else:
                    docTerms[token] = 1

                # account for document freq
                if token in docFreq.keys():
                    # seems backwards but I'm missing something getting initialized
                    if numDocs in docFreq[token].keys():
                        docFreq[token][numDocs] += 1
                    else:
                        docFreq[token][numDocs] = 1
                else:
                    docFreq[token] = {}
                    docFreq[token][numDocs] = 1
                    # print(f'adding {token} :: {self.curID} :: {docFreq[token][self.curID]}')

            docLen[numDocs] = docTerms

    # Convert docFreq lists to counts
    # docFreqCount = {}
    # for k in docFreq.keys():
    #    docFreqCount[k] = len(docFreq[k].keys())

    max_idf = 0.0
    min_idf = 999999.0
    for k, v in docFreq.items():
        idf = math.log2(numDocs / float(len(v)))

        if idf < min_idf:
            min_idf = idf

        if idf > max_idf:
            max_idf = idf
        termIDF[k] = idf

    print(f'max idf: {max_idf} min idf: {min_idf}')

    # build output structure
    max_tfidf = 0.0
    min_tfidf = 999999.0

    # once to get range
    for k in names:

        cur_tf = termFreq.get(k, 0)
        cur_idf = termIDF.get(k, 0)
        cur_tfidf = cur_tf * cur_idf

        if cur_tfidf < min_tfidf:
            min_tfidf = cur_tfidf

        if cur_tfidf > max_tfidf:
            max_tfidf = cur_tfidf

        output[k] = {}
        output[k]['tf'] = cur_tf
        output[k]['idf'] = cur_idf
        output[k]['tfidf'] = cur_tfidf

    print(f'max idf: {max_tfidf} min idf: {min_tfidf}')

    # normalize via max_norm (so we don't lose min_norm weights)
    for k in names:
        output[k]['norm_tfidf'] = output[k]['tfidf'] / max_tfidf

    # debug
    with open(f'{args.weights}.csv', 'w') as weights:
        print(f'label\tTF\tIDF\tTFIDF\tNorm_IDF')
        weights.write(f'label\tTF\tIDF\tNorm_IDF\n')
        for k, v  in output.items():
            # print(f'{k}\t{termFreq.get(k, 0)}\t{termIDF.get(k, 0):0.4f}')
            print(f'{k}\t{v["tf"]}\t{v["idf"]:0.4f}\t{v["tfidf"]:0.4f}\t{v["norm_tfidf"]:0.4f}')
            weights.write(f'{k}\t{v["tf"]}\t{v["idf"]:0.4f}\t{v["tfidf"]:0.4f}\t{v["norm_tfidf"]:0.4f}\n')

    with open(f'{args.weights}.pickle', 'wb') as handle:
        pickle.dump(output, handle, protocol=pickle.HIGHEST_PROTOCOL)
