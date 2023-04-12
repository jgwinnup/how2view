import glob
import json
import pickle
import string
from os.path import splitext, basename

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from nltk import word_tokenize
from nltk.corpus import stopwords
from sklearn.metrics.pairwise import cosine_similarity
from st_aggrid import AgGrid, GridUpdateMode, GridOptionsBuilder
from wordcloud import WordCloud

# datadir = '/tmpssd2/how2-dataset/how2/'
# videodir = f'{datadir}/how2'
# metafname = f'{datadir}/how2-metadata.txt'
# tagfname = f'{datadir}/how2-tags.txt'

# nocturnum for defense demo
datadir = '.'
videodir = f'{datadir}/how2'
metafname = f'model/how2-metadata.txt'
tagfname = f'model/how2-tags.txt'

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

# @st.cache
def load_desctitle_models():
    tfidf = pickle.load(open('model/how2-title+desc.tfidf', 'rb'))
    tfidf_vectorizer = pickle.load(open('model/how2-title+desc.vec', 'rb'))

    return tfidf, tfidf_vectorizer


# @st.cache
def load_yolov5_models():
    # used updated models with all labels
    tfidf = pickle.load(open('model/how2-yolov5labels-all.tfidf', 'rb'))
    tfidf_vectorizer = pickle.load(open('model/how2-yolov5labels-all.vec', 'rb'))

    return tfidf, tfidf_vectorizer


@st.cache_data
def get_videos(dirname):
    fnames = glob.glob(f'{datadir}/*.mp4')
    basenames = [splitext(basename(f))[0] for f in fnames]

    df = pd.DataFrame(basenames)

    return df

@st.cache_data
def load_metadata(fname):
    field_list = ['id', 'duration', 'likecount', 'dislikecount', 'title', 'tags', 'description', 'objects']
    df = pd.read_csv(fname, sep='\t', names=field_list)
    return df

@st.cache_data
def load_tags(fname):

    tags = {}
    with open(fname, 'r') as f:
        line = f.readline()

        while line:
            fields = line.strip().split('\t')
            tags[fields[0]] = int(fields[1])
            line = f.readline()

    return tags

# watch this one
# @st.cache(suppress_st_warning=True)
def gen_wordcloud():

    tags = load_tags(tagfname)
    cloud = WordCloud().generate_from_frequencies(tags)

    fig, ax = plt.subplots()
    ax.imshow(cloud)
    ax.axis('off')
    fig.show()
    st.pyplot(fig)


def play_video(videoid, objects=None):

    if videoid:
        video_byte = open(f'{videodir}/{videoid}.mp4', 'rb')

        with open(f'{videodir}/{videoid}.info.json') as f:
            metadata = json.load(f)

            st.subheader(metadata['title'])
            st.write(f'Video ID: {metadata["id"]}')

            st.video(video_byte)

            if objects:
                ctr = st.expander(label="Objects", expanded=True)
                ctr.write(objects)

            st.write(metadata['description'])
            json_pane = st.expander('Metadata')
            json_pane.write(metadata)


# Tokenize with NLTK's punkt tokenizer, stopword and punctuation removal
def tokenize(sent):
    ww = word_tokenize(sent)
    return [w.lower() for w in ww if (not w.lower() in stop_words) and (not w in string.punctuation)]


def get_tfidf_query_similarity(vectorizer, docs_tfidf, query):

    query_tfidf = vectorizer.transform([" ".join(tokenize(query))])
    cosine_sim = cosine_similarity(query_tfidf, docs_tfidf).flatten()

    return cosine_sim


@st.cache_data
def load_stopwords():
    # use English stopwords
    return set(stopwords.words('english'))


if __name__ == '__main__':

    st.set_page_config(layout="wide")
    meta = load_metadata('model/how2-metadata-aug.txt')
    stop_words = load_stopwords()

    st.header("How2ViewIR")

    # Make radio buttons flow horizontally
    st.write('<style>div.row-widget.stRadio > div{flex-direction:row;justify-content: left;} </style>',
             unsafe_allow_html=True)
    model = st.radio("TF-IDF Model:", ("Desc+Title", "YOLOv5 Objects"))

    if model == "Desc+Title":
        tfidf, tfidf_vectorizer = load_desctitle_models()
    else:
        tfidf, tfidf_vectorizer = load_yolov5_models()
        # write expander with class labels as a key
        yolov5_key = st.expander("YOLOv5 Class Labels")
        yolov5_key.write(" ".join(names))

    search_col, video_col = st.columns([2, 1])

    # placeholders so the debug pane doesn't complain.
    vid_id = ''
    tok_query = ''
    top_results = []
    objects = []

    with search_col:

        form = st.form(key='query')
        text_input = form.text_input(label="Enter Query")
        num_results = form.slider(label="Num. Results", value=10, min_value=1, max_value=100)
        submit_button = form.form_submit_button(label='Submit')

        res_table = None

        if text_input != "":
            tok_query = " ".join(tokenize(text_input))
            cosine_sim = get_tfidf_query_similarity(tfidf_vectorizer, tfidf, tok_query)
            top_results = cosine_sim.argsort()[:-(num_results+1):-1] # yes this is weird

            scores = [cosine_sim[r] for r in top_results]

            res_df = meta.iloc[top_results]
            res_df = res_df.drop(['duration', 'likecount', 'dislikecount', 'tags', 'description'], axis=1)
            # res_df['score'] = scores
            res_df.insert(loc=2, column='score', value=scores)

            gb = GridOptionsBuilder.from_dataframe(res_df)
            gb.configure_selection(selection_mode="single", use_checkbox=False)
            go = gb.build()

            res_table = AgGrid(res_df,
                               gridOptions=go,
                               update_mode=GridUpdateMode.SELECTION_CHANGED,
                               allow_unsafe_jscode=True)

            sel = res_table['selected_rows']
            if len(sel) != 0:
                vid_id = sel[0]['id']
                objects = sel[0]['objects']

        dbg = st.expander(label="Debug")

        if tok_query:
            dbg.write(f'Query: {tok_query}')
        if len(top_results) > 0:
            dbg.write(f'Results: {top_results}')
        dbg.write(f'tdidf: {tfidf.shape}')
        dbg.write(f'meta:  {meta.shape}')

    with video_col:
        # if model == "Desc+Title":
        #    play_video(vid_id)
        # else:
        # Always display objects
        play_video(vid_id, objects)
