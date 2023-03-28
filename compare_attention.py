from os.path import basename
import glob
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridUpdateMode, GridOptionsBuilder
import sacrebleu as sb

how2='/tmpssd2/how2-dataset'    # base dir
data=f'{how2}/data/yolov5-all'  # data dir

src_file=f'{data}/base/dev5.en'
ref_file=f'{data}/base/dev5.pt'
hypdir=f'{how2}/outputs/attention'

# this will have to be on a per-decode basis...
src_base_spm=f'{data}/how2-yolovocab-base.en-pt.spm/test.spm.en'
src_yolo_spm=f'{data}/how2-yolov5-fixspm.en-pt.spm/test.spm.en'

# Hardwired for paper deadline brevity
hyp_refs = {
    'marian-trans-yolov5-fixspm.drop1.n250': f'{data}/how2-yolov5-fixspm.en-pt.spm/test.drop-1.spm.en',
    'marian-trans-yolov5-fixspm.drop2.n250': f'{data}/how2-yolov5-fixspm.en-pt.spm/test.drop-2.spm.en',
    'marian-trans-yolov5-fixspm.drop3.n250': f'{data}/how2-yolov5-fixspm.en-pt.spm/test.drop-2.spm.en',
    'marian-trans-yolov5-fixspm.drop4.n250': f'{data}/how2-yolov5-fixspm.en-pt.spm/test.drop-4.spm.en', # missing
    'marian-trans-yolov5-fixspm.drop5.n250': f'{data}/how2-yolov5-fixspm.en-pt.spm/test.drop-5.spm.en', # missing
    'marian-trans-yolov5-fixspm.idf-3.0.n250': f'{data}/how2-yolov5-fixspm.en-pt.spm/test.idf-3.0.spm.en',
    'marian-trans-yolov5-fixspm.idf4.0.n250': f'{data}/how2-yolov5-fixspm.en-pt.spm/test.idf-4.0.spm.en',
    'marian-trans-yolov5-fixspm.idf-5.0.n250': f'{data}/how2-yolov5-fixspm.en-pt.spm/test.idf-5.0.spm.en',
    'marian-trans-yolov5-fixspm.n150': f'{data}/how2-yolov5-fixspm.en-pt.spm/test.spm.en',
    'marian-trans-yolov5-fixspm.n250': f'{data}/how2-yolov5-fixspm.en-pt.spm/test.spm.en',
    'marian-trans-yolov5-fixspm.norm_tfidf-0.10': f'{data}/how2-yolov5-fixspm.en-pt.spm/test.norm_tfidf-0.10.spm.en',
    'marian-trans-yolov5-fixspm.norm_tfidf0.20': f'{data}/how2-yolov5-fixspm.en-pt.spm/test.norm_tfidf-0.20.spm.en',
    'marian-trans-yolov5-fixspm.norm_tfidf-0.30': f'{data}/how2-yolov5-fixspm.en-pt.spm/test.norm_tfidf-0.30.spm.en',
    'marian-trans-yolov5-fixspm.samp140327.n250': f'{data}/how2-yolov5-fixspm.en-pt.spm/test.spm.en',
    'marian-trans-yolovocab-base.n150': f'{data}/how2-yolovocab-base.en-pt.spm/test.spm.en',
    'marian-trans-yolovocab-base.n250': f'{data}/how2-yolovocab-base.en-pt.spm/test.spm.en',
}


@st.cache_data
def get_src_lines():
    with open(src_file, 'r') as f:
        lines = [line.rstrip() for line in f]
    return lines


@st.cache_data
def get_ref_lines():
    with open(ref_file, 'r') as f:
        lines = [line.rstrip() for line in f]
    return lines


@st.cache_data
def get_file_lines(fname):
    with open(fname, 'r') as f:
        lines = [line.rstrip() for line in f]
    return lines


@st.cache_data
def get_hyp_lines(shortname):

    fname = f'{hypdir}/{shortname}.en-pt.spm.dev5.softalign'
    hyp_lines = []
    hyp_aligns = []

    with open(fname, 'r') as hypfile:
        for line in hypfile:
            fields = line.strip().split(' ||| ')
            hyp_lines.append(fields[0])
            hyp_aligns.append(fields[1])

    return hyp_lines, hyp_aligns


