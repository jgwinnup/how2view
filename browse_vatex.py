import pandas as pd
import streamlit as st
import json
from st_aggrid import AgGrid, GridUpdateMode, GridOptionsBuilder

vatex_base = "/tmpssd/data/vatex"

metadata_file = f'{vatex_base}/json/vatex_training_v1.0.json'


@st.cache_data
def load_captions(fname):
    j = json.load(open(fname, 'r'))
    return j


if __name__ == '__main__':

    st.set_page_config(layout="wide")

    meta = load_captions(metadata_file)

    idx = st.number_input("Index:", min_value=0, max_value=len(meta))

    # this will fail if there is an underscore in a vatex video id
    # vid_id, start_time, stop_time = meta[idx]['videoID'].split('_')
    # youtube video ids are 11 chars
    vid_id = meta[idx]['videoID'][:11]

    # st.write(f'video_id: {vid_id}')

    st.write(f'meta: {meta[idx]}')

    vid_file = f'{vatex_base}/dataset/train.ids.vids/train.ids.{vid_id}.mp4'
    img_file = f'{vatex_base}/dataset/train.ids.vids/train.ids.{vid_id}.jpg'

    # st.write(f'vid_file: {vid_file}')
    st.write(f'img_file: {img_file}')

    st.image(img_file)

    exp = st.expander('Video')

    with exp:
        st.video(vid_file)