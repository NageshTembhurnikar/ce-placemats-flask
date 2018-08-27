import logging
from collections import OrderedDict
from collections import defaultdict
from collections import Counter
from itertools import chain
import itertools
from app.placemats.data.ncbi_client import *
from app.placemats.data.ce_terms import CE_TERMS

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
        for key, value in CE_TERMS.items():
            if key == each_keyword:
                ce_concept = value
                keyword_ce_dict[ce_concept].add(each_keyword)

    # Use an ordered dictionary to sort the data by length of the values for each key
    keyword_ce_dict_sorted = OrderedDict(sorted(keyword_ce_dict.items(), key=lambda item: len(item[1]), reverse=True))

    # Generate the data structure to output
    axis_depth1 = []
    # Select only first 5 key,values to assemble to the collapsible data
    x = itertools.islice(keyword_ce_dict_sorted.items(), 0, 5)
    for k, v in x:
        axis_depth2 = []
        for each_v in v:
            axis_depth2.append({'name': each_v, 'size': key_counter[each_v]})
        axis_depth1.append({'name': k, 'children': axis_depth2})

    return([{'name': term, 'children': axis_depth1}])


