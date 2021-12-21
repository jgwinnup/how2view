import argparse
import math
import pickle
import string

import numpy as np
import pandas as pd
from nltk import word_tokenize
from nltk.corpus import stopwords
from sklearn.metrics.pairwise import cosine_similarity

prog = 'corpus weighting'
__version__ = "0.0.1"


# Tokenize with NLTK's punkt tokenizer, stopword and punctuation removal
def tokenize(sent):
    ww = word_tokenize(sent)
    return [w.lower() for w in ww if (not w.lower() in stop_words) and (not w in string.punctuation)]


# get cosine similarities
def get_tfidf_query_similarity(vectorizer, docs_tfidf, query, num_results=5):

    query_tfidf = vectorizer.transform([" ".join(tokenize(query))])
    cosine_sim = cosine_similarity(query_tfidf, docs_tfidf).flatten()

    top_results = cosine_sim.argsort()[:-(num_results + 1):-1]  # yes this is weird
    sim_scores = [cosine_sim[r] for r in top_results]

    return top_results, sim_scores


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog=prog)
    parser.add_argument("--tune", help="val/test set to tune against" )
    parser.add_argument("--metadata", help="filtered metadata (no test/val video ids")
    parser.add_argument("--train_corpus_ids", help="training corpus segments")
    parser.add_argument("--weights", help="output weights")
    parser.add_argument("--default_weight", default=0.25, help="default_weight (default=0.25)", type=float)
    parser.add_argument("--top_k", default=5, help="top-k closest matches", type=int)
    parser.add_argument("--model", help="sklearn TF-IDF model")
    parser.add_argument("--vectorizer", help="sklearn TF-IDF vectorizer")
    parser.add_argument("--stats", help="output statistics file")
    parser.add_argument("--version", action='version', version='%(prog)s ' + __version__)

    args = parser.parse_args()

    # load nltk stop words
    stop_words = set(stopwords.words('english'))

    # pandas because why not
    field_list = ['id', 'duration', 'likecount', 'dislikecount', 'title', 'tags', 'description', 'objects']
    meta_df = pd.read_csv(args.metadata, sep='\t', names=field_list)

    # load model and vectorizer
    tfidf = pickle.load(open(args.model, 'rb'))
    tfidf_vectorizer = pickle.load(open(args.vectorizer, 'rb'))

    vid_counts = {}
    ctr = 1
    zerocnt = 0
    with open(args.tune, 'r') as tune:
        for line in tune:
            query = line.strip()
            results, scores = get_tfidf_query_similarity(tfidf_vectorizer, tfidf, query, args.top_k)
            # map indices
            res_df = meta_df.iloc[results]
            ids = res_df['id'].tolist()
            # print(f'{ctr}: {list(zip(ids, scores))}')
            for r, s in zip(ids, scores):
                # don't add results with zero score
                if s > 0.0:
                    if r not in vid_counts:
                        vid_counts[r] = []
                    vid_counts[r].append(s)
                else:
                    zerocnt += 1
            ctr += 1

    # calculate some stats so I can figure out how to scale these values
    idmax = ''
    cntmax = 0
    idmin = ''
    cntmin = math.inf

    scalemax = 0.0
    scalemin = math.inf
    vid_weights = {}
    norm_vid_weights = {}

    print(f'Calculating raw scores for {len(vid_counts)} videos')
    for k, v in vid_counts.items():
        # statistics
        if len(v) > cntmax:
            idmax = k
            cntmax = len(v)
        if len(v) < cntmin:
            idmin = k
            cntmin = len(v)

        # first stab: count * avg score, then normalize
        raw_score = float(len(v)) * np.mean(v)
        if raw_score > scalemax:
            scalemax = raw_score
        if raw_score < scalemin:
            scalemin = raw_score
        vid_weights[k] = raw_score

    # L1 normalize scores
    print(f'Normalizing scores for {len(vid_counts)} videos')
    for k, v in vid_weights.items():
        scaled = (v - scalemin) / (scalemax - scalemin)
        # print(f"{k} {v} -> {scaled}")
        norm_vid_weights[k] = scaled

    # Create weights file
    ctr = 1
    missing_count = 0
    with open(args.train_corpus_ids, 'r') as train_ids, open(args.weights, 'w') as weights:
        for line in train_ids:
            id = line[:11]  # youtube videos only first 11 chars
            # short circuit for now
            if id in norm_vid_weights:
                # weights.write(f'{1.0}\n')
                # weights.write(f'{norm_vid_weights[id]}\n')
                # weights.write(f'{norm_vid_weights[id]}\n')
                weights.write(f'{args.default_weight}\n')
            else:
                # print(f'{ctr} {id} No weight found! Using default: {args.default_weight}')
                missing_count += 1
                weights.write(f'{1.0}\n')
                #weights.write(f'{args.default_weight}\n')
            ctr += 1

    with open(args.stats, 'w') as stats:
        print(f'Max count: {idmax} - {cntmax} mean score: {np.mean(vid_counts[idmax])} max score: {np.max(vid_counts[idmax])} min score: {np.min(vid_counts[idmax])}')
        stats.write(f'Max count: {idmax} - {cntmax} mean score: {np.mean(vid_counts[idmax])} max score: {np.max(vid_counts[idmax])} min score: {np.min(vid_counts[idmax])}\n')
        print(f'Min count: {idmin} - {cntmin} mean score: {np.mean(vid_counts[idmin])} max score: {np.max(vid_counts[idmin])} min score: {np.min(vid_counts[idmin])}')
        stats.write(f'Min count: {idmin} - {cntmin} mean score: {np.mean(vid_counts[idmin])} min score: {np.min(vid_counts[idmin])} min score: {np.min(vid_counts[idmin])}\n')
        print(f'Num zero scores: {zerocnt}')
        stats.write(f'Num zero scores: {zerocnt}\n')
        print(f'Missing video count: {missing_count}')
        stats.write(f'Missing video count: {missing_count}\n')
        print(f'Metadata records: {meta_df.size}')
        stats.write(f'Metadata records: {meta_df.size}\n')
        print(f'Query video matches: {len(vid_weights)}')
        stats.write(f'Query video matches: {len(vid_weights)}\n')
        print(f'Raw max score: {scalemax}')
        stats.write(f'Raw max score: {scalemax}')
        print(f'Raw min score: {scalemin}')
        stats.write(f'Raw min score: {scalemax}')