@st.cache_data
def get_hyp_files():
    fnames = [basename(x).replace('.en-pt.spm.dev5.align', '') for x in glob.glob(f'{hypdir}/*.align')]
    fnames.sort()
    return fnames


@st.cache_data
def get_corpus_bleu(hyp):
    # remember to despm
    hyp_detok = [despm(h) for h in hyp]
    return sb.corpus_bleu(hyp_detok, [ref_lines])


def despm(sent):
    return sent.replace(" ", "").replace("▁", " ")


def score_hyp(hyp):

    scores = []
    for h, r in zip(hyp, ref_lines): # yeah global
        h_detok = despm(h)
        score = sb.sentence_bleu(h_detok, [r]).score
        scores.append(score)
    return scores


@st.cache_data
def get_results_dataframe(hyp_a, hyp_b):

    sys_a_scores = score_hyp(hyp_a)
    sys_b_scores = score_hyp(hyp_b)

    res_df = pd.DataFrame(src_lines, columns=['Src'])
    res_df.insert(0, 'Line', range(1, len(hyp_a) + 1))
    res_df.insert(1, 'Sys A', sys_a_scores, True)
    res_df.insert(2, 'Sys B', sys_b_scores, True)

    return res_df


def build_align_grid(src_toks, hyp_toks, aligns):

    src_n = len(src_toks)
    hyp_n = len(hyp_toks)

    grid = np.zeros([src_n, hyp_n])

    for i, a in enumerate(aligns):
        weights = a.split(',')

        for j, w in enumerate(weights):
           grid[j,i] = float(w)

    return grid


def gen_plot(data, src_toks, hyp_toks):
    nx, ny = data.shape
    fig, ax = plt.subplots()
    ax.tick_params(axis='both', which='major', labelsize=fontsize)
    plt.yticks(np.arange(0.0, nx, 1.0))
    ax.set_yticklabels(src_toks) #, prop={"size":16})
    plt.xticks(rotation=90)
    plt.xticks(np.arange(0.0, ny, 1.0))
    ax.set_xticklabels(hyp_toks) #, prop={"size":16})
    ax.imshow(data, cmap='plasma', interpolation='nearest')
    # ax.imshow(data, cmap='gray_r', interpolation='none')

    return fig


