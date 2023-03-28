import json
import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridUpdateMode, GridOptionsBuilder

coco_base = "/extra2/data/mscoco"

metadata_file = f"{coco_base}/annotations/captions_train2014.json"

@st.cache_data
def load_captions(fname):
    j = json.load(open(fname, 'r'))
    return j


if __name__ == '__main__':

    st.set_page_config(layout="wide")

    meta = load_captions(metadata_file)

    idx = st.number_input("Index:", min_value=0, max_value=len(meta['annotations']))

    # try writing a sample
    s = meta['images'][idx]
    c = meta['annotations'][idx]

    #st.write(f'meta: {s}')
    st.write(f'annotation: {c}')

    # construct image id
    i = int(c['image_id'])
    img_id = f'COCO_train2014_{i:012d}.jpg'

    # st.write(f'image_id: {img_id}')
    st.image(f'{coco_base}/train2014/{img_id}')

