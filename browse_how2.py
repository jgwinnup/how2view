import json
import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridUpdateMode, GridOptionsBuilder

how2_base = "/tmpssd2/how2-dataset"

metadata_file = f"{how2_base}/diffaug/train.en"

@st.cache_data
def load_captions(fname):
    with open(fname, 'r') as infile:
        j = [line.rstrip() for line in infile]
    return j


if __name__ == '__main__':

    st.set_page_config(layout="wide")

    sents = load_captions(metadata_file)

    idx = st.number_input("Index:", min_value=1, max_value=len(sents))

    # try writing a sample
    # s = sents['images'][idx]
    # c = sents['annotations'][idx]

    # st.write(f'meta: {s}')
    st.write(f'seg: {sents[idx-1]}') # watch the off by one

    # construct image id
    # i = int(c['image_id'])
    # img_id = f''

    # st.write(f'image_id: {img_id}')
    st.image(f'{how2_base}/diffaug/clip-train.en/{idx}.jpg')

