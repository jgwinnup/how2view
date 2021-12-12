import argparse
import pickle
import string

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer

prog = 'calc_metadata_tfidf'
__version__ = "0.0.1"


# Tokenize with NLTK's punkt tokenizer, stopword and punctuation removal
def tokenize(sent):
    ww = word_tokenize(sent)
    return [w.lower() for w in ww if (not w.lower() in stop_words) and (not w in string.punctuation)]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog=prog)
    parser.add_argument("--infile", help="segment file with labels")
    parser.add_argument("--outfile", help="output tfidf weights")
    parser.add_argument("--outvec", help="output tfidf vectorizer")
    parser.add_argument("--version", action='version', version='%(prog)s ' + __version__)

    args = parser.parse_args()

    # download tokenizer rules and stopwords if needed
    nltk.download('punkt')
    nltk.download('stopwords')

    # use English stopwords
    stop_words = set(stopwords.words('english'))

    # load metadata extracted from json
    print("Reading metadata")
    train_set = []
    with open(args.infile, 'r') as infile:
        for line in infile:
            fields = line.split('\t')
            if len(fields) > 2: # 5:
                # train on tokenized title + description
                # text = fields[4] + " " + fields[6]

                # train on tokenized object labels
                text = fields[-1]

                train_set.append(" ".join(tokenize(text)))
            else:
                print(f"Warning: num fields {len(fields)}: {line}")

    print("Training TD-IDF")

    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(train_set)

    print(f"Dumping tdfidf matrix to {args.outfile}")
    pickle.dump(tfidf_matrix, open(args.outfile, 'wb'))
    pickle.dump(tfidf_vectorizer, open(args.outvec, 'wb'))