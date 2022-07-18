
import numpy as np
import matplotlib.pyplot as plt
from matplotlib_venn import venn3

from matplotlib_venn_wordcloud import venn3_wordcloud

# Plot venn diagram of overlapping labels

naive_drop3 = ['PERSON', 'CUP', 'BOTTLE']

idf_40 = ['PERSON', 'BOTTLE', 'CUP', 'BOWL', 'CHAIR', 'POTTED_PLANT', 'REMOTE',
    'CELL_PHONE', 'TOASTER', 'HAIR_DRIER']

norm_tfidf_020 = ['BICYCLE', 'CAR', 'MOTORCYCLE', 'AIRPLANE', 'BUS', 'TRAIN', 'TRUCK', 'BOAT', 'TRAFFIC_LIGHT',
    'FIRE_HYDRANT', 'STOP_SIGN', 'PARKING_METER', 'BENCH', 'BIRD', 'CAT', 'DOG', 'HORSE', 'SHEEP', 'COW',
    'ELEPHANT', 'BEAR', 'ZEBRA', 'GIRAFFE', 'BACKPACK', 'UMBRELLA', 'HANDBAG', 'TIE', 'SUITCASE', 'FRISBEE',
    'SKIS', 'SNOWBOARD', 'SPORTS_BALL', 'KITE', 'BASEBALL_BAT', 'BASEBALL_GLOVE', 'SKATEBOARD', 'SURFBOARD',
    'TENNIS_RACKET', 'WINE_GLASS', 'FORK','KNIFE', 'SPOON', 'BANANA', 'APPLE', 'SANDWICH', 'ORANGE',
    'BROCCOLI', 'CARROT', 'HOT_DOG', 'PIZZA', 'DONUT', 'CAKE', 'COUCH', 'BED', 'DINING_TABLE', 'TOILET',
    'LAPTOP', 'MOUSE', 'REMOTE', 'KEYBOARD', 'CELL_PHONE', 'MICROWAVE', 'OVEN', 'TOASTER', 'SINK', 'REFRIGERATOR',
    'CLOCK', 'SCISSORS', 'TEDDY_BEAR', 'HAIR_DRIER', 'TOOTHBRUSH']


#  venn3_wordcloud([set(HH), set(Wnt), set(CC)],
#                     set_labels=['Hedgehog', 'Wnt', 'Cell Cycle'])

# wordcloud_kwargs=dict(max_font_size=1000, min_font_size=0)
foo = venn3_wordcloud([set(naive_drop3), set(idf_40), set(norm_tfidf_020)], set_labels=['naive', 'idf', 'norm_tfidf'])

#foo = venn3([set(naive_drop3), set(idf_40), set(norm_tfidf_020)], ['naive', 'idf', 'norm_tfidf'])

plt.show()