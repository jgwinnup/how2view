import streamlit as st
import pandas as pd
import json
import glob
from os.path import splitext, basename

datadir = '/tmpssd2/how2-dataset/how2/how2'


@st.cache
def get_videos(dirname):
    fnames = glob.glob(f'{datadir}/*.mp4')
    basenames = [splitext(basename(f))[0] for f in fnames]

    df = pd.DataFrame(basenames)

    return df


def play_video():
    # video_selectbox = "dBhMHFKXpJo" # st.sidebar.selectbox("Videos",get_videos(datadir))
    video_selectbox = st.sidebar.selectbox("Videos", get_videos(datadir))

    # st.sidebar.write(get_videos(datadir))
    # video_df = get_videos(datadir)
    # st.sidebar.table(video_df)

    video_byte = open(f'{datadir}/{video_selectbox}.mp4', 'rb')

    with open(f'{datadir}/{video_selectbox}.info.json') as f:
        metadata = json.load(f)

    st.title(metadata['title'])
    st.write(f'Video ID: {metadata["id"]}')

    st.video(video_byte)

    json_pane = st.beta_expander('Metadata')
    json_pane.write(metadata)

    # st_player(f'file://{datadir}/{test1}')


if __name__ == '__main__':
    play_video()
