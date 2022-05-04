
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import sacrebleu as sb
import spacy
import spacy_streamlit
from spacy_streamlit import visualize_tokens
import pickle

from st_aggrid import AgGrid, GridUpdateMode, GridOptionsBuilder

# Let's analyze what's going on with our systems

# Local config

how2='/tmpssd2/how2-dataset'    # base dir
data=f'{how2}/data/yolov5-all'  # data dir

src_file=f'{data}/base/dev5.en'
ref_file=f'{data}/base/dev5.pt'

hyp1_file=f'{how2}/outputs/yolov5-augmented/marian-trans.how2-yolovocab.n250.en-pt.spm.dev5.out'
hyp2_file=f'{how2}/outputs/yolov5-augmented/marian-trans.how2-yolov5-fixspm.n250.en-pt.spm.dev5.out'

@st.cache
# Cache to avoid reloads
def get_test_sents(_src_file, _ref_file):
    src_sents = []
    ref_sents = []

    with open(_src_file, 'r') as src:
        for line in src:
            src_sents.append(line.strip())

    with open(_ref_file, 'r') as ref:
        for line in ref:
            ref_sents.append(line.strip())

    return src_sents, ref_sents

@st.cache
def get_hyp_sents():
    hyp1_sents = []
    hyp2_sents = []

    with open(hyp1_file, 'r') as hyp1:
        for line in hyp1:
            hyp1_sents.append(line.strip())

    with open(hyp2_file, 'r') as hyp2:
        for line in hyp2:
            hyp2_sents.append(line.strip())

    return hyp1_sents, hyp2_sents

# @st.cache
# def get_spacy_model():
#    return spacy.load('pt_core_news_md')


if __name__ == '__main__':

    # This needs to be first
    st.set_page_config(layout="wide")

    # get spacy model
    nlp = spacy.load('pt_core_news_md') # get_spacy_model()

    # get (static) test src and refs
    src_sents, ref_sents = get_test_sents(src_file, ref_file)
    # get (hardwired) hypotheses
    hyp1_sents, hyp2_sents = get_hyp_sents()

    sents_df = pd.DataFrame(enumerate(src_sents), columns=['Id', 'Source'])

    st.header("Let's Compare")

    # Test set sentences
    gb = GridOptionsBuilder.from_dataframe(sents_df)
    gb.configure_selection(selection_mode="single", use_checkbox=False)
    go = gb.build()

    res_table = AgGrid(sents_df,
                       gridOptions=go,
                       update_mode=GridUpdateMode.SELECTION_CHANGED,
                       allow_unsafe_jscode=True)

    sel = res_table['selected_rows']

    if len(sel) != 0:
        # st.write(f'Sel is: {sel}')
        id = sel[0]['Id']  # index col of src sents
        # st.write(f'src: {lrp_base[id]}')

        src_sent = src_sents[id]
        ref_sent = ref_sents[id]

        hyp1_sent = hyp1_sents[id]
        hyp2_sent = hyp2_sents[id]

        hyp1_doc = nlp(hyp1_sent)
        hyp2_doc = nlp(hyp2_sent)

        # calculate sentence BLEU for hyps
        hyp1_bleu = sb.sentence_bleu(hyp1_sent, [ref_sent]).score
        hyp2_bleu = sb.sentence_bleu(hyp2_sent, [ref_sent]).score

        # create data array for table
        table_labels = ['System', 'BLEU', 'Sentence']
        table_data = [ ['Source', ' ', src_sent ],
                       ['Ref', ' ', ref_sent],
                       ['Hyp1', f'{hyp1_bleu:0.2f}', hyp1_sent],
                       ['Hyp2', f'{hyp2_bleu:0.2f}', hyp2_sent]]

        st.table(pd.DataFrame(table_data, columns=table_labels))

        # try spacy viz
        visualizers = ["ner", "textcat"]
        spacy_streamlit.visualize(['pt_core_news_md'], hyp1_sent, visualizers)
        # visualize_tokens(hyp1_doc, attrs=["text", "pos_", "dep_"])

