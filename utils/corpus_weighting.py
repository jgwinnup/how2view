import argparse

prog = 'corpus weighting'
__version__ = "0.0.1"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog=prog)
    parser.add_argument("--tune", )
    parser.add_argument("--metadata", help="filtered metadata (no test/val video ids")
    parser.add_argument("--corpus_segments", help="corpus segments")
    parser.add_argument("--weights", help="output weights")
    parser.add_argument("--version", action='version', version='%(prog)s ' + __version__)

    args = parser.parse_args()