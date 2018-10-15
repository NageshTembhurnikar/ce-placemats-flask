import logging
from collections import OrderedDict
from collections import defaultdict
from collections import Counter
from itertools import chain
import itertools
from app.placemats.data.ncbi_client import *
from app.placemats.data.ce_terms import ce_terms
from app.placemats.data.mesh_summaries import mesh_summaries


logger = logging.getLogger(__name__)


def radial_tree(pmids_to_keywords: dict, term):

    term = term
    cutoff7 = 100
    keyword_ce_dict = defaultdict(set)

    all_keywords = list(chain.from_iterable(pmids_to_keywords.values()))
    word_count = Counter(all_keywords)

    # A dictionary of keywords and their counts
    key_counter = dict(word_count)

    # Select Top N keywords from all keywords
    most_occur = word_count.most_common(cutoff7)
    top_keywords = [var[1][0] for var in enumerate(most_occur)]

    for each_keyword in top_keywords:
        for key, value in ce_terms.items():
            if key == each_keyword:
                ce_concept = value
                keyword_ce_dict[ce_concept].add(each_keyword)

    # Use an ordered dictionary to sort the data by length of the values for each key
    keyword_ce_dict_sorted = OrderedDict(sorted(keyword_ce_dict.items(), key=lambda item: len(item[1]), reverse=True))

    # Generate the data structure to output
    axis_depth1 = []
    # Select 7 elements as the value for inner branch
    branch2_value = 28
    # Select only first 5 key,values to assemble to the collapsible data
    x = itertools.islice(keyword_ce_dict_sorted.items(), 0, 5)
    for k, v in x:
        axis_depth2 = []

        for each_v in v:
            info_data = ''
            if each_v in mesh_summaries:
                info_data = mesh_summaries[each_v]
            axis_depth2.append({'name': each_v, 'size': key_counter[each_v], 'info': info_data})
        axis_depth2_sorted = sorted(axis_depth2, key=lambda user: user['size'], reverse=True)
        branch2 = len(axis_depth2_sorted)
        if branch2 > branch2_value:
            branch2 = branch2_value
        axis_depth1.append({'name': k, 'children': axis_depth2_sorted[:branch2]})

    return({'name': term, 'children': axis_depth1})