if __name__ == '__main__':

    # This needs to be first
    st.set_page_config(layout="wide")

    # horizontal radio buttons
    st.write('<style>div.row-widget.stRadio > div{flex-direction:row;justify-content: left;} </style>',
             unsafe_allow_html=True)

    # have them available globally
    src_lines = get_src_lines()
    ref_lines = get_ref_lines()

    # duct tape
    # move this below dropdown selections once we have the hyp/src table built
    # src_base_lines = get_file_lines(src_base_spm)
    # src_yolo_lines = get_file_lines(src_yolo_spm)

    ccol1, ccol2, ccol3 = st.columns([0.3, 0.5, 0.2])
    with ccol1:
        fontsize = st.selectbox('Font:', [8, 10, 12, 14, 16, 18, 20], index=3)
    with ccol2:
        plot_layout = st.radio("Plot:", ("Horizontal", "Stacked"))

    col1, col2 = st.columns([0.5, 0.5])

    #hyplist = get_hyp_files()
    hyplist = hyp_refs.keys()

    with col1:
        sys_a = st.selectbox('Sys A:', hyplist, index=15)
        sys_a_hyp, sys_a_align = get_hyp_lines(sys_a)
        sys_a_src = get_file_lines(hyp_refs[sys_a])
        st.write(f'Corpus BLEU: {get_corpus_bleu(sys_a_hyp)}')

    with col2:
        sys_b = st.selectbox('Sys B:', hyplist, index=9)
        sys_b_hyp, sys_b_align = get_hyp_lines(sys_b)
        sys_b_src = get_file_lines(hyp_refs[sys_b])
        st.write(f'Corpus BLEU: {get_corpus_bleu(sys_b_hyp)}')



    df = get_results_dataframe(sys_a_hyp, sys_b_hyp)
    # df.reset_index() # make line numbers reappear
    #st.dataframe(df)
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_selection(selection_mode="single", use_checkbox=False)
    gb.configure_column('Sys A', type=['numericColumn', 'numberColumnFilter', 'customNumericFormat'], precision = 2)
    gb.configure_column('Sys B', type=['numericColumn', 'numberColumnFilter', 'customNumericFormat'], precision = 2)
    go = gb.build()

    res_table = AgGrid(df,
                       gridOptions=go,
                       update_mode=GridUpdateMode.SELECTION_CHANGED,
                       allow_unsafe_jscode=True)

    # If a line is selected, built the two alignment grids
    sel = res_table['selected_rows']
    if len(sel) != 0:
        # st.write(f'Selected: {sel[0]}')
        sel_idx = sel[0]['Line'] - 1  # adjust for 0-index lists

        sel_src = src_lines[sel_idx]

        # sys_a_src_toks = src_base_lines[sel_idx].split(' ')
        sys_a_src_toks = sys_a_src[sel_idx].split(' ')
        sys_a_src_toks.append('</s>') # add EOS token...
        # sys_a_src_toks.append('PAD')
        sys_a_hyp_toks = sys_a_hyp[sel_idx].split(' ')
        sys_a_hyp_aligns = sys_a_align[sel_idx].split(' ')

        # sys_b_src_toks = src_yolo_lines[sel_idx].split(' ')
        sys_b_src_toks = sys_b_src[sel_idx].split(' ')
        sys_b_src_toks.append('</s>') # add EOS token...
        # sys_b_src_toks.append('PAD')
        sys_b_hyp_toks = sys_b_hyp[sel_idx].split(' ')
        sys_b_hyp_aligns = sys_b_align[sel_idx].split(' ')

        sys_a_grid = build_align_grid(sys_a_src_toks, sys_a_hyp_toks, sys_a_hyp_aligns)
        sys_b_grid = build_align_grid(sys_b_src_toks, sys_b_hyp_toks, sys_b_hyp_aligns)

        
        if plot_layout == 'Stacked':
            sys_a_fig = gen_plot(sys_a_grid, sys_a_src_toks, sys_a_hyp_toks)
            st.pyplot(sys_a_fig)

            sys_b_fig = gen_plot(sys_b_grid, sys_b_src_toks, sys_b_hyp_toks)
            st.pyplot(sys_b_fig)

        else:
            col3, col4 = st.columns([0.5, 0.5])
            with col3:
                st.subheader(f'{sys_a}: {sel[0]["Line"]}')
                sys_a_fig = gen_plot(sys_a_grid, sys_a_src_toks, sys_a_hyp_toks)
                st.pyplot(sys_a_fig)

            with col4:
                st.subheader(f'{sys_b}: {sel[0]["Line"]}')
                sys_b_fig = gen_plot(sys_b_grid, sys_b_src_toks, sys_b_hyp_toks)
                st.pyplot(sys_b_fig)

        # Debugging info
        with st.expander('Debug') :
            st.write(f'Src: {sel_src}')
            st.write(f'Sys A src toks: ({len(sys_a_src_toks)}) {sys_a_src_toks}')
            st.write(f'Sys A hyp toks: ({len(sys_a_hyp_toks)}) {sys_a_hyp_toks}')
            st.write(f'Sys A hyp aligns: ({len(sys_a_hyp_aligns)}) {sys_a_hyp_aligns}')

            # st.table(data=sys_a_grid)

            st.write(f'Sys B src toks: ({len(sys_b_src_toks)}) {sys_b_src_toks}')
            st.write(f'Sys B hyp toks: ({len(sys_b_hyp_toks)}) {sys_b_hyp_toks}')
            st.write(f'Sys B hyp aligns: ({len(sys_b_hyp_aligns)}) {sys_b_hyp_aligns}')
            # st.table(data=sys_b_grid)

        # For alignment matrix debugging
        # sys_a_grid = build_align_grid(sys_a_src_toks, sys_a_hyp_toks, sys_a_hyp_aligns)
        # sys_b_grid = build_align_grid(sys_b_src_toks, sys_b_hyp_toks, sys_b_hyp_aligns)
        # st.table(data=sys_a_grid)
        # st.table(data=sys_b_grid)